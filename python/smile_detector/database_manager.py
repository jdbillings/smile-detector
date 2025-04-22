import os
import json
import sqlite3
import time
import traceback

from smile_detector.app_config import config, logger
logger.debug(f"PID={config.pid};loading database manager")


class DatabaseManager:
    DB_PATH: str = config.database_path
    DB_BASEDIR: str = os.path.dirname(DB_PATH)

    @staticmethod
    def initialize_database() -> None:
        """Initialize the SQLite database."""
        logger.info(f"PID={config.pid};Initializing database at {DatabaseManager.DB_PATH}")

        os.makedirs(DatabaseManager.DB_BASEDIR, exist_ok=True)

        try:
            with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS frames (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        frame BLOB,
                        coords TEXT,
                        has_smile BOOLEAN DEFAULT 0,
                        session_id INTEGER,
                        FOREIGN KEY (session_id) REFERENCES sessions (id)
                    );
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        active BOOLEAN
                    );
                """)
                conn.commit()
        except sqlite3.OperationalError as e:
            pass # Ignore errors in creating tables
        except Exception as e:
            logger.warning(f"PID={config.pid};Error initializing database: {traceback.format_exc()}")
            pass

    @staticmethod
    def create_new_session() -> int | None:
        """Create a new session in the SQLite database."""
        session_id = None

        with sqlite3.connect(DatabaseManager.DB_PATH, autocommit=False) as conn:
            for _retry_ in range(3):
                try:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO sessions (active) VALUES (1); ")
                    session_id = cursor.lastrowid
                    conn.commit()
                except sqlite3.OperationalError as e:
                    conn.rollback()
                    time.sleep(1)

        logger.debug(f"PID={config.pid};created new session with ID {session_id}")
        return session_id


    @staticmethod
    def get_session(session_id: int) -> dict | None:
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            cursor = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            session = cursor.fetchone()
            if session:
                logger.debug(f"PID={config.pid};retrieved session {session_id} from database")
                return {
                    "id": session[0],
                    "timestamp": session[1],
                    "active": session[2]
                }
            else:
                logger.debug(f"PID={config.pid};session {session_id} not found in database")
                return None


    @staticmethod
    def get_active_session(session_id: int) -> dict | None:
        """Get the active session from the SQLite database."""
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            cursor = conn.execute("SELECT * FROM sessions WHERE id = ? AND active = 1", (session_id,))
            session = cursor.fetchone()
            if session:
                logger.debug(f"PID={config.pid};retrieved active session {session_id} from database")
                return {
                    "id": session[0],
                    "timestamp": session[1],
                    "active": session[2]
                }
            else:
                logger.debug(f"PID={config.pid};could not find active session {session_id} in database")
                return None


    @staticmethod
    def get_active_session_count() -> int:
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM sessions WHERE active = 1")
            session_count: int = int(cursor.fetchone()[0])
            logger.debug(f"PID={config.pid};active session count: {session_count}")
            return session_count


    @staticmethod
    def write_frame_to_db(frame: bytes, session_id: int, coords: list[dict]) -> bool:
        """Write a frame to the SQLite database."""
        has_smile = len(coords) > 0
        json_coords = json.dumps(coords)
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            conn.execute("INSERT INTO frames (frame, session_id, coords, has_smile) VALUES (?, ?, ?, ?)", (frame, session_id, json_coords, has_smile))
            conn.commit()
        logger.debug(f"PID={config.pid};wrote frame to database for session {session_id}")
        return True


    @staticmethod
    def deactivate_session(session_id: int) -> bool:
        """Deactivate a session in the SQLite database."""
        with sqlite3.connect(DatabaseManager.DB_PATH, autocommit=False) as conn:
            for i in range(4):
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE sessions SET active = 0 WHERE id = ?", (session_id,))
                    conn.commit()
                    break
                except sqlite3.OperationalError as e:
                    conn.rollback()
                    if i >= 2:
                        raise e
                    time.sleep(1)
            logger.info(f"PID={config.pid};deactivated session {session_id} in database")
        return True


    @staticmethod
    def get_latest_coords(session_id: int) -> dict:
        """Get the latest coordinates for a session."""
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor = conn.execute(
                "SELECT coords FROM frames WHERE session_id = ? AND has_smile = 1 ORDER BY TIMESTAMP DESC LIMIT 1",
                (session_id,)
            )
            result = cursor.fetchone()
            if result and result[0]:
                logger.debug(f"PID={config.pid};retrieved latest coordinates for session {session_id}, json_str={result[0]}")
                return json.loads(result[0])
            else:
                logger.debug(f"PID={config.pid};no coordinates found for session {session_id}")
                return {}

    @staticmethod
    def export_smiles(output_path: str):
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, frame, coords, session_id FROM frames WHERE has_smile = 1")

            def generate_rows():
                while True:
                    row = cursor.fetchone()
                    if row is None or len(row) == 0:
                        break
                    yield row

            for row in generate_rows():
                frame_id = row[0]
                timestamp = row[1]
                frame = row[2]
                coords = json.loads(row[3])
                session_id = row[4]

                session_dir = os.path.join(output_path, str(session_id))
                frame_dir = os.path.join(session_dir, str(frame_id))
                frame_fname = os.path.join(frame_dir, f"{frame_id}.jpg")
                metadata_fname = os.path.join(frame_dir, f"{frame_id}.json")

                os.makedirs(frame_dir, exist_ok=True)
                with open(metadata_fname, "w") as f1:
                    json.dump({
                        "timestamp": timestamp,
                        "coords": coords,
                        "session_id": session_id
                    }, f1)

                with open(frame_fname, "wb") as f2:
                    f2.write(frame)

                logger.debug(f"PID={config.pid};exported frame {frame_id} for session {session_id} to {frame_fname}")

        logger.info(f"PID={config.pid};exported smiles to {output_path}")
        return True

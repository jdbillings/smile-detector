import os
import json
import sqlite3
import time
from smile_detector.filesystem_lock import FSLock

from smile_detector.app_config import config, logger
logger.debug(f"PID={config.pid};loading database manager")


class DatabaseManager:
    DB_PATH = config.database_path
    DB_BASEDIR = os.path.dirname(DB_PATH)
    LOCKFILE = os.path.join(DB_BASEDIR, "LOCK")

    @staticmethod
    def initialize_database():
        """Initialize the SQLite database to store frames and the semaphore."""

        logger.info(f"PID={config.pid};Initializing database at {DatabaseManager.DB_PATH}")
        if not os.path.exists(DatabaseManager.DB_PATH):
            os.makedirs(DatabaseManager.DB_BASEDIR, exist_ok=True)
            lock = FSLock(DatabaseManager.LOCKFILE)
            if lock.acquire() is False:
                logger.debug(f"PID={config.pid};failed to acquire lock for database initialization")
                time.sleep(5)
                return
            logger.info(f"PID={config.pid};acquired lock for database initialization")

            try:
                with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
                    # Create a table for storing frames
                    conn.execute("""
                        CREATE TABLE frames (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            frame BLOB,
                            coords TEXT,
                            has_smile BOOLEAN DEFAULT 0,
                            session_id INTEGER,
                            FOREIGN KEY (session_id) REFERENCES sessions (id)
                        )
                    """)
                    conn.execute("""
                        CREATE TABLE sessions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            active BOOLEAN
                        )
                    """)
                    conn.commit()
            finally:
                lock.release()
                logger.info(f"PID={config.pid};released lock for database initialization")


    @staticmethod
    def create_new_session() -> int | None:
        """Create a new session in the SQLite database."""
        session_id = None
        while True:
            lock = FSLock(DatabaseManager.LOCKFILE)
            if lock.acquire() is False:
                logger.debug(f"PID={config.pid};couldn't acquire lock for creating new session, sleep and retry")
                time.sleep(1)
                continue
            logger.info(f"PID={config.pid};acquired lock for creating new session")

            try:
                with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
                    cursor = conn.execute("INSERT INTO sessions (active) VALUES (1)")
                    session_id = cursor.lastrowid
                    conn.commit()
            finally:
                lock.release()
                logger.info(f"PID={config.pid};released lock for creating new session")
            break
        logger.debug(f"PID={config.pid};created new session with ID {session_id}")
        return session_id


    @staticmethod
    def get_session(session_id: int):
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
    def get_active_session(session_id: int):
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
    def get_active_session_count():
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM sessions WHERE active = 1")
            session_count = cursor.fetchone()[0]
            logger.debug(f"PID={config.pid};active session count: {session_count}")
            return session_count


    @staticmethod
    def write_frame_to_db(frame: bytes, session_id: int, coords: list[dict]):
        """Write a frame to the SQLite database."""
        has_smile = len(coords) > 0
        json_coords = json.dumps(coords)
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            conn.execute("INSERT INTO frames (frame, session_id, coords, has_smile) VALUES (?, ?, ?, ?)", (frame, session_id, json_coords, has_smile))
            conn.commit()
        logger.debug(f"PID={config.pid};wrote frame to database for session {session_id}")
        return True


    @staticmethod
    def deactivate_session(session_id: int):
        """Deactivate a session in the SQLite database."""
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            conn.execute("UPDATE sessions SET active = 0 WHERE id = ?", (session_id,))
            conn.commit()
            logger.info(f"PID={config.pid};deactivated session {session_id} in database")
        return True

    @staticmethod
    def get_latest_coords(session_id: int) -> dict:
        """Get the latest coordinates for a session."""
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            cursor = conn.execute(
                "SELECT coords FROM frames WHERE session_id = ? ORDER BY id DESC LIMIT 1",
                (session_id,)
            )
            result = cursor.fetchone()
            if result and result[0]:
                logger.debug(f"PID={config.pid};retrieved latest coordinates for session {session_id}")
                return json.loads(result[0])
            else:
                logger.debug(f"PID={config.pid};no coordinates found for session {session_id}")
                return {}

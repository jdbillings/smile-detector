import os
import json
import sqlite3
import time
from filesystem_lock import FSLock

with open(f"{os.path.dirname(__file__)}/conf/config.json", "r") as config_file:
    _DB_PATH = json.load(config_file)["sqlite"]["db_path"]

class DatabaseManager:
    DB_PATH = _DB_PATH
    DB_BASEDIR = os.path.dirname(DB_PATH)
    LOCKFILE = os.path.join(DB_BASEDIR, "LOCK")

    @staticmethod
    def initialize_database():
        """Initialize the SQLite database to store frames and the semaphore."""

        if not os.path.exists(DatabaseManager.DB_PATH):
            os.makedirs(DatabaseManager.DB_BASEDIR, exist_ok=True)
            lock = FSLock(DatabaseManager.LOCKFILE)
            if lock.acquire() is False:
                time.sleep(5)
                return

            try:
                with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
                    # Create a table for storing frames
                    conn.execute("""
                        CREATE TABLE frames (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            frame BLOB,
                            session_id INTEGER,
                            coords TEXT
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


    @staticmethod
    def create_new_session() -> int | None:
        """Create a new session in the SQLite database."""
        session_id = None
        while True:
            time.sleep(1)
            lock = FSLock(DatabaseManager.LOCKFILE)
            if lock.acquire() is True:
                try:
                    with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
                        cursor = conn.execute("INSERT INTO sessions (active) VALUES (1)")
                        session_id = cursor.lastrowid
                        conn.commit()
                finally:
                    lock.release()
                    break
        return session_id


    @staticmethod
    def get_session(session_id: int):
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            cursor = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            session = cursor.fetchone()
            if session:
                return {
                    "id": session[0],
                    "timestamp": session[1],
                    "active": session[2]
                }
            return None

    @staticmethod
    def get_active_session(session_id: int):
        """Get the active session from the SQLite database."""
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            cursor = conn.execute("SELECT * FROM sessions WHERE id = ? AND active = 1", (session_id,))
            session = cursor.fetchone()
            if session:
                return {
                    "id": session[0],
                    "timestamp": session[1],
                    "active": session[2]
                }
            return None


    @staticmethod
    def get_active_session_count():
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM sessions WHERE active = 1")
            session_count = cursor.fetchone()[0]
            return session_count


    @staticmethod
    def write_frame_to_db(frame: bytes, session_id: int, coords: list[dict]):
        """Write a frame to the SQLite database."""

        json_coords = json.dumps(coords)

        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            conn.execute("INSERT INTO frames (frame, session_id, coords) VALUES (?, ?, ?)", (frame, session_id, json_coords))
            conn.commit()


    @staticmethod
    def deactivate_session(session_id: int):
        """Deactivate a session in the SQLite database."""
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            conn.execute("UPDATE sessions SET active = 0 WHERE id = ?", (session_id,))
            conn.commit()

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
                return json.loads(result[0])
            return {}

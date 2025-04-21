import sqlite3
import os

class DatabaseManager:
    DB_PATH = "/tmp/smiledetector/frames.db"
    @staticmethod
    def initialize_database():
        """Initialize the SQLite database to store frames and the semaphore."""
        if not os.path.exists(DatabaseManager.DB_PATH):
            os.makedirs(os.path.dirname(DatabaseManager.DB_PATH), exist_ok=True)
            with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
                # Create a table for storing frames
                conn.execute("""
                    CREATE TABLE frames (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        frame BLOB,
                        session_id INTEGER
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

    @staticmethod
    def create_new_session():
        """Create a new session in the SQLite database."""
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            cursor = conn.execute("INSERT INTO sessions (active) VALUES (1)")
            session_id = cursor.lastrowid
            conn.commit()
            return session_id


    @staticmethod
    def get_active_session_count():
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM sessions WHERE active = 1")
            session_count = cursor.fetchone()[0]
            return session_count


    @staticmethod
    def write_frame_to_db(frame: bytes, session_id: int):
        """Write a frame to the SQLite database."""
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            conn.execute("INSERT INTO frames (frame, session_id) VALUES (?, ?)", (frame, session_id))
            conn.commit()


    @staticmethod
    def deactivate_session(session_id: int):
        """Deactivate a session in the SQLite database."""
        with sqlite3.connect(DatabaseManager.DB_PATH) as conn:
            conn.execute("UPDATE sessions SET active = 0 WHERE id = ?", (session_id,))
            conn.commit()

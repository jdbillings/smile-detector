import cv2
from flask import Flask, Response
import sqlite3
import os
import time
from contextlib import contextmanager
import collections

app = Flask(__name__)

# Database path
DB_PATH = "/tmp/smiledetector/frames.db"

BASE_FPS_PER_REQUEST = 30

class SessionManager:
    """Class to manage sessions and their metadata."""
    def __init__(self):
        self.session_id = None
        self.session_count = -1
        initialize_database()

        # Insert a new session into the sessions table
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("INSERT INTO sessions (active) VALUES (1)")
            self.session_id = cursor.lastrowid
            conn.commit()

            self.update_session_count()
        print(f"Session {self.session_id} started, session count: {self.session_count}")

    def update_session_count(self):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT count(id) FROM sessions WHERE active = 1")
            self.session_count = cursor.fetchone()[0]

    def close(self):
        """Close the session and update the database."""
        if self.session_id is not None:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "UPDATE sessions SET active = 0 WHERE id = ?",
                    (self.session_id,)
                )
                conn.commit()
            print(f"Session {self.session_id} ended.")
            self.session_id = None


    def produce_frames(self):
        """Producer logic that reads frames from the camera and writes to the database."""
        cap = cv2.VideoCapture(0)
        while True:
            success, frame = cap.read()
            if success:
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                write_frame_to_db(frame_bytes, self.session_id)
                yield frame_bytes
                self.update_session_count()
                # Control the frame rate based on the session count
                time.sleep(min(0.8, self.session_count / BASE_FPS_PER_REQUEST))
            else:
                cap.release()
                self.close()
                raise IOError("Failed to read from camera")
            
    def generate_responses(self):
        """Generate responses for the frames."""
        genrtr = self.produce_frames()
        while True:
            try:
                frame = next(genrtr)
            except:
                print("Producer failed, stopping frame generation.")
                self.close()
                raise
            if frame:
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    def __del__(self):
        """Destructor to ensure the session is closed."""
        self.close()


def initialize_database():
    """Initialize the SQLite database to store frames and the semaphore."""
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
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



def write_frame_to_db(frame: bytes, session_id: int):
    """Write a frame to the SQLite database."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO frames (frame, session_id) VALUES (?, ?)", (frame, session_id))
        conn.commit()



    
@app.route('/video_feed')
def video_feed():
    """Flask route to serve the video feed."""
    session = SessionManager()
    # Return the video feed
    r = Response(session.generate_responses(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return r


def debug():
    session = SessionManager()

if __name__ == "__main__":
    debug()
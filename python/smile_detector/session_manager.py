import cv2
import time
import traceback
from typing import Tuple, Self
from cv2.typing import MatLike
from cv2.data import haarcascades as haar_path

from smile_detector.database_manager import DatabaseManager
from smile_detector.app_config import config, logger
logger.debug(f"PID={config.pid};Loading session manager")

DatabaseManager.initialize_database()

class SessionManager:
    """Class to manage sessions and their metadata."""
    BASE_FPS_PER_REQUEST = 30
    # Load Haar cascade for smile detection
    smile_cascade = cv2.CascadeClassifier(haar_path + "haarcascade_smile.xml")

    def __init__(self, session_id: int | None = None):
        self.session_id: int | None = session_id
        if self.session_id is None:
            self.session_id = DatabaseManager.create_new_session()
            logger.info(f"Session {self.session_id} started, session count: {DatabaseManager.get_active_session_count()}")

        assert self.session_id is not None, "Error in creating session in DB"

        session_metadata = DatabaseManager.get_session(self.session_id)

        if session_metadata is None:
            raise ValueError(f"Session {self.session_id} not found in the database.")

        self.timestamp = session_metadata["timestamp"]
        self.active: bool = session_metadata["active"]


    def close(self):
        """Close the session and update the database."""
        if self.session_id is not None:
            DatabaseManager.deactivate_session(self.session_id)
            logger.info(f"Session {self.session_id} ended.")
            self.session_id = None

    def detect_smile(self, frame: MatLike) -> list:
        """Detect a smile in the given frame and return the coordinates of the rectangle."""
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        smiles = self.smile_cascade.detectMultiScale(
            gray_frame,
            scaleFactor=1.5,
            minNeighbors=35,
            minSize=(30, 30)
        )
        if len(smiles) == 0:
            return []
        # only return the largest smile (as proxy for "best smile")
        best_smile = max(smiles, key=lambda s: s[2] * s[3])
        return [best_smile]

    def produce_frames(self: Self):
        """Producer logic that reads frames from the camera and writes to the database."""
        cap: cv2.VideoCapture = cv2.VideoCapture(0)
        while True:
            start = time.time()
            res : Tuple[bool, MatLike | None] = cap.read()
            success: bool = res[0]
            if not success or res[1] is None:
                cap.release()
                self.close()
                raise IOError("Failed to read from camera")
            frame: MatLike = res[1]

            # Detect smiles in the frame
            smiles = self.detect_smile(frame)

            coords = []
            # Draw rectangles around detected smiles
            for (x, y, w, h) in smiles:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                coords.append(
                    {
                        "BL": [int(x),int(y)],
                        "BR": [int(x+w), int(y)],
                        "TL": [int(x), int(y+h)],
                        "TR": [int(x+w), int(y+h)]
                    }
                )
            # Encode the frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # Write the frame to the database
            assert self.session_id is not None, "Error: attempting to produce frames for a closed session"
            DatabaseManager.write_frame_to_db(frame_bytes, self.session_id, coords)

            yield frame_bytes

            # Limit the frame rate to avoid contention on camera when we have concurrent sessions
            time.sleep(max(0.3 - (time.time() - start), 0))

    def get_latest_coords(self, session_id: int) -> dict:
        """Get the latest coordinates for the specified session."""
        if self.session_id is None:
            raise ValueError("Session is closed or not initialized.")

        return DatabaseManager.get_latest_coords(session_id)

    def generate_frame_responses(self):
        """Generate responses for the frames."""
        genrtr = self.produce_frames()
        while True:
            try:
                frame = next(genrtr)
            except Exception as e:
                logger.error(f"PID={config.pid};Producer failed, stopping frame generation;{traceback.format_exc()}")
                self.close()
                raise
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

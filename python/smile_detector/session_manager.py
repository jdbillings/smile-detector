import cv2
import time
import traceback
from typing import Tuple, Iterator
from cv2.typing import MatLike
from cv2.data import haarcascades as haar_path

from smile_detector.app_config import config, logger
logger.debug(f"PID={config.pid};Loading session manager")

from smile_detector.database_manager import DatabaseManager
DatabaseManager.initialize_database()

class SessionManager:
    """Class to manage sessions and their metadata."""
    BASE_FPS_PER_REQUEST = 30
    # Load Haar cascade for smile detection
    SMILE_CLASSIFIER = cv2.CascadeClassifier(haar_path + "haarcascade_smile.xml")
    webcam_idx: int = config.webcam_index

    def __init__(self, session_id: int | None = None):
        self.session_id: int | None = session_id
        self.active: bool = False
        self.timestamp: float | None = None
        self.request_counter: int = 0
        self._setup_session()

    def _setup_session(self) -> None:
        if self.session_id is None:
            self.session_id = DatabaseManager.create_new_session()
            logger.info(f"PID={config.pid}; Session {self.session_id} started, active session count: {DatabaseManager.get_active_session_count()}")

        assert self.session_id is not None, "Error in creating session in DB"
        session_metadata = DatabaseManager.get_session(self.session_id)
        if session_metadata is None:
            raise ValueError(f"Session {self.session_id} not found in the database.")

        self.timestamp = session_metadata["timestamp"]
        self.active = session_metadata["active"]


    def close(self) -> None:
        """Close the session and update the database."""
        if self.session_id is None:
            logger.warning(f"pid={config.pid}; attempting to close session object without a session ID")
        else:
            DatabaseManager.deactivate_session(self.session_id)
            logger.info(f"Session {self.session_id} ended.")
        self.session_id = None
        self.active = False
        self.timestamp = None

    @staticmethod
    def _detect_smile(frame: MatLike) -> list:
        """Detect a smile in the given frame and return the coordinates of the rectangle."""
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        smiles = SessionManager.SMILE_CLASSIFIER.detectMultiScale(
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

    def _check_liveliness(self) -> bool:
        # check if the session is still active
        self.request_counter += 1
        if self.request_counter % 4 == 0:
            assert self.session_id is not None, "Error: attempting to check liveliness for a closed session"
            session_metadata = DatabaseManager.get_session(self.session_id)
            if session_metadata is None or not session_metadata["active"]:
                logger.info(f"PID={config.pid}; Liveliness check failed, Session {self.session_id} was closed.")
                self.close()
                return False
        return True

    def _produce_frames(self) -> Iterator[bytes]:
        """Producer logic that reads frames from the camera and writes to the database."""
        cap: cv2.VideoCapture = cv2.VideoCapture(self.webcam_idx)
        while True:
            start = time.time()

            # check the database to make sure the client didnt close the session
            if self._check_liveliness() is False:
                cap.release()
                # check_liveliness will call self.close if the db session is not active
                break

            frame_result : Tuple[bool, MatLike | None] = cap.read()
            if frame_result[0] is False or frame_result[1] is None:
                cap.release()
                raise IOError("Failed to read from camera")

            frame: MatLike = frame_result[1]
            # Detect smiles in the frame
            smiles = self._detect_smile(frame)

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
            frame_bytes: bytes = buffer.tobytes()

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


    def generate_frame_responses(self) -> Iterator[bytes]:
        """Generate responses for the frames."""
        genrtr = self._produce_frames()

        while True:
            try:
                frame = next(genrtr)
                assert frame
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except StopIteration:
                logger.info(f"PID={config.pid};Producer finished, stopping frame generation")
                break
            except Exception as e:
                logger.error(f"PID={config.pid};Producer failed, stopping frame generation;{traceback.format_exc()}")
                self.close()
                raise

    @staticmethod
    def dump_smiles(output_path: str) -> None:
        """Export smiles to the specified output path."""
        DatabaseManager.export_smiles(output_path)
        logger.info(f"PID={config.pid};Exported smiles to {output_path}")

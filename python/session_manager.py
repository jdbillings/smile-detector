import cv2
import time
from database_manager import DatabaseManager


class SessionManager:
    """Class to manage sessions and their metadata."""
    BASE_FPS_PER_REQUEST = 30

    def __init__(self):
        DatabaseManager.initialize_database()
        self.session_id: int = DatabaseManager.create_new_session()
        self.session_count: int = DatabaseManager.get_active_session_count()
        print(f"Session {self.session_id} started, session count: {self.session_count}")

        # Load Haar cascade for smile detection
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

    def close(self):
        """Close the session and update the database."""
        if self.session_id is not None:
            DatabaseManager.deactivate_session(self.session_id)
            print(f"Session {self.session_id} ended.")
            self.session_id = None

    def __del__(self):
        """Destructor to ensure the session is closed."""
        self.close()

    def detect_smile(self, frame) -> list:
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

    def produce_frames(self):
        """Producer logic that reads frames from the camera and writes to the database."""
        cap = cv2.VideoCapture(0)
        while True:
            start = time.time()
            success, frame = cap.read()
            if success:
                # Detect smiles in the frame
                smiles = self.detect_smile(frame)

                # Draw rectangles around detected smiles
                for (x, y, w, h) in smiles:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Encode the frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()

                # Write the frame to the database
                DatabaseManager.write_frame_to_db(frame_bytes, self.session_id)

                yield frame_bytes
                self.session_count = DatabaseManager.get_active_session_count()

                # Limit the frame rate to avoid contention on camera when we have concurrent sessions
                time.sleep(max(0.3 - (time.time() - start), 0))
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


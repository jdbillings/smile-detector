import cv2
import time
from database_manager import DatabaseManager


class SessionManager:
    """Class to manage sessions and their metadata."""
    BASE_FPS_PER_REQUEST = 30

    def __init__(self):
        DatabaseManager.initialize_database()
        self.session_id:int = DatabaseManager.create_new_session()
        self.session_count: int = DatabaseManager.get_active_session_count()
        print(f"Session {self.session_id} started, session count: {self.session_count}")


    def close(self):
        """Close the session and update the database."""
        if self.session_id is not None:
            DatabaseManager.deactivate_session(self.session_id)
            print(f"Session {self.session_id} ended.")
            self.session_id = None


    def __del__(self):
        """Destructor to ensure the session is closed."""
        self.close()


    def produce_frames(self):
        """Producer logic that reads frames from the camera and writes to the database."""
        cap = cv2.VideoCapture(0)
        while True:
            success, frame = cap.read()
            if success:
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                DatabaseManager.write_frame_to_db(frame_bytes, self.session_id)
                yield frame_bytes
                self.update_session_count()
                # Control the frame rate based on the session count
                time.sleep(min(0.8, self.session_count / self.BASE_FPS_PER_REQUEST))
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


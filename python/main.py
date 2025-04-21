from flask import Flask, Response
from session_manager import SessionManager

app = Flask(__name__)

@app.route('/video_feed')
def video_feed():
    """Flask route to serve the video feed."""
    session = SessionManager()
    # Return the video feed
    r = Response(session.generate_responses(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return r


def debug():
    app.run(host='127.0.0.1', port=5050)

if __name__ == "__main__":
    debug()
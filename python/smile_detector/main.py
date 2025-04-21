from flask import Flask, Response, jsonify, request
from smile_detector.session_manager import SessionManager
import os
import json
from flask_cors import CORS

with open(f"{os.path.dirname(__file__)}/conf/config.json", "r") as config_file:
    app_name = json.load(config_file)["python"]["flask_app_name"]

app = Flask(app_name)
CORS(app)  # Enable CORS for all routes


@app.route('/create-session', methods=['POST'])
def create_session():
    """Create a new session and return its ID."""
    session = SessionManager()
    session_id = session.session_id
    return jsonify({"sessionId": session_id})


@app.route('/video_feed/<int:session_id>')
def video_feed(session_id):
    """Flask route to serve the video feed for a specific session."""
    try:
        SM = SessionManager(session_id)
    except:
        return jsonify({"error": "Session not found"}), 404

    try:
        r = Response(SM.generate_frame_responses(), mimetype='multipart/x-mixed-replace; boundary=frame')
        return r
    except:
        return jsonify({"error": "Error in video generator"}), 500

@app.route('/latest-coords/<int:session_id>')
def latest_coords(session_id):
    """Return the latest coordinates for the specified session."""
    try:
        SM = SessionManager(session_id)
    except:
        return jsonify({"error": "Session not found"}), 404

    try:
        coords = SM.get_latest_coords(session_id)
        return jsonify(coords)
    except:
        return jsonify({"error": "Error getting coords"}), 500

@app.route('/close-session/<int:session_id>', methods=['POST'])
def close_session(session_id):
    """Close a specific session."""
    try:
        SM = SessionManager(session_id)
    except:
        return jsonify({"error": "Session not found"}), 404

    if SM.active is False:
        return jsonify({"message": "Session already closed"})

    try:
        SM.close()
        return jsonify({"message": f"Session {session_id} closed successfully"})
    except:
        return jsonify({"error": "Error closing session"}), 500

def debug():
    # run the Flask app in debug mode
    app.run(host='127.0.0.1', port=5050, debug=True)

if __name__ == "__main__":
    debug()
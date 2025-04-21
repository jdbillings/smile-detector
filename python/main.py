from flask import Flask, Response, jsonify, request
from session_manager import SessionManager
from database_manager import DatabaseManager
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
sessions = {}

DatabaseManager.initialize_database()

@app.route('/create-session', methods=['POST'])
def create_session():
    """Create a new session and return its ID."""
    session = SessionManager()
    session_id = session.session_id
    sessions[session_id] = session
    return jsonify({"sessionId": session_id})

@app.route('/video_feed/<int:session_id>')
def video_feed(session_id):
    """Flask route to serve the video feed for a specific session."""
    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404
    r = Response(sessions[session_id].generate_responses(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return r

@app.route('/latest-coords/<int:session_id>')
def latest_coords(session_id):
    """Return the latest coordinates for the specified session."""
    coords = DatabaseManager.get_latest_coords(session_id)
    return jsonify(coords)

@app.route('/close-session/<int:session_id>', methods=['POST'])
def close_session(session_id):
    """Close a specific session."""
    if session_id in sessions:
        session = sessions[session_id]
        session.close()
        del sessions[session_id]
        return jsonify({"message": f"Session {session_id} closed successfully"})
    return jsonify({"message": f"Session {session_id} not found"}), 404

def debug():
    app.run(host='127.0.0.1', port=5050, debug=True)

if __name__ == "__main__":
    debug()
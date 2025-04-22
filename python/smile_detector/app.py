from flask import Flask, Response, jsonify, request
from smile_detector.session_manager import SessionManager
from flask_cors import CORS
import os
import traceback
from typing import Any
from smile_detector.app_config import config, logger

app = Flask(config.app_name)
CORS(app)  # Enable CORS for all routes
logger.info(f"PID={config.pid}; app created with name {config.app_name}")


@app.route('/create-session', methods=['POST'])
def create_session() -> Any:
    """Create a new session and return its ID."""
    try:
        logger.debug(f"PID={config.pid};Creating new session")
        session_id = SessionManager().session_id
        return jsonify({"sessionId": session_id})
    except:
        msg = "Error creating session"
        logger.warning(f"PID={config.pid};{msg}")
        return jsonify({"error": f"{msg}"}), 500

@app.route('/video_feed/<int:session_id>')
def video_feed(session_id: int) -> Any:
    """Flask route to serve the video feed for a specific session."""
    try:
        SM = SessionManager(session_id)
        r = Response(SM.generate_frame_responses(), mimetype='multipart/x-mixed-replace; boundary=frame')
        return r
    except:
        msg = f"Error in video generator for session {session_id}"
        logger.warning(f"PID={config.pid};{msg}")
        return jsonify({"error": f"{msg}"}), 500

@app.route('/latest-coords/<int:session_id>')
def latest_coords(session_id: int) -> Any:
    """Return the latest coordinates for the specified session."""
    try:
        SM = SessionManager(session_id)
        coords = SM.get_latest_coords(session_id)
        return jsonify(coords)
    except Exception as e:
        msg = f"Error getting coords for session {session_id}"
        logger.warning(f"PID={config.pid};{msg};{traceback.format_exc()}")
        return jsonify({"error": f"{msg}"}), 500

@app.route('/close-session/<int:session_id>', methods=['POST'])
def close_session(session_id: int) -> Any:
    """Close a specific session."""
    try:
        SM = SessionManager(session_id)

        if SM.active is False:
            msg = f"Session {session_id} already closed"
            logger.warning(f"PID={config.pid};{msg}")
            return jsonify({"message": f"{msg}"}), 404

        SM.close()
        return jsonify({"message": f"Session {session_id} closed successfully"})
    except:
        msg = f"Error closing session {session_id}"
        logger.error(f"PID={config.pid};{msg}")
        return jsonify({"error": "{msg}"}), 500

@app.route("/dump-smiles", methods=["POST"])
def dump_smiles():
    """Dumps smiles to an absolute path on the file system."""
    try:
        canonical_path = request.json.get("canonical_path")
        if not canonical_path:
            return jsonify({"error": "No path provided"}), 400

        if not os.path.isabs(canonical_path):
            return jsonify({"error": "Path must be absolute"}), 400

        # Ensure path is normalized and resolved
        safe_path = os.path.normpath(os.path.realpath(canonical_path))

        SessionManager.dump_smiles(safe_path)
        return jsonify({"message": "Smiles exported successfully"})
    except Exception as e:
        msg = f"Error exporting smiles: {e}"
        logger.error(f"PID={config.pid};{msg}")
        return jsonify({"error": f"{msg}"}), 500


def debug() -> None:
    # run the Flask app in debug mode
    app.run(host=config.hostname, port=config.port, debug=True)

if __name__ == "__main__":
    debug()
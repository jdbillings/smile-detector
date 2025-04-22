import json
import pytest
import shutil
from smile_detector import database_manager

from smile_detector.app import *

@pytest.fixture(autouse=True)
def setup_and_teardown(monkeypatch):
    """Setup and teardown for each test."""
    test_id = os.urandom(8).hex()
    test_db_path = f"/tmp/smiledetector-test-{test_id}/sqlite.db"

    shutil.rmtree(os.path.dirname(test_db_path), ignore_errors=True)
    monkeypatch.setattr(database_manager.DatabaseManager, "DB_PATH", test_db_path)
    monkeypatch.setattr(database_manager.DatabaseManager, "DB_BASEDIR", os.path.dirname(test_db_path))

    database_manager.DatabaseManager.initialize_database()
    yield
    # Teardown code (if any) goes here
    shutil.rmtree(os.path.dirname(test_db_path), ignore_errors=True)


@pytest.fixture(autouse=True)
def app_fixture():
    app.config.update({"TESTING": True})
    yield app

@pytest.fixture()
def client_fixture(app_fixture):
    """Create a test client for the Flask app."""
    with app_fixture.test_client() as client:
        yield client

@pytest.fixture()
def runner_fixture(app_fixture):
    """Create a test runner for the Flask app."""
    with app_fixture.app_context():
        yield app.test_cli_runner()

def test_create_session(client_fixture):
    """Test the /create-session endpoint."""
    response = client_fixture.post('/create-session')
    assert response.status_code == 200, f"{response.get_json()}"

    data = response.get_json()
    assert "sessionId" in data
    assert isinstance(data["sessionId"], int)
    assert data["sessionId"] > 0

def test_dump_smiles(client_fixture):
    """Test the /dump-smiles endpoint."""
    # add jpeg data to the db

    test_case_data = f"/tmp/smiledetector-testdumpsmiles-{os.urandom(8).hex()}"
    session_id = database_manager.DatabaseManager.create_new_session()
    file_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(file_directory, "data/smile.jpg")
    with open(file_path, "rb") as f:
        jpeg_data = f.read()
    coords = [{"x": [0,0], "y": [0,1], "w": [1,0], "h": [1,1]}]
    database_manager.DatabaseManager.write_frame_to_db(jpeg_data, session_id, coords)


    response = client_fixture.post('/dump-smiles', json={"canonical_path": test_case_data})
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Smiles exported successfully"

    # Check if the directory exists
    assert os.path.exists(test_case_data)
    session_dir = os.path.join(test_case_data, str(session_id))
    assert os.path.exists(session_dir)
    # Check if the session directory is empty  
    assert len(os.listdir(session_dir)) > 0
    found = False
    for frame_dir in os.listdir(session_dir):
        frame_dir_path = os.path.join(session_dir, frame_dir)
        if not os.path.isdir(frame_dir_path):
            continue

        if not os.path.exists(os.path.join(frame_dir_path, f"{frame_dir}.jpg")):
            continue
        with open(os.path.join(frame_dir_path, f"{frame_dir}.jpg"), "rb") as f:
            jpeg_data = f.read()
            assert jpeg_data == jpeg_data
        with open(os.path.join(frame_dir_path, f"{frame_dir}.json"), "r") as f:
            json_data = json.load(f)
            assert json_data["coords"] == coords
            assert json_data["session_id"] == session_id
            assert json_data["timestamp"] is not None
        found = True
        break
    assert found, "No valid frame directories found in the session directory"

    # Clean up
    shutil.rmtree(test_case_data, ignore_errors=True)
    database_manager.DatabaseManager.deactivate_session(session_id)
    assert int(database_manager.DatabaseManager.get_session(session_id)["active"]) == 0
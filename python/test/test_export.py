import pytest

from smile_detector.app import *
from database_manager import DatabaseManager

from smile_detector.app_config import config

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test."""
    config.app_name = "test_app"
    config.database_path = "/tmp/smiledetector-test/sqlite.db"
    # Setup code (if any) goes here
    DatabaseManager.initialize_database()
    yield
    # Teardown code (if any) goes here
    os.path.remove(config.database_path)
    shutil.rmtree(os.path.dirname(config.database_path), ignore_errors=True)


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
    assert response.status_code == 200
    data = response.get_json()
    assert "sessionId" in data
    assert isinstance(data["sessionId"], int)
    assert data["sessionId"] > 0

def test_dump_smiles(client_fixture):
    """Test the /dump-smiles endpoint."""
    # add jpeg data to the db
    DatabaseManager.create_new_session()
    DatabaseManager.write_frame_to_db()


    response = client_fixture.post('/exportsmiles-foobar')
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Export completed successfully"
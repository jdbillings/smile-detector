## System Dependencies 
Please install the following dependencies using your favorite system package maanger:
- sqlite3
- node (includes npm, npx, etc)
- OpenCL
- python >= 3.13
  - pip
- bash
- make
- tkinter?

## How to install
This was only tested on MacOS, but in theory, it should work cross-platform relatively easily. 

To start, make sure the above system dependencies are available. 

Next, clone the `main` branch of this repository. 

Then, run `make rebuild-all` from the project root to configure a virtualenv with all required python packages installed, and also to install all npm packages needed for the React app. 

## How to run the web app
Open two terminal windows and navigate to the project root. In the first one, run `make run-gunicorn` to start the flask backend server, and in the second, run `scripts/run-react.sh` to start the react development server. The former will serve on `localhost:5050`, and the latter will serve on `localhost:3000`. Next, visit `localhost:3000` in your browser to view the application. Start the camera feed and smile to get the boxes/coordinates to appear. See ("Model Selection + Tuning" section of System Design Notes)[System-Design-Notes.md] for a discussion on how the accuracy of the smile detection could be improved. 

## How to run tests
- `make pytests` runs the test suite in `python/test/test_export.py`
- `make lint` runs mypy linter

## How to modify configuration
Please see `python/smile_detector/conf/config.json`. On a windows system, you may need to modify the default database path, for example.
If you modify that file, please rebuild and reinstall the `smile_detector` package. 

## How to view the images of smiles
The images are being stored in the sqlite3 database, which the default location is `/tmp/smile-detector/frames.db`. They're not stored on the filesystem by default. However, there's a REST endpoint `/dump-smiles` which you can use to write the JPEG files with smiles detected out to a directory of your choice. This is also demonstrated by the main test case in `python/test/test_export.py`. 
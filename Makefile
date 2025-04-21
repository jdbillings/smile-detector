
virtualenv:
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Creating virtual environment..." "----------------------------------------"
	@bash scripts/setup-venv.sh
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Done" "----------------------------------------"

install-requirements:
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Installing dependencies..." "----------------------------------------"
	@pip install -r python/requirements.txt
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Done" "----------------------------------------"

build-wheel:
	@echo "Building the project..."
	@bash -c '(cd python; python -m build --wheel --out-dir dist)'

install-wheel: build-wheel
	@echo "Installing the wheel..."
	@bash -c '(cd python; pip install dist/*.whl)'

install-react:
	@echo "Installing the React app..."
	@bash -c '(cd javascript/react-video-app ; npm install)'

run-react: install-react
	@echo "Running the React app..."
	@bash -c '(cd javascript/react-video-app ; npm install && npm start)'

run: install-wheel
	@echo "Running the project..."
	@bash -c '(cd python ; gunicorn -c conf/gunicorn.conf.py main:app)'

all:
	@bash scripts/run-all.sh

clean:
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Cleaning up..." "----------------------------------------"
#delete build artifacts
	@bash -c '(cd python ; rm -rf dist build *.egg-info)'
#delete sqlite database
	@bash -c '(cd python/conf ; python -c 'import json, shutil; shutil.rmtree( json.load( open("config.json", "r") )["sqlite"]["db_path"]  )' )'
#delete venv
	@bash -c '(cd python ; rm -rf venv)'
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Done" "----------------------------------------"

.PHONY: virtualenv install-requirements run-react run clean all

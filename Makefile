
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
	@bash -c '(source venv/bin/activate ; cd python; python -m build --wheel)'

install-wheel: build-wheel
	@echo "Installing the wheel..."
	@bash -c '(source venv/bin/activate ; cd python; pip uninstall -y smile_detector ; pip install dist/*.whl)'

install-react:
	@echo "Installing the React app..."
	@bash -c '(cd javascript/react-video-app ; npm install)'

rebuild-all:
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Rebuilding all..." "----------------------------------------"
	@bash scripts/rebuild-all.sh
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Done" "----------------------------------------"

run-gunicorn:
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Running Python server..." "----------------------------------------"
	@bash -c '(source venv/bin/activate && . scripts/run-gunicorn.sh)'

clean:
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Cleaning up..." "----------------------------------------"
#delete build artifacts
	@bash -c '(cd python ; rm -rf dist build *.egg-info)'
#delete sqlite database
	@bash -c 'python scripts/cleanup-db.py'
#delete venv
	@bash -c '(cd python ; rm -rf venv)'
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Done" "----------------------------------------"

.PHONY: virtualenv install-requirements run-react run-gunicorn clean rebuild-all


virtualenv:
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Creating virtual environment..." "----------------------------------------"
	@bash scripts/setup-venv.sh
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Done" "----------------------------------------"

install-requirements:
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Installing dependencies..." "----------------------------------------"
	@pip install -r python/requirements.txt
	@pip install -r python/requirements-dev.txt
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Done" "----------------------------------------"

build-wheel:
	@echo "Building the project..."
	@bash -c '(source venv/bin/activate ; cd python; python -m build --wheel)'

install-wheel: 
	@echo "Installing the wheel..."
	@bash -c '(source venv/bin/activate ; cd python; pip uninstall -y smile_detector ; pip install dist/*.whl)'

install-react:
	@echo "Installing the React app..."
	@bash -c '(cd javascript/react-video-app ; npm install)'

lint:
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Running Python linting..." "----------------------------------------"
	@bash -c '(source venv/bin/activate ; cd python ; mypy smile_detector )'

	@printf "%s\n%s\n%s\n" "----------------------------------------" "Running React linting..." "----------------------------------------"
	@bash -c '(cd javascript/react-video-app ; npm audit --production)'

	@printf "%s\n%s\n%s\n" "----------------------------------------" "Done" "----------------------------------------"

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
	@bash -c '(cd python ; rm -rf dist build *.egg-info .mypy_cache __pycache__ smile_detector/conf/__pycache__ smile_detector/__pycache__)'
#delete sqlite database
	@bash -c 'python scripts/cleanup-db.py'
#delete venv
	@bash -c 'rm -rf venv .mypy_cache'
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Done" "----------------------------------------"

pytests:
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Running Python tests..." "----------------------------------------"
	@bash -c '(source venv/bin/activate ; cd python/tests ; pytest -s)'
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Done" "----------------------------------------"


.PHONY: virtualenv install-requirements run-react run-gunicorn clean rebuild-all lint install-wheel install-react pytests

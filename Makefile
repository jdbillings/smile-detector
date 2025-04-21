
virtualenv:
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Creating virtual environment..." "----------------------------------------"
	@bash scripts/setup-venv.sh
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Done" "----------------------------------------"

install-deps: 
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Installing dependencies..." "----------------------------------------"
	@pip install -r python/requirements.txt
	@printf "%s\n%s\n%s\n" "----------------------------------------" "Done" "----------------------------------------"

build:
	@echo "Building the project..."
#   @mkdir -p build
	@echo "TODO" && exit 1

run: 
	@echo "Running the project..."
	@bash -c '(cd python ; gunicorn -c conf/gunicorn.conf.py main:app)'
	

.PHONY: make-virtualenv install-deps

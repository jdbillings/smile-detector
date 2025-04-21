#!/bin/bash -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../python"

echo "starting mypy linter..."
# Run mypy linter
mypy smile_detector

echo "finished linting..."

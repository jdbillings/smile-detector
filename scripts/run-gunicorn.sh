#!/bin/bash -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR/../"
source venv/bin/activate
cd python
gunicorn -c conf/gunicorn.conf.py smile_detector.main:app
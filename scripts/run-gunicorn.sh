#!/bin/bash -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR/../"
source venv/bin/activate
cd python
gunicorn -c smile_detector/conf/gunicorn.conf.py --log-level DEBUG smile_detector.app:app
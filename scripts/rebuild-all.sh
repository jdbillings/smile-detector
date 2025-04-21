#!/bin/bash -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR/.."
make clean
make virtualenv
source venv/bin/activate
make install-requirements
make build-wheel
make install-wheel
make install-react


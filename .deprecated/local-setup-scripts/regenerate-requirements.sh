#!/bin/bash -ex

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
echo "$SCRIPT_DIR"
rm "$SCRIPT_DIR/../python/requirements.txt" || true
pip freeze --all > "$SCRIPT_DIR/../python/requirements.txt"




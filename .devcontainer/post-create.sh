#!/bin/bash -ex

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR/../"

# note: we are already in a pyenv per the devcontainer.json
pip install --upgrade pip
pip install ipython # for developer convenience

make install-deps

sudo unminimize -y
sudo apt-get update -y 
sudo apt-get install -y shellcheck

echo "Success"

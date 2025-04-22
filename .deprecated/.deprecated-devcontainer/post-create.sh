#!/bin/bash -ex

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR/../"

# note: we are already in a pyenv per the devcontainer.json
pip install ipython # for developer convenience

make install-deps


sudo apt install -y libgl1 x11-apps


echo "post-create.sh: Success"

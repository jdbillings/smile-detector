#!/bin/bash 

export PYENV_VERSION="${PYENV_VERSION:-3.11}"

if which pyenv ; then 
    echo "pyenv already installed"
    exit 0
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd ${script_dir}

./get-pyenv.sh

export PYENV_ROOT="${HOME}/.pyenv"
export PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${HOME}/.local/bin:$PATH"

curl -sSL https://pyenv.run | bash

echo 'export PYENV_ROOT="${HOME}/.pyenv"' >> "${HOME}/.pyenvrc"
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> "${HOME}/.pyenvrc"
echo 'eval "$(pyenv init - bash)"' >> "${HOME}/.pyenvrc"

echo '# source ${HOME}/.pyenvrc' >> "${HOME}/.bashrc"
echo "added commented-out command to bashrc to make pyenv avaialble in new shells -- uncomment that line to enable it"

source "${HOME}/.pyenvrc"

pyenv install "$PYENV_VERSION"

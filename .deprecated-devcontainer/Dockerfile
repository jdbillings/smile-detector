FROM mcr.microsoft.com/devcontainers/base:jammy

ARG DEBIAN_FRONTEND=noninteractive
ARG USER=vscode

RUN DEBIAN_FRONTEND=noninteractive \
    && apt-get update \ 
    && apt-get install -y build-essential --no-install-recommends make \
        ca-certificates \
        git \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        wget \
        curl \
        llvm \
        libncurses5-dev \
        xz-utils \
        tk-dev \
        libxml2-dev \
        libxmlsec1-dev \
        libffi-dev \
        liblzma-dev \
    && apt-get install -y shellcheck 

RUN yes | unminimize

# Python and poetry installation
USER $USER
ARG HOME="/home/$USER"

ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${HOME}/.local/bin:$PATH"

ADD --chown=${USER}:${USER} --chmod=755 https://pyenv.run /tmp/pyenv-install.sh

RUN <<EOF
    set -e 
    bash /tmp/pyenv-install.sh 
    rm /tmp/pyenv-install.sh
EOF
ARG PYTHON_VERSION=3.11

RUN <<EOF
    set -e 
    pyenv install ${PYTHON_VERSION} 
    pyenv global ${PYTHON_VERSION} 
EOF

ADD --chown=${USER}:${USER} --chmod=755 https://install.python-poetry.org /tmp/get-poetry.py
RUN <<EOF 
    set -e
    python3 /tmp/get-poetry.py 
    rm /tmp/get-poetry.py 
    poetry config virtualenvs.in-project true
EOF

RUN pip install --upgrade pip

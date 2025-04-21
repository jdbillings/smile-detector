#!/bin/bash 
# Prerequisite: make sure xquartz security options has both Allow auth and Allow network connections enabled.
set -ex

ENABLE_X11_RESET="${ENABLE_X11_RESET:-true}" # by default, reset all x11 tempdirs. if you are running multiple x11 apps, you may want to set this to false.
XEYES_IMG_NAME="${XEYES_IMG_NAME:-xeyes-jammy-local-v1}"

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR"

if [ "$(docker image ls | grep -c "${XEYES_IMG_NAME}")" -eq 0 ] ; 
then
  # build an image so we only need to apt install x11-apps once
  docker build -t "${XEYES_IMG_NAME}" .
fi

# we want to restart xquartz cleanly, so we need to kill any existing xquartz processes first
set +e
pgrep -if xquartz | xargs -n1 echo kill -15 | bash # give opportunity to exit cleanly
sleep 2
pgrep -if xquartz | xargs -n1 echo kill -9  | bash 

set -e

if [[ "$ENABLE_X11_RESET" = "true" ]]; 
then
  # reset x11 directory. exit if sudo password prompt times out.
  function timeout() { perl -e 'alarm shift; exec @ARGV' "$@"; } # https://stackoverflow.com/questions/3504945/timeout-command-on-mac-os-x
  timeout 8 sudo bash -c 'rm -rf /tmp/.X11-unix* ; rm -rf /tmp/.X*-lock'
fi
x11_displayid="$(find /tmp/ -type f -name ".X*-lock" -depth 1 | wc -w | xargs)"
mkdir -p /tmp/.X11-unix

# start xquartz
open -a XQuartz
xhost +local:docker
xhost +localhost

# run xeyes in the container
docker run -it --rm -v /tmp/.X11-unix/:/tmp/.X11-unix --env "DISPLAY=host.docker.internal:${x11_displayid}" "${XEYES_IMG_NAME}" xeyes

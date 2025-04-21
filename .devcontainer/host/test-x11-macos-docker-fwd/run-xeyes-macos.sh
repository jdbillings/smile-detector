#!/bin/bash
# Prerequisite: make sure xquartz security options has both Allow auth and Allow network connections enabled.
set -ex

### global variables ###
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ENABLE_X11_RESET="${ENABLE_X11_RESET:-true}" # by default, reset all x11 tempdirs and force restart of xquartz. if you are running multiple x11 apps, you may want to set this to false.
XEYES_IMG_NAME="${XEYES_IMG_NAME:-xeyes-jammy-local-v1}"
LOCKFILE_COUNT="-1"
x11_displayid="-1"

### functions ###
function timeout() { perl -e 'alarm shift; exec @ARGV' "$@"; } # https://stackoverflow.com/questions/3504945/timeout-command-on-mac-os-x

function build_docker_img() {
  # build an image so we only need to `apt install x11-apps` once
  if [[ "$(docker image ls | grep -c "${XEYES_IMG_NAME}")" -eq 0 ]] ; then
    echo "INFO: building docker image ${XEYES_IMG_NAME}"
    docker build -t "${XEYES_IMG_NAME}" .
  else
    echo "INFO: docker image ${XEYES_IMG_NAME} already exists"
  fi
}

function kill_xquartz() {
  set +e
  # give opportunity to exit cleanly w/ SIGTERM
  pgrep -if xquartz | xargs -n1 echo kill -15 | bash
  for i in {1..4}; do
    if pgrep -if xquartz > /dev/null ; then sleep "$i" ; else break ; fi
  done

  # send SIGKILL to any remaining xquartz processes
  pgrep -if xquartz  | xargs -n1 echo kill -9 | bash
  set -e

}

function cleanup_xquartz() {
  if [[ "$ENABLE_X11_RESET" = "true" ]];
  then
    echo "INFO: killing xquartz and cleaning up any artifacts"
    kill_xquartz
  else
    echo "INFO: kill_quartz disabled by env var"
  fi

  # cleanup any artifacts left behind from prior x11 sessions
  timeout 10 sudo bash -c 'rm -rf /tmp/.X11* ; rm -rf /tmp/.X*-lock'
}

function get_lock_counter() {
  LOCKFILE_COUNT="$(find /tmp/ -type f -name ".X*-lock" -depth 1 | wc -w | xargs)"
  if [[ $LOCKFILE_COUNT -gt 255 ]] ; then echo "Error: too many X11 lockfiles found." ; exit 1 ; fi
  echo "$LOCKFILE_COUNT"
}

function start_xquartz() {
  # start xquartz
  mkdir -p /tmp/.X11-unix
  open -a XQuartz

  # wait for xquartz to start
  timeout 10 bash -c 'while ! pgrep -if xquartz > /dev/null ; do sleep 1 ; done'

  # wait for xquartz to create the lockfile
  sleep 4
}

### Main() ###

cd "$SCRIPT_DIR"
cleanup_xquartz
start_xquartz
build_docker_img

if [[ $LOCKFILE_COUNT -le 0 ]];
then
  echo "INFO: no lockfiles found, using display id 0"
  x11_displayid="0"
else
  x11_displayid=$((LOCKFILE_COUNT-1))
fi

# setup permissions for x11 client (in docker container) to access XServer (on macos host)
xhost +local:docker
xhost +localhost

# run xeyes in the container
docker run -it --rm -v /tmp/.X11-unix/:/tmp/.X11-unix --env "DISPLAY=host.docker.internal:${x11_displayid}" "${XEYES_IMG_NAME}" xeyes

cleanup_xquartz

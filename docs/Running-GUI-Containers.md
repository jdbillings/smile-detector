# How to run containerized Docker GUI app locally

## MacOS
- Install [XQuartz](https://www.xquartz.org/releases/index.html) and Docker Desktop for MacOS.
- Open XQuartz GUI app. Open Settings -> Security. Enable "Authenticate Connections" and "Allow connections from network clients" options. Quit XQuartz.
- Test your setup: Open a terminal, and run `.devcontainer/host/test-x11-macos-docker-fwd/run-xeyes-macos.sh`. It should create a GUI window on the host, with eyes that follow your mouse cursor.
- devcontainer.json will hardcode "DISPLAY=host.docker.internal:0", assuming that it can obtain /tmp/.X0-lock.
    - If you have concurrent X11 apps or XQuartz received SIGKILL, you may need to increment the display ID. run-xeyes-macos.sh handles this edge case -- see that script for more info
## Windows / Linux
### Windows
- Setup Docker Desktop to use WSL2 as its backend
- [Use WSLg to enable X11 (or Wayland) forwarding](https://github.com/microsoft/wslg/blob/main/samples/container/Containers.md)
### Linux
- X11/Wayland and Docker are native to Linux. Same idea as Windows, just simpler without the WSLg middleware.
### Devcontainer.json
- This is hardcoded to MacOS. You'll probably want `DISPLAY=${hostEnv:DISPLAY}` , not `DISPLAY=host.docker.internal:0`

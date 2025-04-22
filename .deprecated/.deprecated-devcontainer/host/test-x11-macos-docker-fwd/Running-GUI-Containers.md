# How to run containerized Docker GUI app locally

## MacOS
- Install [XQuartz](https://www.xquartz.org/releases/index.html) and Docker Desktop for MacOS.
- Open XQuartz GUI app. Open Settings -> Security. Enable "Authenticate Connections" and "Allow connections from network clients" options. Quit XQuartz.
- Test your setup: Open a terminal, and run `.devcontainer/host/test-x11-macos-docker-fwd/run-xeyes-macos.sh`. It should create a GUI window on the host, with eyes that follow your mouse cursor.
## Windows
- Setup Docker Desktop to use WSL2 as its backend
- [Use WSLg to enable X11 (or Wayland) forwarding](https://github.com/microsoft/wslg/blob/main/samples/container/Containers.md)
## Linux
- X11/Wayland and Docker are native to Linux. Same idea as Windows, just simpler without the WSLg middleware.
## Devcontainer.json
- The environment variable to enable x11 forwarding, `DISPLAY=host.docker.internal:0`, is hardcoded for MacOS. 
  - On Windows/Linux, you'll probably want `DISPLAY=${hostEnv:DISPLAY}` instead
#### MacOS assumptions
- XQuartz must be running, and you must also run `xhost +local:docker ; xhost +localhost` on restart
- There shouldn't be existing XQuartz artifacts in `/tmp/`. 
  - See `run-xeyes-macos.sh` for how you can handle cases where this isn't true
    - If XQuartz did not exit gracefully, you may need to clear files from /tmp
    - If you have concurrent x11 apps running, you may need to increment the display ID accordingly.

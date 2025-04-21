# How to run containerized Docker GUI app locally on MacOS

- Install [XQuartz](https://www.xquartz.org/releases/index.html) and Docker Desktop for MacOS.
- Open XQuartz GUI app. Open Settings -> Security. Enable "Authenticate Connections" and "Allow connections from network clients" options. Quit XQuartz.
- Test your setup: Open a terminal, and run `.devcontainer/host/test-x11-macos-docker-fwd/run-xeyes-macos.sh`. It should create a GUI window on the host, with eyes that follow your mouse cursor. 
- 
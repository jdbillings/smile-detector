#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR/../javascript"
yes | npx create-react-app react-video-app --template typescript 
cd react-video-app
# Install the necessary dependencies for handling the video feed and styling:
npm install axios

# make npm audit --production not complain about old CVEs
npm install react-scripts@^5.0.1 --save-dev
npm install

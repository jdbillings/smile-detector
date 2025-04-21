#!/bin/bash -e

# todo: do I need tkinter anymore? probably not


if which brew ; then 
    yes | brew install python-tk
    exit 0

elif which apt-get ; then    
    sudo apt-get install -y python3-tk
    exit 0

elif which dnf ; then 
    sudo dnf install -y python3-tkinter
    exit 0
else
    echo "No package manager found. Please install python-tk or python3-tk manually."
    exit 1
fi
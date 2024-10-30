#!/bin/bash

# Check if the script is running as root(service).
if [ $(id -u) -ne 0 ]; then
    echo "VG Stater must be run as root."
    echo "Try 'sudo bash $0'"
    exit 1
fi

# Get the path of the script
DIR="$( cd "$( dirname "$0" )" && pwd -P )"
echo VG Program Path=\'$DIR\'
cd $DIR

# Start the VG program without sudo
python3 main.py
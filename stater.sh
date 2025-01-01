#!/bin/bash

if [ $(id -u) -ne 0 ]; then
    echo "VGServer Stater must be run as root."
    echo "Try 'sudo bash $0'"
    exit 1
fi

DIR="$( cd "$( dirname "$0" )" && pwd -P )"
echo VGServer Program Path=\'$DIR\'
cd $DIR

python3 app.py
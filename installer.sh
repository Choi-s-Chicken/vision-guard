#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd -P )"

# Get the path of the script
echo VGServer Program Path=\'$DIR\'
cd "$DIR"

# Check if the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "VGServer Installer must be run as root."
    echo "Try 'sudo bash $0'"
    exit 1
fi

echo "This VGServer_Installer will reboot after execution."
echo -n "Do you want to continue? [y/[n]] "
read -r REPLY
if [[ ! "$REPLY" =~ ^(yes|y|Y)$ ]]; then
    echo "Exit by refusing reboot."
    exit 1
fi

# apt update upgrade
echo "Updating and upgrading system..."
if apt update && apt upgrade -y; then
    echo "System updated and upgraded successfully."
else
    echo "System update and upgrade failed."
    exit 1
fi

# install module
echo "Installing python modules..."
if python3 -m pip config set global.break-system-packages true; then
    if pip install -r requirements.txt; then
        echo "python modules install successfully."
    else
        echo "python modules install failed."
        exit 1
    fi
else
    echo "python modules install failed."
    exit 1
fi

# install service
echo "Installing service..."
## copy service file
if sudo cp ./src/vgserver.service /lib/systemd/system/vgserver.service; then
    echo ".service file copied successfully."
else
    echo
    echo "VGServer installation failed."
    exit 1
fi
## change permission
if sudo chmod 644 /lib/systemd/system/vgserver.service; then
    echo "Service permission changed successfully."
else
    echo
    echo "VGServer installation failed."
    exit 1
fi
## reload daemon
if sudo systemctl daemon-reload; then
    echo "Daemon reloaded successfully."
else
    echo
    echo "VGServer installation failed."
    exit 1
fi
## enable service
if sudo systemctl enable vgserver.service; then
    echo "Service enabled successfully."
else
    echo
    echo "VGServer installation failed."
    exit 1
fi
echo "Service installation completed successfully."
echo

# complete installation
echo "VGServer installation completed successfully."
echo

# reboot
for ((i=5; i>=1; i--)); do
    echo "Reboot in $i seconds..."
    sleep 1
done
echo "Reboot process started."
reboot now
#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd -P )"

# Get the path of the script
echo VG Program Path=\'$DIR\'
cd "$DIR"

# Check if the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "VG Installer must be run as root."
    echo "Try 'sudo bash $0'"
    exit 1
fi

echo "This VG_Installer will reboot after execution."
echo -n "Do you want to continue? [y/[n]] "
read -r REPLY
if [[ ! "$REPLY" =~ ^(yes|y|Y)$ ]]; then
    echo "Exit by refusing reboot."
    exit 1
fi

# install module
## ~~~

# install service
echo "Installing service..."
## copy service file
if sudo cp ./src/vg.service /lib/systemd/system/vg.service; then
    echo ".service file copied successfully."
else
    echo
    echo "VG installation failed."
    exit 1
fi
## change permission
if sudo chmod 644 /lib/systemd/system/vg.service; then
    echo "Service permission changed successfully."
else
    echo
    echo "VG installation failed."
    exit 1
fi
## reload daemon
if sudo systemctl daemon-reload; then
    echo "Daemon reloaded successfully."
else
    echo
    echo "VG installation failed."
    exit 1
fi
## enable service
if sudo systemctl enable vg.service; then
    echo "Service enabled successfully."
else
    echo
    echo "VG installation failed."
    exit 1
fi
echo "Service installation completed successfully."
echo

# complete installation
echo "VG installation completed successfully."
echo

# reboot
for ((i=5; i>=1; i--)); do
    echo "Reboot in $i seconds..."
    sleep 1
done
echo "Reboot process started."
reboot now
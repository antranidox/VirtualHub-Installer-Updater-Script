#!/bin/bash

echo "############################################################"
echo " VIRTUALHUB INSTALLER-NG / UPDATER-NG SCRIPT, VERSION 3.2.1 "
echo "############################################################"

# you need to be root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root, or Groot :p" 
   exit 1
fi

# install dependencies
echo "Installing dependencies..."
apt-get install curl php5-cli php5-curl unzip wget libusb-1.0.0-dev -y

wget https://raw.githubusercontent.com/auckenox/VirtualHub-Installer-Updater-Script/master/virtualhub_updater.php -O /tmp/virtualhub_updater.php
mv /tmp/virtualhub_updater.php /usr/bin/virtualhub_updater
chmod +x /usr/bin/virtualhub_updater
/usr/bin/virtualhub_updater




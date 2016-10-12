#!/bin/bash

echo "############################################################"
echo " VIRTUALHUB INSTALLER-NG / UPDATER-NG SCRIPT, VERSION 3.3.0 "
echo "############################################################"

# os: macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
curl "https://raw.githubusercontent.com/auckenox/VirtualHub-Installer-Updater-Script/master/virtualhub_updater.php" > /tmp/virtualhub_updater.php
mv /tmp/virtualhub_updater.php /usr/local/bin/virtualhub_updater
chmod +x /usr/local/bin/virtualhub_updater
/usr/local/bin/virtualhub_updater
exit 0
fi

# os: Linux
wget https://raw.githubusercontent.com/auckenox/VirtualHub-Installer-Updater-Script/master/virtualhub_updater.php -O /tmp/virtualhub_updater.php
mv /tmp/virtualhub_updater.php /usr/bin/virtualhub_updater
chmod +x /usr/bin/virtualhub_updater

# you need to be root
if [[ $EUID -ne 0 ]]; then
   echo "please run this script as root, or install dependencies yourself by typing:"
   echo "apt-get install curl php5-cli php5-curl unzip wget libusb-1.0.0-dev -y"
   echo ""
   echo "and after that start the script by just typing:"
   echo "virtualhub_updater"
   exit 1
else
# install dependencies
echo "Installing dependencies..."
apt-get install curl php5-cli php5-curl unzip wget libusb-1.0.0-dev -y
exit 0
fi


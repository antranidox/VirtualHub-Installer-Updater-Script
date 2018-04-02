### what is this?
Use this script to automatically download and install VirtualHub from yoctopuce.com.

This version of the script works for Linux, macOS and Synology.
It uses regex to check for the newest VirtualHub version on the yoctopuce website and compares the version number to the already installed (or just doing a new install, if VirtualHub wasnt found on the device).
If a update is available it downloads it to your device, unzips the zip file, installs the binary and the startscript (systemd only - so far)

#### tested on
+  Raspbian stretch
+  macOS 10.13.3
+  Synology DSM 6.x (armv7, DS214)

#### requirements:
* python 2.7 or python 3.x
* internet connection

#### usage - the easy way:
1. `curl https://raw.githubusercontent.com/auckenox/VirtualHub-Installer-Updater-Script/master/VirtualHub_installer.py | python`

#### usage
1. Download the VirtualHub_installer_or_updater.py
2. `python VirtualHub_installer_or_updater.py`


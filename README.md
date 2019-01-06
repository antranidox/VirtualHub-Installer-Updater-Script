### what is this?
Use this script to automatically download and install VirtualHub from yoctopuce.com.

This version of the script works for Raspbian / Debian / Ubuntu and macOS
It gets the newest VirtualHub version on the yoctopuce website and compares the installed version (or just doing a new install, if VirtualHub wasnt found on the device).
If a update is available it downloads it to your device, unzips the zip file, installs the binary and the startscript if you want to (systemd only)

#### tested on
+  Raspbian stretch
+  macOS 10.14.2

#### requirements:
* python 3.x
* internet connection

#### usage - the easy way:
1. `curl https://raw.githubusercontent.com/auckenox/VirtualHub-Installer-Updater-Script/master/VirtualHub_installer.py | python3`

#### usage
1. `git clone https://github.com/auckenox/VirtualHub-Installer-Updater-Script.git && cd VirtualHub-Installer-Updater-Script`
2. `python3 VirtualHub_installer_or_updater.py`

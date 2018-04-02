### what is this?
Use this script to automatically download and install VirtualHub from yoctopuce.com.

This version of the script works for Linux, macOS and Synology.
It uses regex to check for the newest VirtualHub version on the yoctopuce website and compares the version number to the already installed (or just doing a new install, if VirtualHub wasnt found on the device).
If a update is available it downloads it to your device, unzips the zip file, installs the binary and the startscript (systemd only - so far)

#### tested on
+  Raspbian stretch
+  macOS 10.13.3
+  EXPERIMENTAL: Synology DSM 6.x

#### requirements:
* python 2.7 or python 3.x
* internet connection

#### usage - the easy way:
1. `curl https://raw.githubusercontent.com/auckenox/VirtualHub-Installer-Updater-Script/master/VirtualHub_installer.py | python`

#### usage
1. Download the VirtualHub_installer_or_updater.py
2. `python VirtualHub_installer_or_updater.py`


#### synology:
i tested this script with a DS214 (armv7) and a the Plex Package,
the Plex Package is needed because it has a libusb-1.0.so.0 file that is needed to run VirtualHub.
You always can compile libusb-1.0 it yourself, if you do so, you need version 1.0.9!
Because higher versions of libusb depend on udev and are not working on synology (AFAIK)
You can get the source from https://sourceforge.net/projects/libusb/
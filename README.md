### what is this?
Use this script to automatically download and install VirtualHub from yoctopuce.com.

### tell me more
This version of the script works for Linux and on macOS.
It uses Regex to check for the newest VirtualHub version on the website and compares to the already installed (or just doing a new install, if VirtualHub wasnt found on the device).
If a update is available it downloads it to your device, unzips the zip file, installs the binary and the startscript (systemd only)

#### tested on
+  Raspbian stretch, python 2.7
+  macOS 10.13.3, python3.x

#### requirements:
* python requests (install by: pip install requests)
* python
* internet connection

#### usage - the easy way:
1. `curl https://raw.githubusercontent.com/auckenox/VirtualHub-Installer-Updater-Script/master/VirtualHub_installer_or_updater.py | python`

#### usage
1. Download the VirtualHub_installer_or_updater.py
2. `python VirtualHub_installer_or_updater.py`


##### legacy info:
this project was once written in bash and php, those files are still there for legacy reasons.
<<<<<<< HEAD
you only need VirtualHub_installer_or_updater.py now
=======
you only need VirtualHub_installer_or_updater.py now
>>>>>>> 190cacf4626481a100a254b74d559923c1c7b506

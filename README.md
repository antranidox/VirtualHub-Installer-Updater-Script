###dahell is this?
Use this script to automatically download and install VirtualHub from yoctopuce.ch.

This version of the script works for the armhf VirtualHub (Raspberry Pi & co) and on macOS.
It uses Regex to check for the newest VirtualHub version on the website and compares to the already installed (or just doing a new install, if VirtualHub wasnt found on the device).
If a update is available it downloads it with curl to your device, unzip the zip file, installs the armhf binary (or x86 on Mac), installs the startscript and finally starts VirtualHub as a service.

Tested on Raspbian Pi1 & Pi2.
..and on macOS Sierra (only install, without startscript and stuff)

####Requirements:
* curl
* php5-cli
* php5-curl
* unzip
* internet connection
* yoctopuce devices

On Linux, install the requirements with this command:
`apt-get install curl php5-cli php5-curl unzip`

on macOS, all requirements should be satisfied from the beginning.

###Usage - the easy way:
1. `curl https://raw.githubusercontent.com/auckenox/VirtualHub-Installer-Updater-Script/master/vh_install.sh | bash`

###Usage:
1. Download the virtualhub_updater.php file to your armhf device or Mac
2. `chmod +x virtualhub_updater.php`
3. execute virtualhub_updater.php directly with `php virtualhub_updater.php` 
4. or copy the script to /usr/bin/ on Raspbian or to /usr/local/bin on macOS `cp virtualhub_updater.php /usr/bin/virtualhub_updater` from now on you can start it with typing `virtualhub_updater`

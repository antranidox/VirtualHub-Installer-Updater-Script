###daquf is this?
Use this script to automatically download and install VirtualHub from [yoctopuce.ch]().

This version of the script works only for the armhf VirtualHub (Raspberry Pi & co).
It uses Regex to check for the newest version on the website and compares to the already installed (or just doing a new install, if virtualhub wasnt found on the device).
If a update is available it downloads it with curl to your device, unzip the zip file, installs the armhf binary, installs the startscript and finally starts VirtualHub as a service.

Tested only on Raspbian.

####Requirements:
* curl
* php5-cli
* unzip
* internet connection
* yoctopuce devices

###Usage:
1. Download the virtualhub_updater.php file to your armhf device
2. `chmod +x virtualhub_updater.php`
3. execute virtualhub_updater.php directly with `php -f virtualhub_updater.php` 
4. or copy the script to /usr/bin/ `cp virtualhub_updater.php /usr/bin/virtualhub_updater` from now on you can start it with typing `virtualhub_updater`

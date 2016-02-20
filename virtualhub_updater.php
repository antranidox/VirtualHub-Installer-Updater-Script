#!/usr/bin/php
<?php
define("temp_dir","/tmp/");
if(!file_exists("/usr/bin/unzip")) {echo "Please install unzip first. \n apt-get install unzip -y"; exit;}
$cred="\033[33m"; $cgreen="\033[32m"; $cwhite="\033[0m"; $clblue="\033[34m";

echo $line=str_repeat("-=", 35);
echo "\n          VirtualHub Linux Installer / Updater Script 1.0\n";
echo $line."\n\n";

$ydlp = file_get_contents("http://www.yoctopuce.com/EN/virtualhub.php");
preg_match("/VirtualHub\\.linux\\.(\\d*).zip/", $ydlp, $current_version); // getting build-number from website
$iversion_raw = shell_exec("/usr/sbin/VirtualHub -v");
preg_match("/(\\d*) \\(/", $iversion_raw, $installed_version); // extracting only the build-number from local VH
if(is_numeric($installed_version[1])) { echo "                Installed VirtualHub Build: ".$installed_version[1];} 
else {echo "                Installed VirtualHub Build: $cred NONE $cwhite";}
      echo "\n                Current   VirtualHub Build: ".$current_version[1];

// update VH
if($installed_version[1]!=$current_version[1]) {
echo "\n\n $clblue $line \n                       a new update is available ...\n $line \n $cwhite";
preg_match_all("/<a href='(\\/FR\\/downloads\\/VirtualHub\\.\\S*\\.\\d*.zip)/", $ydlp, $matches); // extracting file link
$purl = "http://www.yoctopuce.com/".$matches[1][1];
echo "\nDownloading VirtualHub Zip file from $purl to ".temp_dir."vh_install/";
echo $res = shell_exec("curl -k -L $purl -o ".temp_dir."vh.zip");
if(!file_exists(temp_dir."vh.zip")) {echo "file not found, there seems to be a problem. sorry. ERR-1"; exit;}
echo "Unzipping ".temp_dir."vh.zip now to ".temp_dir."vh_install";
echo $res2 = shell_exec("unzip -o ".temp_dir."vh.zip -d ".temp_dir."vh_install");
unlink(temp_dir."vh.zip");
echo "Installing VirtualHub binary...";
echo $res3 = shell_exec("cp -f -v ".temp_dir."vh_install/armhf/VirtualHub /usr/sbin/VirtualHub");
echo "Installing Startscript for VirtualHub...\n";
echo $res4 = shell_exec("cp -f -v ".temp_dir."vh_install/startup_script/yVirtualHub /etc/init.d/VirtualHub")."\n";
echo $res5 = shell_exec("chmod +x /etc/init.d/VirtualHub && update-rc.d VirtualHub defaults")."\n";
echo "Starting VirtualHub now as a service...\n";
echo $res6 = shell_exec("service VirtualHub start && pidof VirtualHub")."\n";
echo "$clblue Please check http://{THISIP}:4444 in your browser $cwhite \n$line\n$line";
}
else
{
// no update needed
echo "\n\n$cgreen $line\n           You already have the newest Build of VirtualHub!\n $line \n$cwhite\n\n";
}

?>
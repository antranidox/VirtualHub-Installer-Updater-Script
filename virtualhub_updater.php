#!/usr/bin/php
<?php
define("yVirtualHubURL","http://www.yoctopuce.com/EN/virtualhub.php");

/* --------- yMatchNo ---------
[0] => /FR/downloads/VirtualHub.windows.25250.zip
[1] => /FR/downloads/VirtualHub.linux.25250.zip
[2] => /FR/downloads/VirtualHub.osx.25250.zip
[3] => /FR/downloads/VirtualHub.qnap.25250.zip
*/

if(PHP_OS=="Darwin") 
{
define("myOS","macOS");
define("temp_dir","/tmp/");
$yMatch = "/VirtualHub\\.osx\\.(\\d*).zip/";
define("yAppLocation","/usr/local/bin/VirtualHub");
define("yMatchNo",2);
}
else
{
define("myOS","Linux, ".PHP_OS);
define("temp_dir","/tmp/");
if(!file_exists("/usr/bin/unzip")) {echo "Please install unzip first. \n apt-get install unzip -y"; exit;}
$yMatch = "/VirtualHub\\.linux\\.(\\d*).zip/";
define("yAppLocation","/usr/sbin/VirtualHub");
define("yMatchNo",1);
}


$cred="\033[31m"; $cgreen="\033[32m"; $cwhite="\033[0m"; $clblue="\033[34m";

echo $line=str_repeat("-=", 35);
echo "\n      VirtualHub Linux/macOS Updater / Installer Script 1.2 (".myOS.")\n";
echo $line."\n\n";


$ydlp = file_get_contents(yVirtualHubURL);
preg_match($yMatch, $ydlp, $current_version); // getting build-number from website
$iversion_raw = shell_exec(yAppLocation." -v");
preg_match("/(\\d*) \\(/", $iversion_raw, $installed_version); // extracting only the build-number from local VH
if(is_numeric($installed_version[1])) { echo "                Installed VirtualHub Build: ".$installed_version[1];} 
else {echo "                Installed VirtualHub Build: ".$cred." NONE ".$cwhite;}
      echo "\n                Current   VirtualHub Build: ".$current_version[1];
     

// update VH
if($installed_version[1]!=$current_version[1]) {
echo "\n\n $clblue $line \n                       a new update is available ...\n ".$line." \n ".$cwhite;
preg_match_all("/<a href='(\\/FR\\/downloads\\/VirtualHub\\.\\S*\\.\\d*.zip)/", $ydlp, $matches); // extracting file link
$purl = "http://www.yoctopuce.com/".$matches[1][yMatchNo];
echo "\nDownloading VirtualHub Zip file from $purl to ".temp_dir."vh_install/";
echo $res = shell_exec("curl -k -L $purl -o ".temp_dir."vh.zip");
if(!file_exists(temp_dir."vh.zip")) {echo "\nfile not found, there seems to be a problem. sorry. ERR-1"; exit;}
echo "Unzipping ".temp_dir."vh.zip now to ".temp_dir."vh_install";
echo $res2 = shell_exec("unzip -o ".temp_dir."vh.zip -d ".temp_dir."vh_install");
unlink(temp_dir."vh.zip");

// finding the right VirtualHub binary
$hsz_exists=false;
exec('find /tmp/vh_install/ -name VirtualHub',$vhubs);
foreach($vhubs as $biloc){
	if($biloc=="/tmp/vh_install/armel/VirtualHub") {continue;} // pi1 armhf fix!
	exec('chmod +x '.$biloc.' && '.$biloc.' -v > /dev/null 2>&1',$output,$ecode);
	echo "\ntesting $biloc.. result: $ecode";
	if($ecode==127) {$hsz_exists=true; $bin127=$biloc;}
	if($ecode==0) {$binary_location=$biloc; break;}
}
if(!isset($binary_location)) 
{
	echo "\n$cred\nFatal Error: could not guess the right binary!".$cwhite."\n\n";
	if($hsz_exists) {echo "Info: you can try to run $bin127 yourself and check the error message. maybe you need to install libusb-1.0 with:\napt-get install libusb-1.0.0-dev\n\n";}
	echo $line."\n\n\n\n";
	exit;
}

echo "\nInstalling VirtualHub binary to ".yAppLocation."...";
echo $res3 = shell_exec("cp -f -v ".$binary_location." ".yAppLocation);

// only on Linux (not on macOS)
if(PHP_OS!="Darwin") {
	echo "\nInstalling Startscript for VirtualHub...\n";
	echo $res4 = shell_exec("cp -f -v ".temp_dir."vh_install/startup_script/yVirtualHub /etc/init.d/VirtualHub")."\n";
	echo $res5 = shell_exec("chmod +x /etc/init.d/VirtualHub && update-rc.d VirtualHub defaults")."\n";
	echo "\nStarting VirtualHub now as a service...\n";
	echo $res6 = shell_exec("service VirtualHub start")."\n";
	sleep(1);
	exec("pidof VirtualHub",$pid_output,$ecodeX);
	if($ecodeX==0) {
	echo "\n$clblue VirtualHub is now running with PID ".$pid_output[0]."\n";
	echo "\nPlease check http://{THISIP}:4444 in your browser $cwhite \n$line\n$line";
	}
}
else
{
// on macOS
echo "VirtualHub is now installed / updated, start it by typing VirtualHub in your terminal.";
}

}
else
{
// no update needed
echo "\n\n".$cgreen." ".$line."\n           You already have the newest Build of VirtualHub!\n ".$line." \n".$cwhite."\n\n";
}
?>

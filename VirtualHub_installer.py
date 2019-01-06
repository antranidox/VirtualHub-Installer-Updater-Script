#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tested with: macOS 10.14.2
requirements: requests

"""

import sys,os,re,time,shutil,zipfile,subprocess,platform,json,requests

script_version = "2.0.0"


updateCheckUrl = "https://www.yoctopuce.com/FR/common/getLastFirmwareLink.php"

myOS = platform.uname()

# checking if verbose mode is on (with the -v flag)
verbose = False
if len(sys.argv)>1:
	if sys.argv[1]=="-v":
		verbose = True
		print("verbose mode: on")


class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


print(bcolors.OKBLUE+'='*100+bcolors.ENDC)
print(bcolors.OKBLUE+"                     UNOFFICIAL VirtualHub installer/updater %s" %script_version+bcolors.ENDC)
print(bcolors.OKBLUE+'='*100+bcolors.ENDC)
print("")


# system is macOS
if myOS[0] == 'Darwin':
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15'}
	appLocation = "/usr/local/bin/VirtualHub"
	tempLocation = "/tmp"
	fromPath = tempLocation+"/VirtualHub/VirtualHub"

# system is Linux
if myOS[0] == 'Linux':
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
	appLocation = "/usr/local/bin/VirtualHub"
	tempLocation = "/tmp"
	fromPath = ''

# defaults
if appLocation == '':
	appLocation = "/bin/VirtualHub"
	tempLocation = "/tmp"
	fromPath = ''

if verbose:
	print("-"*100)
	print("using these settings:")
	print("  appLocation:	%s"%appLocation)
	print("  tempLocation:	%s"%tempLocation)
	print("  fromPath:		%s"%fromPath)
	print("-"*100)


def exitScript(type,message):
	if type == 'good':
		print(bcolors.OKGREEN+"-"*100+bcolors.ENDC)
		print(bcolors.OKGREEN+message+bcolors.ENDC)
		print(bcolors.OKGREEN+"-"*100+bcolors.ENDC)
		exit(0)
	else:
		print(bcolors.FAIL+"X"*100+bcolors.ENDC)
		print(bcolors.FAIL+message+bcolors.ENDC)
		print(bcolors.FAIL+"X"*100+bcolors.ENDC)
		exit(1)

def downloadFile(url,filename):
	try:
		r = requests.get(url, stream=True)
		with open(filename, 'wb') as f:
			shutil.copyfileobj(r.raw, f)
		return True
	except Exception as e:
		exitScript("bad","downloadFile(): failed to download: %s"%e)

def unzipFile(zipFile,unzipTo):
	if verbose:
		print("unzipping the file '%s' to path '%s'"%(zipFile,unzipTo))
	try:
		zip_ref = zipfile.ZipFile(zipFile, 'r')
		zip_ref.extractall(unzipTo)
		zip_ref.close()
		return True
	except Exception as e:
		exitScript("bad","unzipFile(): could not unzip VirtualHub from '%s' to '%s': %s"%(zipFile,unzipTo,e))

def checkReturnCode(binfile):
	os.chmod(binfile, 755)
	command = binfile+" -v"
	process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	process.wait()
	if verbose:
		print ("checked binary '%s' with result: %i" %(binfile,process.returncode))
	return process.returncode

def tryBinaries():
	results = {"armhf": 999,"armel": 999,"32bits": 999,"64bits": 999}
	winner = 'Unknown'
	vh_files = os.listdir(tempLocation+"/VirtualHub/")

	for file in vh_files:
		if file == "startup_script" or file == "udev_conf":
			continue

		if os.path.isdir(tempLocation+"/VirtualHub/"+file):
			res = checkReturnCode(tempLocation+"/VirtualHub/"+file+"/VirtualHub")
			if res == 0:
				winner=file
			results[file] = res

	if results['armhf'] == 0 and results['armel'] == 0:
		winner = "armhf"

	if results['32bits'] == 0 and results['64bits'] == 0:
		winner = "64bits"

	fromPath = tempLocation+"/VirtualHub/"+str(winner)+"/VirtualHub"

	if winner == 'Unknown':
		exitScript("bad","found NO usable VirtualHub binary!")

	return fromPath


def checkIfVirtualhubIsRunning():
	if verbose:
		print("checking now if VirtualHub is running...")
	process = subprocess.Popen('pidof VirtualHub', shell=True, stdout=subprocess.PIPE)
	process.wait()
	if process.returncode == 0:
		i=8
		while i>0:
			print("VirtualHub is currently running, killing in %i seconds! press CTRL-C to cancel" %i)
			time.sleep(1)
			i = i -1
		if verbose:
			print("KILLING VirtualHub now..")
		kill_process = subprocess.Popen('killall VirtualHub', shell=True, stdout=subprocess.PIPE)


def whichLinuxInit():
	if verbose:
		print("try to find out which init system is running..")

	try:
		process = subprocess.Popen(['cat','/proc/1/status'], stdout=subprocess.PIPE)
		pout = process.communicate()[0]

		if 'systemd' in str(pout):
			if verbose:
				print("this system is using systemd")
			return "systemd"
	except Exception as e:
		print("whichLinuxInit(): Exception: %s"%e)

	if verbose:
		print("could not determine which init this system uses: Unknown")
	return 'Unknown'


def installInitSystemd():
	answer = input("Install VirtualHub as a service (systemd)? (Y/N) ")
	if answer == "Y" or answer == "Yes" or answer == "y" or answer == "yes" or answer == "yes":
		print("installing VirtualHub startup_script..")
		try:
			shutil.copyfile(tempLocation+"/VirtualHub/startup_script/yvirtualhub.service","/lib/systemd/system/VirtualHub.service")
			command = "systemctl enable VirtualHub.service"
			process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
			process.wait()
			if process.returncode == 0:
				print ("----------------------- startup_script installed ---------------------------")
				print ("you can control VirtualHub now with these commands:")
				print ("   service VirtualHub start|stop|restart|status")
				print ("")
				print ("if you want to disable the VirtualHub service:")
				print ("   systemctl disable VirtualHub")
				print ("----------------------------------------------------------------------------")
				return True
		except Exception as e:
			print ("WARNING: failed to move startup_script to '/lib/systemd/system/VirtualHub.service': %s"%e)
			return False



if verbose:
	print("detected OS is: %s"%myOS[0])
	print("checking the version of the installed VirtualHub binary..")

process = subprocess.Popen("VirtualHub -v", shell=True, stdout=subprocess.PIPE)
process.wait()
myVersionString = str(process.communicate()[0])

if process.returncode == 126:
	exitScript("bad","Local VirtualHub, found, but no permission to run, please give your local VirtualHub binary execute rights (chmod +x)")

if process.returncode != 0:
	if verbose:
		print("could not find a local VirtualHub installation")
	local_version = 0
else:
	try:
		regex = r"\.(\d*) \("
		match = re.search(regex, myVersionString)
		local_version = match.group(1)
		if verbose:
			print("the currently installed version of VirtualHub is: %s"%str(local_version))
		
	except Exception as e:
		exitScript("bad","checkInstalledVersion(): error parsing installed version: %s" %e)


if verbose:
	print('checking yoctopuce.com now for current version of VirtualHub..')
try:
	r = requests.get(updateCheckUrl, headers=headers)
	jsonData = r.json()
	if verbose:
		print("answer from yoctopuce.com follows, in json format:")
		print(jsonData)

	remote_version = jsonData['version']
	download_url = jsonData['link']
	if verbose:
		print("the current version from yoctopuce.com is: %s"%remote_version)
except Exception as e:
	exitScript('bad','failed to connect to yoctopuce.com, message: %s, please make sure your internet connection is OK and try again'%e)


# better output if VH is not installed yet
if local_version == 0:
	local_version_str = bcolors.WARNING+"not installed"+bcolors.ENDC
else:
	local_version_str =local_version


if(int(remote_version)!=int(local_version)):
	print(bcolors.OKGREEN+"-"*100)
	print('Installed Version:	%s'%local_version_str)
	print('Newest Version:		%s'%remote_version)
	if local_version != 0:
		print("Update available")
	print("-"*100+bcolors.ENDC)
else:
	print(bcolors.OKGREEN+"-"*100)
	print('Installed Version:	%s'%local_version_str)
	print('Newest Version:		%s'%remote_version)
	print("you have the newest version of VirtualHub")
	print("-"*100+bcolors.ENDC)
	exit(0)





local_filename = download_url.split('/')[-1]

if verbose:
	print('downloading VirtualHub from %s'%download_url)

downloadFile(download_url,tempLocation+"/VirtualHub.zip")
unzipFile(tempLocation+"/VirtualHub.zip",tempLocation+"/VirtualHub/")

if myOS[0] == 'Linux':
	checkIfVirtualhubIsRunning()
	myInit = whichLinuxInit()
	if myInit == 'systemd':
		installInitSystemd()

if fromPath=='':
	fromPath = tryBinaries()
	if verbose:
		print("found a working binary for this cpu architecture: %s"%fromPath)


# moving binary to appLocation folder
try:
	shutil.copyfile(fromPath, appLocation)
	if verbose:
		print ("%s is the best suited VirtualHub binary, lets move it to %s now" %(fromPath,appLocation))
except Exception as e:
	exitScript("bad","failed to move VirtualHub binary from %s to %s, error: %s" %(fromPath,appLocation,e))

# change permissions
try:
	os.chmod(appLocation, 755)
except Exception as e:
	exitScript("bad","failed to change permission of '%s': %s"%(appLocation,e))

# removing tmp folder and zip file
try:
	os.unlink(tempLocation+"/VirtualHub.zip")
	shutil.rmtree(tempLocation+"/VirtualHub")
	if verbose:
		print("cleaning up temporary files.. OK")
except Exception as e:
	exitScript("bad","failed to cleanup my temp files: %s" %e)


exitScript("good","VirtualHub is now installed")

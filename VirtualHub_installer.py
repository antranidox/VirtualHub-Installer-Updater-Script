#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tested with macOS 10.13.3, raspbian stretch, debian stretch
with python 2.7.x and python 3.x

Q: why not just use requests? A: because that would add another dependency
"""

script_version = "0.9.4"
import sys,os,re,time,shutil,zipfile,subprocess,ssl,string,platform
print ("welcome to the (unofficial) VirtualHub installer/updater Script v %s" %script_version)

# checking args
verbose = False
if len(sys.argv)>1:
	if sys.argv[1]=="-v":
		verbose = True
		print("verbose mode: on")


# get current OS
myOS = platform.uname()

# urllib for python2+3
if sys.version_info[0] >= 3:
	# python 3.x and up
	if verbose:
		print("this is python3 or higher, importing urlopen from urllib.request")
	from urllib.request import urlopen
else:
	# python 2.x
	if verbose:
		print("this is python 2.x, importing urlopen from urllib and urllib as urlretrieve")
	from urllib import urlopen
	import urllib as urlretrieve


# dont check ssl cert
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


# url of the virtualhub update site
yoctopuce_url = "https://www.yoctopuce.com/EN/virtualhub.php"



# same as getUrlContent but for python 2.x
def getUrlContent_M2(url):
	if verbose:
		print("using methode2 to get url")
	try:
		with urlopen(url,timeout=15,context=ctx) as reado:
			s = reado.read()
		return str(s)
	except Exception as e:
		print("failed to getUrl '%s' with both methodes: %s"%(url,e))
		return False

# get html-code of url (python 3.x version)
def getUrlContent(url):
	if verbose:
		print("using methode1 to get url")
	try:
		s = urlopen(url,context=ctx).read()
		return str(s)
	except Exception as e:
		print(e)
		m2 = getUrlContent_M2(url)
		if m2:
			return m2
		else:
			return False


# execute VirtualHub binary and check returncode
def checkVHreturnCode(binfile):
	print ("checking %s now ..." %binfile)
	os.chmod(binfile, 755)
	command = binfile+" -v"
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	process.wait()
	return process.returncode

# gets the zip filename from html-source via regex
# returns something similar to this: VirtualHub.linux.29681.zip
def pageToZip(currentPlatform):
	try:
		html = getUrlContent(yoctopuce_url)
		if not html:
			print("Failed to extract zip filename from url")
			return False
		regex = r"(VirtualHub\."+currentPlatform+"\.\d*\.zip)"
		match = re.search(regex, html)
		if verbose:
			print("searching in source of '"+yoctopuce_url+"' for VirtualHub."+currentPlatform)
			print("found match: %s" %match.group(1))
		return match.group(1)
	except Exception as e:
		print ("Error while searching for zipFile: %s" %e)
		return False

# check virtualhub version on website
def checkWebsiteVersion(myOS):
	try:
		html = getUrlContent(yoctopuce_url)
		if not html:
			print("Failed to extract newest VH version from webpage")
			return False
		regex = r"VirtualHub\.linux\.(\d*)\.zip" # would be better to search for specific plattform!
		match = re.search(regex, html)
		if verbose:
			print("searching in source of '"+yoctopuce_url+"' for VirtualHub Version")
			print("found versions match: %s" %match.group(1))
		return match.group(1)
	except Exception as e:
		print ("Error while searching for newest version: %s" %e)
		return False

# check if virtualhub is installed and which version
def checkInstalledVersion(myOS):
	if myOS[0] == "Windows":
		print("Sorry, update is not yet implemented for Windows")
		return "00000"

	if verbose:
		print("trying to open VirtualHub with the -v command, to get Version of current installed VirtualHub")

	command = "VirtualHub -v"
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	process.wait()
	myVersionString = str(process.communicate()[0])
	
	if process.returncode == 126:
		print("Failed to start VirtualHub, please give the VirtualHub binary chmod +x / execute rights")
		return False

	if process.returncode != 0:
		if verbose:
			print("Failed to find VirtualHub binary, got errorcode: "+str(process.returncode))
		return False

	try:
		regex = r"\.(\d*) \("
		match = re.search(regex, myVersionString)
		if verbose:
			print("Nice! We got a installed VirtualHub, Version: "+str(match.group(1)))
		return match.group(1)
	except Exception as e:
		print ("Error while parsing installed Version: %s" %e)
		return False

# download VirtualHub ZIP file from website
def downloadVH(url,destination):
	print("downloading file from %s to %s" %(url,destination))
	try:
		urlretrieve.urlretrieve(url, destination,context=ctx)
	except Exception as e:
		try:
			with urlopen(url, context=ctx) as u, open(destination, 'wb') as f:
				f.write(u.read())
		except Exception as e2:
			print("failed to download VirtualHub, error: %s" %e2)


# synology specific function: searches for libusb in given path
def findFile(where,filename='libusb-1.0.so.0'):
	if verbose:
		print("searching for %s in %s" %(filename,where))
	process = subprocess.Popen(['find', where, '-name', filename], stdout=subprocess.PIPE)
	process.wait()
	if process.returncode == 0:
		return process.communicate()[0]

	if verbose:
		print("Failed to find %s in %s -- got errorcode: %s" %(filename,where,str(process.returncode)))
	return "not found"


# synology specific function: searches possible libusb locations, gives back THE location (or false)
def synologyGetLibusb(libusbLoc):
	if not os.path.isfile(libusbLoc):
		print (libusbLoc+" not found, i will try to locate it in another location now..")
		# "find /volume*/@appstore/ -name libusb-1.0.so.0" doesn't work idk why

		# iterate through volume-names (volume1,volume2,volume3.. etc)
		for vn in xrange(1,10):
			if os.path.exists('/volume%i/@appstore'%vn):
				libfile = findFile('/volume%i/@appstore'%vn)
				print ("found a libusb-1.0.so.0 on "+str(libfile))
				return str(libfile.rstrip())
			if os.path.exists('/volume%i/@entware'%vn):
				libfile = findFile('/volume%i/@entware'%vn)
				print ("found a libusb-1.0.so.0 on "+str(libfile))
				return str(libfile.rstrip())

		# nothing found
		print("i searched everywhere, found no libusb-1.0.so.0! please install Plex Package from Synology Package Center")
		print("or move a compatible libusb-1.0.so.0 file to /lib/libusb-1.0.so.0, important: libusb version MUST be 1.0.9")
		return False
	# return file location
	if verbose:
		print("found libusb-1.0.so.0 here: %s" %libusbLoc)
	return libusbLoc

# linux specific function, checks which init system is beeing used: systemd,initv or unknown
def whichLinuxInit():
	process = subprocess.Popen(['pidof', ' /sbin/init'], stdout=subprocess.PIPE)
	myInit = process.communicate()[0]
	if myInit == 1:
		if verbose:
			print("this system is using sysvinit")
		return "sysvinit"

	process = subprocess.Popen(['pidof', 'systemd'], stdout=subprocess.PIPE)
	myInit = process.communicate()[0]
	if myInit == 1:
		if verbose:
			print("this system is using systemd")
		return "systemd"

	if verbose:
		print("could not determine which init this system uses: Unknown")
	return "Unknown"


# checking VirtualHub versions local VS newest (web)
webVersion = checkWebsiteVersion(myOS)
myVersion = checkInstalledVersion(myOS)

# VirtualHub not found or not installed
if not myVersion:
	print("VirtualHub is not installed, installing it now")
else:
	# VirtualHub up to date, do not need update
	if int(webVersion)==int(myVersion):
		print("Installed VirtualHub is the newest available version (local: %s / web: %s)"%(myVersion,webVersion))
		sys.exit()
	else:
		# VirtualHub update available
		print("Installed VirtualHub: %s / Newest Version (web): %s)"%(myVersion,webVersion))

# checking if VirtualHub is running, kill it if its running
process = subprocess.Popen('pidof VirtualHub', shell=True, stdout=subprocess.PIPE)
process.wait()
if process.returncode == 0:
	kill_process = subprocess.Popen('killall VirtualHub', shell=True, stdout=subprocess.PIPE)


# setting some platform specific stuff like /tmp folder and binary location
if myOS[0] == "Linux":
	print ("checking yoctopuce.com for VirtualHub for "+myOS[0])
	zipFile = pageToZip('linux')

	# need the FULL uname string to find synology, that os.uname() will no provide
	# ex: Linux LeSource 3.2.40 #22259 SMP Mon Oct 2 02:40:53 CST 2017 armv7l GNU/Linux synology_armadaxp_ds214
	process = subprocess.Popen(['uname', '-a'], stdout=subprocess.PIPE)
	myOSa = process.communicate()[0]

	# synology specific
	if "synology" in myOSa:
		print("System: Synology")
		libusbLoc = '/lib/libusb-1.0.so.0'
		synoLibusb = synologyGetLibusb(libusbLoc)

		if synoLibusb == True:
			if synoLibusb!=libusbLoc:
				try:
					shutil.copyfile(synoLibusb, libusbLoc)
				except Exception as e:
					print('could not copy "%s" to "%s": %s'%(synoLibusb, libusbLoc, e))
					print("please try to copy it manually and start this script again")
					sys.exit(1)
			else:
				print ("could not be installed, because there is no such file /lib/libusb-1.0.so.0")
				sys.exit(1)
			

	# linux specific
	appLocation = "/usr/sbin/VirtualHub"
	tempLocation = "/tmp"
elif myOS[0] == "Darwin":
	print ("checking yoctopuce.com for VirtualHub for macOS")
	zipFile = pageToZip('osx')
	appLocation = "/usr/local/bin/VirtualHub"
	tempLocation = "/tmp"
	fromPath = tempLocation+"/VirtualHub/VirtualHub"
	winner = "VirtualHub"
elif myOS[0] == "Windows":
	print ("checking yoctopuce.com for VirtualHub for "+myOS[0])
	zipFile = pageToZip('windows')
	windowsDesktopPath = os.path.join(os.environ["HOMEPATH"], "Desktop")
	appLocation = windowsDesktopPath+"\\VirtualHub"
	tempLocation = windowsDesktopPath
	fromPath = tempLocation+"/VirtualHub"
	winner = "VirtualHub"
else:
	print ("unknown os: %s" %myOS[0])
	sys.exit(127)

if not zipFile:
	print ("sorry, didnt find zipfile on webpage!")
	sys.exit(1)

# download VirtualHub.zip file
download_url = "https://www.yoctopuce.com/FR/downloads/"+zipFile
downloadVH(download_url,tempLocation+"/VirtualHub.zip")

# unzip  VirtualHub.zip file
try:
	zip_ref = zipfile.ZipFile(tempLocation+"/VirtualHub.zip", 'r')
	zip_ref.extractall(tempLocation+"/VirtualHub/")
	zip_ref.close()
except Exception as e:
	print ("could not unzip VirtualHub: %s" %e)
	sys.exit(1)


# linux specific: iterate over all binaries, check which one we can use on the current platform/architecture
# this is just try and error, using the exit code
if myOS[0] == "Linux":
	results = {"armhf": 999,"armel": 999,"32bits": 999,"64bits": 999}
	winner = 'Unknown'
	vh_files = os.listdir(tempLocation+"/VirtualHub/")

	for fina in vh_files:
		if fina == "startup_script" or fina == "udev_conf":
			continue

		if os.path.isdir(tempLocation+"/VirtualHub/"+fina):
			res = checkVHreturnCode(tempLocation+"/VirtualHub/"+fina+"/VirtualHub")
			if res == 0:
				winner=fina
			results[fina] = res

	if results['armhf'] == 0 and results['armel'] == 0:
		winner = "armhf"

	if results['32bits'] == 0 and results['64bits'] == 0:
		winner = "64bits"

	fromPath = tempLocation+"/VirtualHub/"+str(winner)+"/VirtualHub"

	if winner == 'Unknown':
		print("found NO usable VirtualHub binary!")
		print(results)
		sys.exit(1)


# moving binary to appLocation -->  /bin folder
try:
	shutil.copyfile(fromPath, appLocation)
	print ("%s is the best suited VirtualHub binary, lets move it to %s now" %(winner,appLocation))
except Exception as e:
	print ("failed to move VirtualHub binary from %s to %s, error: %s" %(fromPath,appLocation,e))
	sys.exit(1)


# linux specific: ask if want to install init script, to autostart VirtualHub after boot & run as service
if myOS[0] == "Linux":
	myInit = whichLinuxInit()
	if myInit == 'sysvinit':
		print("sysvinit startscript support not yet implemented in this script, please copy the startscript manualy")

	if myInit == 'systemd':
		answer = raw_input("Install VirtualHub as a service (systemd)? (Y/N) ")
		if answer == "Y" or answer == "Yes" or answer == "y" or answer == "yes" or answer == "yes":
			print("installing VirtualHub startup_script..")
			try:
				fromPath = tempLocation+"/VirtualHub/"+winner+"/VirtualHub"
				os.rename(tempLocation+"/VirtualHub/startup_script/yvirtualhub.service","/lib/systemd/system/VirtualHub.service")
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
			except Exception as e:
				print ("failed to move startup_script to /lib/systemd/system/VirtualHub.service")
				sys.exit(1)

# mac specific chmod +x VirtualHub binary
if myOS[0] == "Darwin" or myOS[0] == "Linux":
	try:
		print("making %s executable"%appLocation)
		os.chmod(appLocation, 755)
	except Exception as e:
		print("############### warning --> failed to chmod +x the VirtualHub binary: %s" %e)
		print("you may need to execute this manualy: chmod +x "+appLocation)


# windows specific
if myOS[0] == "Windows":
	print("VirtualHub is now on your desktop, i will open it for you now")
	os.system(appLocation)


# cleaning up, removing tmp folder and zip file
try:
	os.unlink(tempLocation+"/VirtualHub.zip")
	shutil.rmtree(tempLocation+"/VirtualHub")
except Exception as e:
	print("############### warning --> failed to cleanup some files: %s" %e)


# success
print ("------------------------------ SUCCESS -------------------------------------")
print ("")
print("                    you can use VirtualHub now :) ")
print ("")
print ("----------------------------------------------------------------------------")

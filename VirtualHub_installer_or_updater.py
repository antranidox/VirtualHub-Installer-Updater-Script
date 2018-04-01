#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tested with macOS 10.13.3, raspbian stretch, debian stretch
"""

# check dependency: requests
import imp
try:
    imp.find_module('requests')
    found = True
except ImportError:
	import sys
	print("")
	print("")
	print ("------------------------------ REQUIREMENT -------------------------------------")
	print ("                    please install requests by typing:				            ")
	print ("                          pip install requests			                     	")
	print ("                  after that, execute this script again						    ")
	print ("--------------------------------------------------------------------------------")
	print("")
	print("")
	sys.exit()

script_version = "0.8"
import sys,os,re,json,time,requests,shutil,zipfile,subprocess


yoctopuce_url = "http://www.yoctopuce.com/EN/virtualhub.php"
myOS = os.uname()

# execute VirtualHub binary and check returncode
def checkVHreturnCode(binfile):
	print ("checking %s now ..." %binfile)
	os.chmod(binfile, 755)
	command = binfile+" -v"
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	process.wait()
	return process.returncode


# returns something similar to this: VirtualHub.linux.29681.zip
def pageToZip(plattform):
	try:
		r = requests.get(yoctopuce_url)
		regex = r"(VirtualHub\."+plattform+"\.\d*\.zip)"
		match = re.search(regex, r.text)
		return match.group(1)
	except Exception as e:
		print ("error while searching for zipFile: %s" %e)
		return False

# check virtualhub version on website
def checkWebsiteVersion():
	try:
		r = requests.get(yoctopuce_url)
		regex = r"VirtualHub\.linux\.(\d*)\.zip"
		match = re.search(regex, r.text)
		return match.group(1)
	except Exception as e:
		print ("error while searching for newest version: %s" %e)
		return False

def checkInstalledVersion():
	command = "VirtualHub -v"
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	process.wait()
	myVersionString = str(process.communicate()[0])
	if process.returncode != 0:
		return False

	try:
		regex = r"\.(\d*) \("
		match = re.search(regex, myVersionString)
		return match.group(1)
	except Exception as e:
		print ("error while parsing local version: %s" %e)
		return False

# download VirtualHub ZIP file from website
def downloadVH(url,destination):
	print("downloading from %s to destination %s" %(url,destination))
	response = requests.get(url, stream=True)
	with open(destination, 'wb') as out_file:
	    shutil.copyfileobj(response.raw, out_file)
	del response


# checking versions
webVersion = checkWebsiteVersion()
myVersion = checkInstalledVersion()

if not myVersion:
	print("VirtualHub is not installed, installing it now")
else:
	if int(webVersion)==int(myVersion):
		print("Installed VirtualHub is the newest available version (local: %s / web: %s)"%(myVersion,webVersion))
		sys.exit()


# setting some plattform specific stuff
if myOS[0] == "Linux":
	print ("checking yoctopuce.com for VirtualHub for "+myOS[0])
	zipFile = pageToZip('linux')
	appLocation = "/usr/sbin/VirtualHub"
	tempLocation = "/tmp"
elif myOS[0] == "Darwin":
	print ("checking yoctopuce.com for VirtualHub for "+myOS[0])
	zipFile = pageToZip('osx')
	appLocation = "/usr/local/bin/VirtualHub"
	tempLocation = "/tmp"
	fromPath = tempLocation+"/VirtualHub/VirtualHub"
	winner = "VirtualHub"
else:
	print ("unknown os: %s" %myOS[0])
	sys.exit()

if not zipFile:
	print ("sorry, didnt find no zipfile")
	sys.exit()

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
	sys.exit()


# [LINUX] iterate over all binaries, check which one we can use
if myOS[0] == "Linux":
	results = {"armhf": 999,"armel": 999,"32bits": 999,"64bits": 999}
	winner = False
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

	fromPath = tempLocation+"/VirtualHub/"+winner+"/VirtualHub"

	if not winner:
		print("found NO usable VirtualHub binary!")
		print(results)
		sys.exit()


# moving binary to appLocation -->  /bin folder
print ("%s is the best suited VirtualHub binary, lets move it to %s now" %(winner,appLocation))

try:
	os.rename(fromPath, appLocation)
except Exception as e:
	print ("failed to move VirtualHub binary from %s to %s" %(fromPath,appLocation))
	sys.exit()


if myOS[0] == "Linux":
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
			sys.exit()

# [MAC] chmod +x VirtualHub binary
if myOS[0] == "Darwin":
	try:
		print("making %s executable"%appLocation)
		os.chmod(appLocation, 755)
	except Exception as e:
		print("############### warning --> failed to chmod +x the VirtualHub binary: %s" %e)
		print("you may need to execute this manualy: chmod +x "+appLocation)

# cleaning up
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

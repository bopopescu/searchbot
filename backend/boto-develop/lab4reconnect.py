# Python Browser Lab 4
# Group g326-1-019 [Gwyneth, David, Gligor]
# Last modified December 3, 2016

### TO RUN: ###
# need to have proper credential file as 'credentials.csv'
# like the one provided by AWS for a set up user
# user with these credentials must have admin privileges (to install packages)
# add permissions (Administrator) via AWS website > IAM > user > user_name
#
# IP addr will be written in info.txt
###
try:
	import boto.ec2
	import string, random
	import subprocess, os
	import time
except ImportError, e:
	print "Failed to import a library in lab4reconnect.py"
	print e
	exit()


dryrun = False

# DOCUMENTATION help with boto.ec2 objects:
# http://boto.cloudhackers.com/en/latest/ec2_tut.html
# http://boto.readthedocs.io/en/latest/ref/ec2.html

# read credentials from file
keyfile = open("credentials.csv", 'r')
keys = keyfile.readline() # first line is useless, contains headers
keys2 = keyfile.readline() # contains the actual keys we need
sep_keys = str.split(keys2, ',') # extract the keys we need
for i in range(0,len(sep_keys)):
	sep_keys[i] = sep_keys[i].strip() # remove \r \n from end
keyfile.close()

# read instance ID from file
infotxt = open('info.txt', 'r')
insta_id = infotxt.readline().strip()
infotxt.close()


# connect_to_region(region_name, aws_access, aws_secret_access)
conn = boto.ec2.connect_to_region("us-east-1", aws_access_key_id=sep_keys[1], aws_secret_access_key=sep_keys[2])
# get all the instances, the one we just created should be the first one
if insta_id:
	reservations = conn.get_all_reservations([insta_id])
else:
	reservations = conn.get_all_reservations()
insta = reservations[0].instances[0]

# wait for instance to boot and stabilize
print "instance is", insta.state
while insta.state != "running" or insta.ip_address == None or insta.public_dns_name == None:
	print "waiting for instance to finish booting..."
	time.sleep(10)
print "instance booted!", insta.state, "!"


# save the IP address & DNS name to info file
infotxt = open('info.txt', 'w')
infotxt.write(insta.id + '\n')
infotxt.write(insta.ip_address + '\n')
infotxt.write(insta.public_dns_name + '\n')
infotxt.close()

print "Instance", insta.id, "is", insta.state
print "public IP is:", insta.ip_address
print "public DNS is:", insta.public_dns_name


# SCP to transfer files to instance
# SSH to install the necessary packages and launch SearchBot
# do the ssh stuff
print "\nSearchBot INSTALLATION: (this may take a while)\n"
keypem = insta.key_name + '.pem'
filepath = os.path.abspath('frontend.tar.gz') # tar file containing all required files
hostname = "ubuntu@" + str(insta.ip_address)

print "transferring front-end files"
subprocess.call(['scp', '-o', 'StrictHostKeyChecking=no', '-i', keypem, filepath, hostname + ':~/' ])

subprocess.call(['ssh', '-i', keypem, '-t', '-t', hostname, "'ls'"])
subprocess.call(["ls"])

#using subprocess.call(ssh [user]@[server] '[command]')
# tar -zxvf frontend.tar.gz
# cd frontend
# bash lab4_remote_lib_installer.sh
exit()




print "connecting to", hostname
sshProcess = subprocess.Popen(['ssh', '-i', keypem, '-t', '-t', hostname], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, bufsize=-1)

print "unpacking front-end files"
sshProcess.stdin.write("tar -zxvf frontend.tar.gz \n")
time.sleep(3)



# DONE IN REMOTE BASH SCRIPT
# print "installing dependent frameworks"
# sshProcess.stdin.write("sudo apt-get --assume-yes update\n")
# sshProcess.stdin.write("sudo apt-get --assume-yes install python-pip\n")
# sshProcess.stdin.write("sudo apt-get --assume-yes install python-dev\n")

# print "installing numpy"
# sshProcess.stdin.write("sudo pip install numpy\n")

# print "installing bottle"
# sshProcess.stdin.write("sudo pip install bottle\n")

# print "installing beaker"
# sshProcess.stdin.write("sudo pip install beaker\n")

# print "installing oauth2client"
# sshProcess.stdin.write("sudo pip install oauth2client\n")

# print "installing googleapiclient"
# sshProcess.stdin.write("sudo pip install google-api-python-client\n")
# DONE IN REMOTE BASH SCRIPT


# RUN SearchBot remote server
print "running 'SearchBot.py' (in background)"
#sshProcess = subprocess.Popen(['ssh', '-i', keypem, '-t', '-t', hostname], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, bufsize=-1)
sshProcess.stdin.write("cd frontend\n")
time.sleep(1)
sshProcess.stdin.write("tmux\n")
time.sleep(1)
sshProcess.stdin.write("sudo python SearchBot.py\n")
time.sleep(2)
sshProcess.stdin.write("^b\n")
sshProcess.stdin.write("d\n")
time.sleep(1)

print "exiting ssh session"
sshProcess.stdin.write("exit")
sshProcess.stdin.close()

print "\nstart_searchbot is COMPLETE\n"
print "Instance", insta.id, "is", insta.state
print "public IP is:", insta.ip_address
print "public DNS is:", insta.public_dns_name

exit()


# ACCESS INSTANCE via insta.key_name and insta.ip_address, default username is ubuntu
# $ ssh -i key_pair.pem ubuntu@<PUBLIC-IP-ADDRESS>

# copy file from local machine to AWS instance using
# $ scp -i key_pair.pem <FILE-PATH> ubuntu@<PUBLIC-IP-ADDRESS>:~/<REMOTE-PATH>

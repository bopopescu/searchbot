# Python Browser Lab 4
# Group g326-1-019 [Gwyneth, David, Gligor]
# Last modified December 4, 2016

### TO RUN: ###
# Must have proper credential file as 'credentials.csv' provided by AWS for a set up user
# User needs to have admin privileges (to install packages)
# Add permissions (Administrator) via AWS website > IAM > user > 'user_name'
#
# instance-ID, IP addr, DNS nme will be written in info-g019.txt
### ###
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
infotxt = open('info-g019.txt', 'r')
insta_id = infotxt.readline().strip()
infotxt.close()


# connect_to_region(region_name, aws_access, aws_secret_access)
conn = boto.ec2.connect_to_region("us-east-1", aws_access_key_id=sep_keys[1], aws_secret_access_key=sep_keys[2])
# get all the instances, the one we just created should be the first one
if insta_id:
	reservations = conn.get_all_reservations([insta_id]) # get instance we just created
else:
	reservations = conn.get_all_reservations()
insta = reservations[0].instances[0]

# wait for instance to boot and stabilize
print "instance is", insta.state
for i in range(30):
	if insta.state == "running" and insta.ip_address != None and insta.public_dns_name != None:
		break
	print "waiting for instance to finish booting..."
	time.sleep(10)
print "instance booted!", insta.state, "!"


# save the insta-ID, IP address, and DNS name to info-g019 file
print "Writing to info-g019.txt"
infotxt = open('info-g019.txt', 'w')
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
#using subprocess.call(ssh [user]@[server] [command; command 'args'])
# ex: ssh blah_server "ls some_folder; ./someaction.sh 'some params'; pwd; ./some_other_action 'other params';"

print "\nSearchBot library INSTALLATION: (this may take a while)"
keypem = insta.key_name + '.pem'
filepath = os.path.abspath('frontend.tar.gz') # tar file containing all required files
hostname = "ubuntu@" + str(insta.ip_address)

print "\ntransferring front-end files"
subprocess.call(['scp', '-o', 'StrictHostKeyChecking=no', '-i', keypem, filepath, hostname + ':~/' ])

print "\nconnecting to", hostname
subprocess.call(['ssh', '-i', keypem, hostname, 'whoami; pwd'])

print "\nunpacking front-end files"
time.sleep(1)
subprocess.call(['ssh', '-i', keypem, hostname, 'tar -zxvf frontend.tar.gz'])

print "\ninstalling required libraries on remote machine"
time.sleep(1)
subprocess.call(['ssh', '-i', keypem, hostname, 'cd frontend; bash lab4_remote_lib_installer.sh'])

# RUN SearchBot remote server
print "\nrunning 'SearchBot.py' (remotely)"
time.sleep(1)
sshProcess = subprocess.Popen(['ssh', '-i', keypem, '-t', '-t', hostname, 'cd frontend; tmux new -s Sbot'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, bufsize=-1)
sshProcess.stdin.write("sudo python SearchBot.py\n")
time.sleep(1) # wait for things to stabilize
sshProcess.stdin.write("^b\n")
sshProcess.stdin.write("d\n")
time.sleep(0.5) # wait for things to stabilize

print "exiting ssh session"
sshProcess.stdin.write("exit")

print "\nstart_searchbot is COMPLETE\n"
print "Instance", insta.id, "is", insta.state
print "public IP is:", insta.ip_address
print "public DNS is:", insta.public_dns_name

exit()


# ACCESS INSTANCE via insta.key_name and insta.ip_address, default username is ubuntu
# $ ssh -i key_pair.pem ubuntu@<PUBLIC-IP-ADDRESS>

# copy file from local machine to AWS instance using
# $ scp -i key_pair.pem <FILE-PATH> ubuntu@<PUBLIC-IP-ADDRESS>:~/<REMOTE-PATH>

# Python Browser Lab 4
# Group g326-1-019 [Gwyneth, David, Gligor]
# Last modified December 3, 2016

try:
	import boto.ec2
	import string, random
	import subprocess
	import os, time
except ImportError, e:
	print "Failed to import a library in lab4stop.py"
	print e
	exit()


dryrun = False

# DOCUMENTATION help:
# http://boto.cloudhackers.com/en/latest/ec2_tut.html
# http://boto.readthedocs.io/en/latest/ref/ec2.html


# read credentials from file
print "stop_searchbot is RUNNING"
print "STOP remote process:\n"
keyfile = open("credentials.csv", 'r')
keys = keyfile.readline() # first line is useless, contains headers
keys2 = keyfile.readline() # contains the actual keys we need
sep_keys = str.split(keys2, ',') # get what we need
for i in range(0,len(sep_keys)):
	sep_keys[i] = sep_keys[i].strip() # remove \r \n from end
keyfile.close()

# read instance ID from file
if os.path.exists('info.txt'):
	infotxt = open('info.txt', 'r')
	insta_id = infotxt.readline().strip()
	# can also read public IP and DNS
	infotxt.close()
else:
	insta_id = ""


# connect_to_region(region_name, aws_access, aws_secret_access)
conn = boto.ec2.connect_to_region("us-east-1", aws_access_key_id=sep_keys[1], aws_secret_access_key=sep_keys[2])
if insta_id:
	reservations = conn.get_all_reservations([insta_id])
else:
	reservations = conn.get_all_reservations()
insta = None
# get the instance object below and assign it to 'insta'
if reservations == None or len(reservations) == 0:
	print 'No reservations found, exiting'
	exit()
elif len(reservations[0].instances) == 0:
	print 'No instances found in reservation, exiting'
	exit()
else:
	insta = reservations[0].instances[0]


# END the remote SearchBot server via SSH
key_name = insta.key_name
keypem = key_name + '.pem'
security_group_name = key_name + "_csc326-group019"
hostname = "ubuntu@" + str(insta.ip_address)
#ssh in
#tmux attach
#^c (twice)
print "connecting to", hostname
sshProcess = subprocess.Popen(['ssh', '-i', keypem, '-t', '-t', hostname], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, bufsize=-1)

print "ending 'SearchBot.py'"
sshProcess.stdin.write("tmux attach\n")
time.sleep(1)
sshProcess.stdin.write("^c\n") # terminate SearchBot
sshProcess.stdin.write("^c\n")
time.sleep(1)
sshProcess.stdin.write("exit\n") # terminate tmux
print "exiting ssh session"
#sshProcess.stdin.write("exit\n")
sshProcess.stdin.close()


# SHUTDOWN the instance
# and delete the AWS key_pair, AWS security_groupo, and .pem file
print "SHUTDOWN instance", insta.id, ":"
if(insta.state == "running"):
	insta.stop() # takes time!!
	while (insta.state != "stopped"):
		print "waiting for instance to stop..."
		time.sleep(10)
	print insta.state

if (insta.state == 'stopped'):
	insta.terminate() # takes time!!!
	while (insta.state != "terminated"):
		print "waiting for instance to terminate..."
		time.sleep(10)
	print insta.state
else:
	print "Instance already terminated"

conn.delete_security_group(security_group_name)
conn.delete_key_pair(key_name)
if os.path.exists(keypem):
	os.remove(keypem)
if exists('info.txt'):
	infotxt = open('info.txt', 'a')
	infotxt.write("INVALID")
	infotxt.close()

print "stop_searchbot is COMPLETE"
exit()

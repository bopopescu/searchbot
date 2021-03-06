# Python Browser Lab 4
# Group g326-1-019 [Gwyneth, David, Gligor]
# Last modified December 4, 2016

###########################################
# INSTANCE ID READ FROM info-g019.txt !!! #
###########################################

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
print "stop_searchbot is RUNNING\n"
print "STOPPING remote process:\n"
keyfile = open("credentials.csv", 'r')
keys = keyfile.readline() # first line is useless, contains headers
keys2 = keyfile.readline() # contains the actual keys we need
sep_keys = str.split(keys2, ',') # get what we need
for i in range(0,len(sep_keys)):
	sep_keys[i] = sep_keys[i].strip() # remove \r \n from end
keyfile.close()

# read instance ID from file
if os.path.exists('info-g019.txt'):
	infotxt = open('info-g019.txt', 'r')
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
#^c
print "connecting to", hostname
print "ending 'SearchBot.py'"
time.sleep(0.5)
subprocess.call(['ssh', '-i', keypem, hostname, 'tmux kill-session -t Sbot'])
print "exiting ssh session"


# SHUTDOWN the instance
# and delete the AWS key_pair, AWS security_groupo, and .pem file
print "SHUTDOWN instance", insta.id, ":"
if(insta.state == "running"):
	insta.stop() # takes time!!
	for i in range(6):
		print "waiting for instance to stop..."
		if insta.state == "stopped":
			break
		time.sleep(10)

time.sleep(5) # wait for things to stabilize

exit()

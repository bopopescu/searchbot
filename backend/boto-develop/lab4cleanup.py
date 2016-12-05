# stop# Python Browser Lab 4
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


# get key names
key_name = insta.key_name
keypem = key_name + '.pem'
security_group_name = key_name + "_csc326-group019"
hostname = "ubuntu@" + str(insta.ip_address)


# SHUTDOWN the instance
# and delete the AWS key_pair, AWS security_groupo, and .pem file
print "instance is", insta.state
if(insta.state != "stopped"):
	for i in range(30):
		print "waiting for instance to stop..."
		if insta.state == "stopped":
			break
		time.sleep(10)
	print insta.state

if (insta.state == 'stopped'):
	insta.terminate() # takes time!!!
	for i in range(30):
		print "waiting for instance to terminate..."
		if insta.state == "terminated":
			break
		time.sleep(10)
	print insta.state
else:
	print "Instance already terminated"

print "cleaning up AWS objects"
time.sleep(10) # wait for things to stabilize
conn.delete_security_group(security_group_name)
time.sleep(5) # wait for things to stabilize
conn.delete_key_pair(key_name)

print "cleaning up local files"
if os.path.exists(keypem):
	os.remove(keypem)
if os.path.exists('info-g019.txt'):
	infotxt = open('info-g019.txt', 'a')
	infotxt.write("INVALID")
	infotxt.close()

print "\nstop_searchbot is COMPLETE"
exit()

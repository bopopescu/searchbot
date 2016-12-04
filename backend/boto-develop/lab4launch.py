# Python Browser Lab 4
# Group g326-1-019 [Gwyneth, David, Gligor]
# Last modified December 3, 2016

### TO RUN: ###
# Must have proper credentials file named 'credentials.csv'
# provided by AWS website (aws.amazon.com).
# Also the user must have Administrator permissions, so that
# we may install required packages.
# Add via AWS website > IAM > user > user_name
#
# IP addr will be written in info.txt
###
try:
	import boto.ec2
	import string, random
	import subprocess
	import time
except ImportError, e:
	print "Failed to import a library in lab4launc.py"
	print e
	exit()


dryrun = False

# DOCUMENTATION help with boto.ec2 objects:
# http://boto.cloudhackers.com/en/latest/ec2_tut.html
# http://boto.readthedocs.io/en/latest/ref/ec2.html

# read credentials from file
print "start_searchbot is RUNNING"
keyfile = open("credentials.csv", 'r')
keys = keyfile.readline() # first line is useless, contains headers
keys2 = keyfile.readline() # contains the actual keys we need
sep_keys = str.split(keys2, ',') # get what we need
for i in range(0,len(sep_keys)):
	sep_keys[i] = sep_keys[i].strip() # remove \r \n from end
keyfile.close()


print "CONNECT to AWS instance:\n"
print "create keypair, security group, and info.txt"
# connect_to_region(region_name, aws_access, aws_secret_access)
conn = boto.ec2.connect_to_region("us-east-1", aws_access_key_id=sep_keys[1], aws_secret_access_key=sep_keys[2])


# create random key pair name and save the key pair
key_name = ""
for i in range(0,8):
	key_name = key_name + random.choice(string.letters)
# boto.ec2.create_key_pair(key_name, dry_run=True)
key_pair = conn.create_key_pair(key_name, dry_run=dryrun)
# boto.ec2.keypair.KeyPair.save(dir_path)
key_pair.save('./') # must save in this same directory


# create security group with random name and authorize proper ports/protocols
security_group_name = key_name + "_csc326-group019"
# boto.ec2.create_security_group(name, description, vpc_id=None, dry_run=False)
security_group = conn.create_security_group(security_group_name, 'secure group of searchbot group019', dry_run=dryrun)
# authorize(ip_protocol=None, from_port=None, to_port=None, cidr_ip=None, src_group=None, dry_run=False)
security_group.authorize('icmp', -1, -1, '0.0.0.0/0', dry_run=dryrun) #SSH
security_group.authorize('tcp', 22, 22, '0.0.0.0/0', dry_run=dryrun) #TCP
security_group.authorize('tcp', 80, 80, '0.0.0.0/0', dry_run=dryrun) #HTTP


# create instance on AWS
# conn.run_instances('<ami-image-id>', key_name='myKey', instance_type='c1.xlarge', security_groups=['your-security-group-here'])
reservation = conn.run_instances('ami-8caa1ce4', key_name=key_name, instance_type='t1.micro', security_groups=[security_group_name], dry_run=dryrun)
insta = reservation.instances[0]
# To find a free Micro connection in us-east-1 look at
# http://cloud-images.ubuntu.com/releases/14.04.1/release-20140927
# ex: 64bit ebs
# ec2-run-instances ami-8caa1ce4 -t t1.micro --region us-east-1 --key ${EC2_KEYPAIR_US_EAST_1}

# save the instanceID to info file
time.sleep(1)
infotxt = open('info.txt', 'w')
infotxt.write(insta.id + '\n')
infotxt.close()

# while (insta.ip_address == None or insta.public_dns_name == None):
# 	print "waiting for instance to boot..."
# 	time.sleep(5)
# print "instance ready!"

exit()

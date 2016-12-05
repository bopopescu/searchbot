#!/bin/bash

# check if credentials.csv file exists in this directory
if [ ! -e credentials.csv ] ; then
	echo "credentials.csv was not found in the current directory"
fi

# set up the AWS instance
python lab4launch.py

# install libraries, run SearchBot on remote instance
python lab4reconnect.py

echo -n ">> hit [ENTER] enter to exit <<"
read end # Waits for user to press enter to terminate script

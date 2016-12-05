#!/bin/bash

# check if credentials.csv file exists in this directory
if [ ! -e credentials.csv ] ; then
	echo "credentials.csv was not found in the current directory"
fi

# stop SearchBot on remote instance, close down that instance
python lab4stop.py

# clean up created files and AWS objects (keypair, secure group)
python lab4cleanup.py

echo -n "\n>> hit enter to exit <<"
read end # Waits for user to press enter to terminate script

#!/bin/bash

echo -n "What is the file name: "
read FILENAME

if [ -e "$FILENAME" ] ; then
	echo "file exists"
else
	echo "No such file exists in the current directory"
fi

# don't know how to check if file DOES NOT EXIST?
echo -n "What's another file name? "
read FILE2
#credentials.csv
if [ ! -e "$FILE2" ] ; then
	echo "$FILE2 was not found in current directory"
fi

echo -n ">> hit [ENTER] to exit <<"
read end # wait for user input to terminate

#!/bin/bash

# check if credentials.csv file exists in this directory
if [ -e credentials.csv ] ; then
	python lab4launch.py
	python lab4reconnect.py
else
	echo "credentials.csv was not found in the current directory"
fi

# filename= *.pem
# while read -r line
# do
#     name="$line"
#     echo "Name read from file - $name"
# done < "$filename"
#ssh -i *.pem ubuntu@
#sudo pip install boto

echo -n "\n>> hit [ENTER] enter to exit <<"
read end # Waits for user to press enter to terminate script

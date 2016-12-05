#!/bin/bash

echo ""
echo "installing dependent frameworks"
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
sudo apt-get --assume-yes update
sudo apt-get --assume-yes install python-pip
sudo apt-get --assume-yes install python-dev

echo "~~~~~~~~~~~~~~~~~"
echo "installing numpy"
echo "~~~~~~~~~~~~~~~~~"
sudo pip install numpy

echo "~~~~~~~~~~~~~~~~~"
echo "installing bottle"
echo "~~~~~~~~~~~~~~~~~"
sudo pip install bottle

echo "~~~~~~~~~~~~~~~~~"
echo "installing beaker"
echo "~~~~~~~~~~~~~~~~~"
sudo pip install beaker

echo "~~~~~~~~~~~~~~~~~~~~~~~~"
echo "installing oauth2client"
echo "~~~~~~~~~~~~~~~~~~~~~~~~"
sudo pip install oauth2client

echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo "installing googleapiclient"
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~"
sudo pip install google-api-python-client

echo "~~~~~~~~~~~~~~~~~"
echo "DONE"

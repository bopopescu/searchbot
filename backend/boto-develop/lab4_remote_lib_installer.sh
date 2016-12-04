#!/bin/bash

echo "installing dependent frameworks"
sudo apt-get --assume-yes update
sudo apt-get --assume-yes install python-pip
sudo apt-get --assume-yes install python-dev

echo "installing numpy"
sudo pip install numpy

echo "installing bottle"
sudo pip install bottle

echo "installing beaker"
sudo pip install beaker

echo "installing oauth2client"
sudo pip install oauth2client

echo "installing googleapiclient"
sudo pip install google-api-python-client

echo "DONE"

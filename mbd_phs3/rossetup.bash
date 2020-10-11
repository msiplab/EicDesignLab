#!/bin/bash -e

function printKeys(){
    echo "Installed keys are"
    echo ""
    sudo apt-key list
}

if [ $EUID -eq 0 ]; then
   echo "This script must NOT be run as root" 1>&2
   exit 1
fi

# TODO: Check OS
# /etc/os-release
# NAME="Ubuntu"
# VERSION_ID="18.04"

# Set up keys
ROSLIST="/etc/apt/sources.list.d/ros-latest.list"
if [ -e ${ROSLIST} ]; then
    echo "${ROSLIST} found."
else
    echo  "${ROSLIST} NOT found."
    sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
fi

KEYID="C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654"
if [ '$(sudo apt-key list | grep "${KEYID}" )' ]; then
    echo "${KEYID} found."
else
    echo "${ROSLIST} NOT found."
    sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
fi 

# Installation
sudo apt update
sudo apt install ros-melodic-desktop-full

# Environment setup
SETUPLINE="source /opt/ros/melodic/setup.bash"
if [ '$(cat ~/.bashrc | grep "${SETUPLINE}" )' ]; then
    echo "${SETUPLINE} found."
else
    echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc
    source ~/.bashrc
fi

# Dependencies for building packages
sudo apt-get -y install python-rosdep python-rosinstall python-rosinstall-generator python-wstool build-essential

# Initialize rosdep
ROSDEFAULTLIST="/etc/ros/rosdep/sources.list.d/20-default.list"
sudo apt-get -y install python-rosdep
if [ -e ${ROSDEFAULTLIST} ]; then
    echo "${ROSDEFAULTLIST} found."
else
    echo  "${ROSDEFAULTLIST} NOT found."
    sudo rosdep init
fi
sudo -u ${USER} rosdep update
#!/bin/bash

# install python3 and pip
opkg update
opkg install python3
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py

opkg -e /etc/opkg/openwrt/distfeeds.conf update
opkg -e /etc/opkg/openwrt/distfeeds.conf install nano

# install python packages
pip install pyserial==3.5 pymodbus==3.11.3

su

mkdir tekever
cd tekever
mkdir tpsu
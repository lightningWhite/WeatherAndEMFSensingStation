#!/bin/bash

# This script sets up the Raspberry Pi to have the weather station start up
# on boot.

echo "This script must be run as root."

echo "Copying startWeatherStation.sh to /etc/init.d"
cp startWeatherStation.sh /etc/init.d/


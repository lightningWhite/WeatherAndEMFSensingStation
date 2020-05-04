#!/bin/bash

# This script sets up the Raspberry Pi to have the weather station start up
# on boot.

echo "This script must be run as root."

echo "Copying startWeatherStation.sh to /etc/init.d"
cp startWeatherStation.sh /etc/init.d/

echo "Enabling the weather station to start on boot"
update-rc.d startWeatherStation.sh defaults

echo "The weather staion has been installed!"
echo "The Raspberry Pi must be restarted for the weather station to start automatically."
echo ""


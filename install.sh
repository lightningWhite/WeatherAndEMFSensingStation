#!/bin/bash

# This script sets up the Raspberry Pi to have the weather station start up
# on boot.

echo ""
echo "This script must be run as root."
echo ""

echo "Copying startWeatherStation.sh to /etc/init.d"
cp startWeatherStation.sh /etc/init.d/

echo "Enabling the weather station to start on boot"
update-rc.d startWeatherStation.sh defaults

echo "Creating /mnt/usb1 as a mount point for an external storage device..."
mkdir -p /mnt/usb1
sudo chown -R pi:pi /mnt/usb1

echo "Modifying the fstab to mount an external USB storage device to /mnt/usb1..."
echo "/dev/sda1 /mnt/usb1 vfat uid=pi,gid=pi,umask=0022,sync,auto,nofail,nosuid,rw,nouser 0 0" >> /etc/fstab

echo "Setting up a default network to which the Pi should attempt to connect if present..."
printf 'network={\n\tssid="Weather"\n\tpsk="weatherStationNetwork"\n\tkey_mgmt=WPA-PSK\n\tpriority=20\n}\n' >> /etc/wpa_supplicant/wpa_supplicant.conf

echo ""

echo "The weather station has been installed!"
echo "The Raspberry Pi must be restarted for the weather station to start automatically."
echo ""


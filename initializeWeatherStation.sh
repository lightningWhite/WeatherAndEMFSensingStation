#!/bin/bash

# This will source the virtual environment for the weather station

echo 'Ensure this script is run as follows to source the current terminal:'
echo '. /home/pi/WeatherAndEMFSensingStation/initializeWeatherStation.sh'

echo 'Sourcing the python virtual environment...'
source /home/pi/WeatherAndEMFSensingStation/env/bin/activate


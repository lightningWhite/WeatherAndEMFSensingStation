#!/bin/bash

# This will source the virtual environment for the weather station

echo 'Ensure this script is run as follows to source the current terminal:'
echo '. /home/pi/WeatherStation/initializeWeatherStation.sh'

echo 'Sourcing the python virtual environment...'
source env/bin/activate


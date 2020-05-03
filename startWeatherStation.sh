#!/bin/bash

# This script will start the weather station in a tmux terminal and then detach
# it. This makes it so the ssh session can time out or be terminated and the
# weather station process will remain running. Using tmux also allows the user
# to attach to the session at any time and view the real-time output of the
# program.

# Start the weather station in a tmux terminal and then detach it
tmux new-session -d -s weather_station '. /home/pi/WeatherStation/initializeWeatherStation.sh && python3 weather_station.py && tmux detach'

echo "The weather station has been started."
echo "The log location is at ${PWD}/data/"
echo "To view the real-time output of the process, run 'tmux attach'"
echo "To detach and keep the process running after exiting the ssh session, type 'Ctrl+b' and then 'd' before logging out"


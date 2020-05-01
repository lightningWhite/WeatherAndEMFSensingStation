# This will source the virtual environment and start the weather station

echo 'Ensure this script is run as follows to source the current terminal:'
echo '. ./startWeatherStation.sh'

echo 'Sourcing the python virtual environment...'
source env/bin/activate

echo 'Starting the weather station...'
echo ''
python3 weather_station.py


# Weather Station

## Overview

The object of this project is to provide a collection of Python modules for
various sensors to be connected to a Raspberry Pi to form a weather station
equipped with logging. It is heavily based off of the tutorial found 
[here](https://projects.raspberrypi.org/en/projects/build-your-own-weather-station).

## Sensors

This project is set up to handle the following sensors:

* BME280 - Temperature, pressure, and humidity

## Development

The project requires Python 3. Once this repository is cloned, perform the
following steps:

* Create a python virtual environment and activate it:

```
python3 -m venv env
source venv/bin/activate
```

* Install the BME280 Python library

```
sudo pip3 install RPi.bme280
```

* Install the MariaDB database server software

```
sudo apt-get install -y mariadb-server mariadb-client libmariadbclient-dev
pip3 install mysqlclient
```


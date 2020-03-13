# Weather Station

## Overview

The object of this project is to provide a collection of Python modules for
various sensors to be connected to a Raspberry Pi to form a weather station
equipped with logging. It is heavily based off of the tutorial found 
[here](https://projects.raspberrypi.org/en/projects/build-your-own-weather-station).

## Sensors

This project is set up to handle the following sensors:

* BME280 - Temperature, pressure, and humidity.
  * We are using a Diymore sensor. The address for this is 0x76.

## Raspberry Pi Configuration

This works well with the NOOBS Raspbian OS installation.

In order to use the I2C and SPI interfaces, these have to be enabled. This can
be done by running `sudo raspi-config` and enabling I2C and SPI. A reboot is
required for these to be fully enabled.

## Dependencies and Prerequisites

The project requires Python 3. Once this repository is cloned, perform the
following steps:

Create a python virtual environment and activate it:

```
python3 -m venv env
source venv/bin/activate
```

Install the BME280 Python library (Note: Don't use sudo for the pip 
installations in the virtual environment):

```
pip3 install RPi.bme280
```

Install the MariaDB database server software:

```
sudo apt-get install -y mariadb-server mariadb-client libmariadbclient-dev
pip3 install mysqlclient
```

TODO: Format this better
pip install gpiozero
pip install RPi.GPIO

## Files

### bme280_sensor.py

This file interfaces with the BME280 sensor to read the humidity, pressure,
and ambient temperature. A flag is present that can be set true or false
to report the temperature in Celsius or Fahrenheit. 

There is also a calibration value that can be used to calibrate the barometer.
It is simply a value to be added or subtracted from the sensor's reading. To
determine what value to add or subtract from the reading, look up the 
barometric reading from a local weather reporting agency, such as Weather.com
or Wunderground.com. You may need to convert the agency's reading from inHg 
to millibars. Then find the difference between the weather agency's reading and
that which is reported by the sensor and add or subtract that difference as
needed from the reading.

TODO: List the pin connections

### wind.py

The datasheet for the anemometer can be found
[here](argentdata.com/files/80422_datasheet.pdf).

TODO: List the pin connections

Pin 3 on the RJ11 connector to ground
Pin 4 on the RJ11 connector to pin 5 (BCM pin 5)


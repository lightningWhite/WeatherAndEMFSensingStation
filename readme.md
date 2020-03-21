# Weather Station

## Overview

The object of this project is to provide a collection of Python modules for
various sensors to be connected to a Raspberry Pi to form a weather station
equipped with logging. It is heavily based off of the tutorial found 
[here](https://projects.raspberrypi.org/en/projects/build-your-own-weather-station).

## Hardware

Raspberry Pi 3 Model B Board
* 40 GPIO Pins - [Pinout](https://pinout.xyz/#)

### Sensors

This project is set up to handle the following sensors:

* [BME280](https://www.diymore.cc/products/5pcs-bme280-digital-pressure-sensor-temperature-humidity-barometricbreakout-module-board-gy-bme280interface-5v?_pos=1&_sid=955bdf851&_ss=r) - Temperature, pressure, and humidity.
  * Provided by Diymore sensor. The address to access it is 0x76.
* [Wind / Rain Sensor Assembly](https://www.argentdata.com/catalog/product_info.php?products_id=145)
  * Provided by Argent Data Systems
  * [Datasheet](https://www.argentdata.com/files/80422_datasheet.pdf)
* [Apogee SP-110-SS Pyranometer](https://www.apogeeinstruments.com/sp-110-ss-self-powered-pyranometer/)
  * Provided by Apogee Instruments
  * [Manual](https://www.apogeeinstruments.com/content/SP-110-manual.pdf)
* TODO: EMF Sensor

### Misc Parts

* [MCP3208](https://www.digikey.com/product-detail/en/microchip-technology/MCP3208-CI-P/MCP3208-CI-P-ND/305928) - 12 bit Analog to Digital Converter
  * Provided by Microchip Technology
  * [Datasheet](http://ww1.microchip.com/downloads/en/DeviceDoc/21298e.pdf)
* 16-pin DIL/DIP IC Socket
* 2 - 4.7 KOhm Through-hole Resistors
* 2 - 2-pin male headers
* [Adafruit Perma-Proto HAT for Pi Mini Kit - No EEPROM](https://www.adafruit.com/product/2310)
* 2 - [RJ11 Breakout Boards](http://www.mdfly.com/products/rj11-6p6c-connector-breakout-board-module-ra-screw-terminals.html)
* [3.4 x 3.4 x 2inch (85 x 85 x 50mm) Junction Box](https://www.amazon.com/Zulkit-Dustproof-Waterproof-Universal-Electrical/dp/B07Q1YBFLP/ref=asc_df_B07Q1YBFLP/?tag=hyprod-20&linkCode=df0&hvadid=344005018279&hvpos=&hvnetw=g&hvrand=4742956269277649464&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9029805&hvtargid=pla-807538012684&psc=1&tag=&ref=&adgrpid=69357499415&hvpone=&hvptwo=&hvadid=344005018279&hvpos=&hvnetw=g&hvrand=4742956269277649464&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9029805&hvtargid=pla-807538012684)
* [5.9 x 4.3 x 2.8inch (150 x 110 x 70mm) Junction Box](https://www.amazon.com/Zulkit-Dustproof-Waterproof-Universal-Electrical/dp/B07PVVDLCC/ref=asc_df_B07Q1YBFLP/?tag=&linkCode=df0&hvadid=344005018279&hvpos=&hvnetw=g&hvrand=4742956269277649464&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9029805&hvtargid=pla-807538012684&ref=&adgrpid=69357499415&th=1)
* TODO: May need a clock

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

Install the pip dependencies of the project (Note: Don't use sudo for the pip
installation in the virtual environment): 

```
pip3 install -r requirements.txt
```

Install the Debian dependencies:

```
sudo apt-get install -y mariadb-server mariadb-client libmariadbclient-dev
```

## Files

### bme280_sensor.py

This file interfaces with the BME280 sensor to report the following:

* Relative Humidity as a percentage.
* Barometric Pressure in millibars calibrated to an elevation.
* Temperature in Fahrenheit or Celsius

A flag is present that can be set true or false to report the temperature in
Celsius or Fahrenheit. 

There is also a calibration value that can be used to calibrate the barometer.
It is simply a value to be added or subtracted from the sensor's reading. To
determine what value to add or subtract from the reading, look up the 
barometric reading from a local weather reporting agency, such as Weather.com
or Wunderground.com. You may need to convert the agency's reading from inHg 
to millibars. Then find the difference between the weather agency's reading and
that which is reported by the sensor and add or subtract that difference as
needed from the sensor's reading.

Ensure the following connections to the Raspberry Pi 3 Model B:

* VIN of the BME280 sensor connected to pin 17 (3v3 Power)
* GND of the BME280 sensor connected to pin 9 (Ground)
* SCL of the BME280 sensor connected to BCM 3 (SCL)
* SDA of the BME280 sensor connected to BCM 2 (SDA)

See [https://projects.raspberrypi.org/en/projects/build-your-own-weather-station/2](https://projects.raspberrypi.org/en/projects/build-your-own-weather-station/2) for more information.

### wind.py

This file interfaces with the anemometer to record the wind speed and the wind
gust in miles per hour. It will read the wind speed every 30 seconds and store
the value. Every 15 minutes it will log the average wind speed recorded as
well as the highest speed (wind gust) recorded during the last 15 minutes.

The wind speed sensor's radius of 9.0 cm. is used to calculate the speed.

The datasheet indicates that the sensor should report a wind speed of 1.492 MPH
if the switch is closed once per second. Thus, to calibrate the sensor, first
modify the code so it prints the wind speed every 5 seconds and it calculates
the wind speed every 5 seconds. Then, rotate the sensor five times in the first
5 seconds and obtain the reading. If the reading is not 1.492, perform the 
following equation to determine the value that should be entered in for 
the `CALIBRATION` constant in the file:

```
CALIBRATION = 1.492 / reading
```

After adjusting the `CALIBRATION` factor in wind.py, repeating the test should
result in a reading of 1.492.

The datasheet for the anemometer can be found
[here](https://www.argentdata.com/files/80422_datasheet.pdf).


Ensure the following connections to the Raspberry Pi 3 Model B:

Pin 3 on the RJ11 connector to Ground
Pin 4 on the RJ11 connector to BCM 5

### Vane Values

A helper script for calculating the Vout values for each of 16 resistance values
contained in the wind direction sensor.

Each position of the wind vane results in a different resistance reading based
off of the reference voltage (3.3V) and the resistors in the voltage divider
circuit. The R2 value, chosen by us, is used to sufficiently separate the
voltage readings so they can be mapped to 16 specific directions.

The wind vane datasheet provides output voltages based off of a 5V reference
voltage. The Raspberry Pi logic levels are 3.3V, so we needed to recalculate
the voltages that map to each direction. This script is also used for finding
a suitable R2 value in our voltage divider circuit that separates the readings
sufficiently to differentiate between them.

For our uses, we've found that an R2 value of 4.7kohms works pretty well with
3.3 volts.

The wind direction sensor's resistance values mapped to the voltage values using
3.3V and 4.7kohms are as follows:

```
33000 2.9
6570 1.9
8200 2.1
891 0.5
1000 0.6
688 0.4
2200 1.1
1410 0.8
3900 1.5
3140 1.3
16000 2.6
14120 2.5
120000 3.2
42120 3.0
64900 3.1
21880 2.7
```

### Wind Direction

Ensure the following connections:

TODO: Verify this.

* Anemometer connected into the Wind Direction Sensor
* Wind Direction Sensor connected to the RJ11 connector
* Pin 2 on the RJ11 connector to 3v3
* Pin 5 on the RJ11 connector to pin 1 (CH0) on the MCP3208
* Pin 3 on the RJ11 connector to Ground (For the anemometer)
* Pin 4 on the RJ11 connector to BCM 5 (For the anemometer)
* Ground to pin 9 on the MCP3208 chip
* BCM 8 (CE0) to pin 10 (CS/SHDN) on the MCP3208 chip
* BCM 10 (MOSI) to pin 11 (Din) on the MCP3208 chip
* BCM 9 (MISO) to pin 12 (Dout) on the MCP3208 chip
* BCM 11 (SCLK) to pin 13 (CLK) on the MCP3208 chip
* Ground to pin 14 (AGND) on the MCP3208 chip
* 3v3 to pin 15 on (Vref) the MCP3208 chip
* 3v3 to pin 16 on (Vdd) the MCP3208 chip
* 4.7kohm resistor from ground to pin 1 on the MCP3208 chip for voltage 
division

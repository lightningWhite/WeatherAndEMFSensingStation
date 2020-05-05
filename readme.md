# Weather Station

## Overview

The object of this project is to provide a collection of Python modules for
various sensors to be connected to a Raspberry Pi to form a weather station
equipped with logging. It is heavily based off of the tutorial found 
[here](https://projects.raspberrypi.org/en/projects/build-your-own-weather-station).

It also provides for EMF sensing and logging using the EMF-390 sensor connected
to the Raspberry Pi.

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
* [EMF-390 Sensor](https://www.amazon.com/Advanced-GQ-Multi-Field-Electromagnetic-Radiation/dp/B07JGJ897T)
  * Provided by GQ Electronics
  * Software for running a command line interface on the Raspberry Pi can be
  downloaded [here](https://gitlab.com/codref/em390cli/-/tags/v0.1.0).
  * [Manual](https://www.gqelectronicsllc.com/GQ-EMF-360V2-380V2-390_UserGuide.pdf)

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
* [ChronoDot 2.1 (DS3231 Chip) Real Time Clock](https://www.adafruit.com/product/255)

## Raspberry Pi Configuration

This works well with the NOOBS Raspbian OS installation.

In order to use the I2C and SPI interfaces, these have to be enabled. This can
be done by running `sudo raspi-config` and enabling I2C and SPI. A reboot is
required for these to be fully enabled.

### Real Time Clock

The Raspberry Pi can't keep accurate time when it's disconnected from the
internet. For this reason, we use a Real Time Clock (RTC) module. We've
chosen to use the ChronoDot 2.1.

The following location provides a nice tutorial for setting up the Raspberry Pi
to use the RTC:

* [Adding a DS3231 Real Time Clock To The Raspberry Pi](https://www.raspberrypi-spy.co.uk/2015/05/adding-a-ds3231-real-time-clock-to-the-raspberry-pi/)

The following instructions come largely from the link above.

Ensure the following connections to the Raspberry Pi 3 Model B:

* GND of the RTC connected to pin 9 (Ground)
* VCC of the RTC connected to pin 17 (3v3 Power)
* SCL of the RTC connected to BCM 3 (SCL)
* SDA of the RTC connected to BCM 2 (SDA)

To view the I2C address of the RTC, the following command can be run:

```
sudo i2cdetect -y 1
```

This may show the addresses of other connected I2C devices, but the RTC address
will likely by 0x68.

In order to synchronize the Raspberry Pi's time with the RTC when the Pi boots,
the following needs to be added to the `/etc/rc.local` file right before the
`exit 0` at the end: 

```
echo ds3231 0x68 > /sys/class/i2c-adapter/i2c-1/new_device
```

The Raspberry Pi should then be rebooted:

```
sudo reboot
```

The date and time reported by the Raspberry Pi can be viewed with the `date`
command. If the time needs to be manually set, it can be done with a command
such as the following:

```
sudo date -s "29 AUG 1997 13:00:00"
```

When the time is correcly set, the system date and time can be written to the
RTC module with the following command:

```
sudo hwclock -w
```

The time can then be read from the RTC with this command:

```
sudo hwclock -r
```

To verify that the system time and the RTC time is the same, the following
command can be run:

```
date; sudo hwclock -r
```

To verify that the RTC is correctly keeping time and that the Raspberry Pi
will use it when it boots, power down the Raspberry Pi, disconnect the
power cable, remove the network connection, connect the Pi to a monitor and
keyboard, leave it overnight, and then power it up and use "date" to
verify that the time reported is correct.

## Dependencies and Prerequisites

The project must be cloned to `/home/pi/` for the scripts to work correctly.

The project requires Python 3 to be installed. 

Once this repository is cloned, perform the following steps:

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

Install `tmux`:

```
sudo apt-get install tmux
```

## Running the Weather Station

The `startWeatherStation.sh` script will start a tmux session and call the
`initializeWeatherStation.sh` script. This script will source the python virtual
environment. It will then start the weather station and detach the tmux session. 
This makes it so the ssh session can time out or be terminated and the weather
station process will remain running. Using tmux also allows the user to attach
to the session at any time and view the real-time output of the program.

After the `startWeatherStation.sh` script has been executed, you can attach to
the process and view the output in real-time by typing `tmux attach`. To detach
from the session again so it can continue running when the ssh session times
out or you log out from it, type `Ctrl+b` and then `d`. This will put it in the
background to continue running.

The `install.sh` script when run will copy the necessary files to `/etc/init.d`
so the weather station will start on boot automatically. Simply execute the
script and reboot. Note that the `install.sh` script must be run as root.

Also note that when the weather station has been started automatically on boot,
to view the real-time output of the weather station, you must attach to the
tmux session as root: `sudo tmux attach`.

The EMF-390 sensor must be connected to the Raspberry Pi for the weather
station to start up correctly. The sensor must also be in vertical mode viewing
RF. If this is not set up like this, the Weather Station may crash and/or won't
report the correct EMF values. Also, it's important that the battery is
removed from the EMF-390 device. Some resources on the internet report that
the charging circuit is not shielded. Since it is plugged into the Raspberry
Pi, this unshielded circuit would throw off the EMF readings.

## Data Logging

As the weather station runs, it will log readings from all of the sensors at a
configurable rate. This can be set in the weather_sttion.py file. The
LOG_INTERVAL defines how often the readings will be logged. The
ACCUMULATION_INTERVAL defines how often samples should be taken of some of the
sensors in order to calculate and averages or maximums. The
ACCUMULATION_INTERVAL should be less than the LOG_INTERVAL.

A log file will be created every time the weather station is started and it
will be saved to `/home/pi/WeatherStation/data` and be named the date and time
of when it was created.

The CSV file will grow at a rate of about 4 Kilobytes for every 13 entries.

## Files

### weather_station.py

This file is the main program. It contains the main program loop.

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

### vane_values.py

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

TODO: Update these...

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

### wind_direction.py

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

### rainfall.py

This file interfaces with the rain sensor to calculate how much rain has fallen
in inches. It counts how many times the bucket has tipped, where each bucket
tip signifies 0.011 inches of rain.

Ensure the following connections to the Raspberry Pi 3 Model B:

* Pin 3 on the RJ11 connector to Ground
* Pin 4 on the RJ11 connector to BCM 6

### pyranometer.py

TODO

### EMF-390

A command line interface tool has been written that allows the Raspberry Pi
to perform real-time logging of the readings from the EMF-390 sensor.

The application can be downloaded from [here](https://gitlab.com/codref/em390cli/-/tags/v0.1.0).
Simply download the Arm Linux zip file to the Raspberry Pi and unzip it:

`unzip emf390cli.zip`

A forum that may be helpful that references this application and source code 
can be found [here](https://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=6308).

Instructions for running the tool can be found in the project's README
[here](https://gitlab.com/codref/em390cli/-/blob/master/README.md).

As a precaution in case the project disappears, the source code for it has been
added to this repository. The clone of the GitLab project also includes the
build directory with the application binaries for different platforms.
However, as long as the project is alive, it will be best to use the provided
application in order to receive the updates. The source code is licensed under
the GNU General Public License. Instructions for building from source on the
Raspberry Pi are provided in the README file.

The README of the project also notes that to use the device for real-time data
logging, it's best to remove the battery. It says that the charging circuit is
not shielded and it will produce a lot of interferance.

To read data in real-time from the device in a CSV format, the following command
can be used:

```
emf390cli -p /dev/ttyUSB0 -f '%w%d%e%t%k%E%M' --csv
```

This specifies the serial port to connect to, the desired format, and to export
the fetched values as a CSV string.

The following is some sample output:

```
rfwatts, 0.000000000158, 158, pW, 672, MHz
rfdbm, -68, -68, dbm, 672, MHz
rfdensity, 0.0001, 0.1, mW/m2, 672, MHz
rftotaldensity, 0.06720000000000001, 67.2, mW/m2, 0, n/a
rftotaldensitypeak, 0.6354, 635.4, mW/m2, 0, n/a
ef, 11.8, 11.8, V/m, 0, n/a
emf, 0.6, 0.6, mG, 0, n/a
```

For each metric, it lists the name, the value, the raw value, the raw value
unit, the MHz, and the MHz unit.

IMPORTANT: In order for the correct values to be obtained, the EMF sensor must
be in `Vertical Mode` or else the readings will be incorrect and a potential
crash could occur.

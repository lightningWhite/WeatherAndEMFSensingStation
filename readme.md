# Weather and EMF Sensing Station

## Overview

The object of this project is to provide a collection of Python modules for
various sensors to be connected to a Raspberry Pi to form a weather and
Electromagnetic Frequency sensing station equipped with logging. It is heavily
based off of the tutorial found [here](https://projects.raspberrypi.org/en/projects/build-your-own-weather-station) and further customized.

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
* [5.9 x 5.9 x 2.8inch (150 x 150 x 70mm) Junction Box](https://www.amazon.com/LeMotech-Dustproof-Waterproof-Electrical-150mmx150mmx70mm/dp/B075DG55KS/ref=sr_1_4?dchild=1&keywords=150x150x70+junction+box+Zulkit&qid=1590254877&sr=8-4)
* [ChronoDot 2.1 (DS3231 Chip) Real Time Clock](https://www.adafruit.com/product/255)

## Raspberry Pi Configuration

This works well with the [NOOBS Raspbian OS](https://www.raspberrypi.org/downloads/noobs/) installation. This was all tested with the Buster version of Raspbian.

In order to use the I2C and SPI interfaces, these have to be enabled. This can
be done by running `sudo raspi-config` and enabling I2C and SPI in the
`Interfacing Options`. A reboot is required for these to be fully enabled. This
can be done by running `sudo reboot`.

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
hwclock -s
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

When the time is correctly set, the system date and time can be written to the
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
This can be done by running the following:

```
git clone https://github.com/lightningWhite/WeatherAndEMFSensingStation.git
```

The project requires Python 3 to be installed. 

Once this repository is cloned, perform the following steps:

Create a python virtual environment and activate it:

```
python3 -m venv env
source env/bin/activate
```

Install the pip dependencies of the project (Note: Don't use sudo for the pip
installation in the virtual environment): 

```
pip3 install -r requirements.txt
```

Install `tmux`:

```
sudo apt-get update
sudo apt-get install tmux
```

The `install.sh` script when run will copy the necessary files to `/etc/init.d`
so the weather station will start on boot automatically. It will also create a
mount point and modify the fstab so an external USB storage device will be
automatically mounted on boot. It will also configure the Pi to automatically
connect to a network named `Weather` if present. This can be helpful if you want
to connect to the Pi wirelessly using a mobile hotspot. This script must be run
as root and the Pi must be restarted for the changes to take effect:

```
sudo ./install.sh
sudo reboot
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

Note that when the weather station has been started automatically on boot,
to view the real-time output of the weather station, you must attach to the
tmux session as root: `sudo tmux attach`.

The EMF-390 sensor must be connected to the Raspberry Pi via USB for the weather
station to start up correctly. The sensor must also be in vertical mode viewing
RF. If this is not set up like this, the Weather Station may crash and/or won't
report the correct EMF values. Also, it's important that the battery is
removed from the EMF-390 device. Some resources on the internet report that
the charging circuit is not shielded. Since it is plugged into the Raspberry
Pi, this unshielded circuit would throw off the EMF readings.

When the weather and EMF sensing station is started with the
`startWeatherStation.sh` script, the real-time output will be written to a log
file by the name of the time the weather station was started and be written to
the /logs directory in the repository. Log messages are written to stdout and
should capture most of the problems that may arise while the weather station is
running. This can assist in debugging.

## Data Logging

As the weather station runs, it will log readings from all of the sensors at a
configurable rate. This can be set in the weather_station.py file. The
LOG_INTERVAL defines how often the readings will be logged. The
ACCUMULATION_INTERVAL defines how often samples should be taken of some of the
sensors in order to calculate and averages or maximums. The
ACCUMULATION_INTERVAL should be less than the LOG_INTERVAL.

A log file will be created every time the weather station is started and it
will be saved to `/home/pi/WeatherAndEMFSensingStation/data` and be named the date and time
of when it was created.

The CSV file will grow at a rate of about 4 Kilobytes for every 13 entries.

If an external USB storage device is connected, such as a thumbdrive, the data
file will be copied to it after each data record is written. When the next
record is to be copied to the external storage drive, the previously copied
file will have its name changed to have a .bak extension so it isn't overwritten
until the latest copy of the data file is obtained. The next time the data file
is to be copied to the external storage device, the .bak file will be
overwritten with the previously backed up file and the new data file will be
copied to the drive.

Here is some sample data that was logged by the station:

```
Record Number, Time, Temperature (F), Pressure (mbar), Humidity (%), Wind Direction (Degrees), Wind Direction (String), Wind Speed (MPH), Wind Gust (MPH), Precipitation (Inches), Shortwave Radiation (W m^(-2)), Avg. RF Watts (W), Avg. RF Watts Frequency (MHz), Peak RF Watts (W), Frequency of RF Watts Peak (MHz), Peak RF Watts Frequency (MHz), Watts of RF Watts Frequency Peak (W), Avg. RF Density (W m^(-2)), Avg. RF Density Frequency (MHz), Peak RF Density (W m^(-2)), Frequency of RF Density Peak (MHz), Peak RF Density Frequency (MHz), Density of RF Density Frequency Peak (W m^(-2)), Avg. Total Density (W m^(-2)), Max Total Density (W m^(-2)), Avg. EF (V/m), Max EF (V/m), Avg. EMF (mG), Max EMF (mG)
1, 2020-05-16 16:38:54.100572, 67.8, 1014.3, 23.8, 256.5, WSW, 0.7, 2.5, 0.0, 130.0, 0.0000000003326912, 694.0, 0.0000000050000000, 1866.0, 1866.0, 0.0000000050000000, 0.0000338235294118, 732.6, 0.0005000000000000, 1866.0, 1881.0, 0.0003000000000000, 0.0001264705882353, 0.0010000000000000, 693.7, 886.0, 1.2, 1.4
2, 2020-05-16 16:53:55.786168, 66.2, 1014.3, 24.0, 252.0, WSW, 0.5, 2.1, 0.0, 140.0, 0.0000000008500571, 759.1, 0.0000000250000000, 1880.0, 1881.0, 0.0000000040000000, 0.0000542857142857, 776.4, 0.0013000000000000, 1880.0, 1881.0, 0.0004000000000000, 0.0003014285714286, 0.0011000000000000, 676.6, 844.0, 1.3, 1.5
3, 2020-05-16 17:08:56.629817, 65.8, 1014.1, 23.3, 255.5, WSW, 0.4, 3.1, 0.0, 130.0, 0.0000000004531143, 741.0, 0.0000000050000000, 1861.0, 1878.0, 0.0000000030000000, 0.0000285714285714, 758.6, 0.0005000000000000, 1861.0, 1878.0, 0.0003000000000000, 0.0002600000000000, 0.0011000000000000, 690.1, 889.6, 1.2, 1.4
4, 2020-05-16 17:23:58.887251, 65.1, 1014.2, 24.5, 248.4, WSW, 0.3, 1.5, 0.0, 140.0, 0.0000000005634000, 775.9, 0.0000000160000000, 1884.0, 1884.0, 0.0000000160000000, 0.0000028571428571, 671.5, 0.0001000000000000, 1880.0, 1880.0, 0.0001000000000000, 0.0004728571428571, 0.0028000000000000, 664.1, 880.0, 1.2, 1.5
5, 2020-05-16 17:38:59.409071, 65.1, 1014.2, 23.7, 295.7, WNW, 0.1, 0.9, 0.0, 145.0, 0.0000000002303000, 670.8, 0.0000000030000000, 1872.0, 1872.0, 0.0000000030000000, 0.0000228571428571, 776.0, 0.0003000000000000, 1872.0, 1879.0, 0.0003000000000000, 0.0011057142857143, 0.0029000000000000, 675.8, 880.0, 1.2, 1.4

```

This can easily be viewed by opening the .csv file with a spreadsheet
application such as Microsoft Excel, LibreOffice Calc, or Google Sheets.

## Logging

The `weather_station.py` file initializes a logger. Log messages from the
weather and EMF sensing station will be stored in the `logs` directory by
the same time name as the data file. This log output can be very helpful for
debugging if any issues arise.

## Helpful Connection Information

In order to connect to the Raspberry Pi via ssh, it must be enabled first.
This resource provides some instructions on how to do that:

* https://www.raspberrypi.org/documentation/remote-access/ssh/

One of the methods mentioned is to have the Pi connected to a keyboard and
monitor and then run the following:

```
sudo systemctl enable ssh
sudo systemctl start ssh
```

Note that this can also be done using `raspi-config`.

A helpful tool for finding the IP address of the Raspberry Pi in order to
ssh to it, is `arp-scan`. It can be installed by running the following:

```
sudo apt-get install arp-scan
```

To list the IP addresses of devices on the network, run the following:

```
sudo arp-scan -l
```

### Connecting to the Raspberry Pi Using an Android Phone

#### termux

An Android app called `termux` can be installed from Google Play. This
app provides a terminal on the Android phone. Using this terminal, files
can be copied from the Raspberry Pi via `scp`. Connections can also be made to
the Pi using `ssh`. To do this, open termux on an Android phone and run the
following commands:

Enable tmux to access the phone's storage so you can access any copied files
from the Pi:

```
termux-setup-storage
```

Allow access when the dialog pops up.

Install ssh and scp:

```
pkg install openssh
```

You can now ssh to the Raspberry Pi using the Pi's IP address if you're on
the same network:

```
ssh pi@192.168.0.23
```

You can also copy one of the data files from the Pi to your phone with a
command such as this:

```
cd storage/downloads
scp pi@192.168.0.23:/home/pi/WeatherAndEMFSensingStation/data/05-07-2020--19-08-22.csv .
```

Enter the Raspberry Pi's password and the file should be copied to the phone.

The file should then be copied to the Downloads folder of the phone.

If you want to copy all of the data files to your phone, you can do so using
the wildcard such as this:

```
cd storage/downloads
scp -r pi@192.168.0.23:/home/pi/WeatherAndEMFSensingStation/data/ .
```

#### VNC Viewer - Remote Desktop

`VNC Viewer - Remote Desktop` can be installed via Google Play. Once this is
installed, a vncserver can be started on the Raspberry Pi. vncserver needs to
be enabled on the Pi before doing this. This can be done by running
`raspi-config` and selecting `Interfacing Options`. Then select VNC and
enable it.

Once it is enabled, a vncserver can be started by running the following:

```
vncserver :1
```

This will start the vncserver on port 5901.

Using the Android vnc client application, you can connect to the Pi by
entering the IP address of the Raspberry Pi followed by a :1 such as this:

```
192.168.0.23:1
```

This will provide the desktop GUI with which you can interact.

#### Connecting Using a WiFi Hotspot from an Android Phone

Since the Pi will likely be running in a location without WiFi, in order to
connect via the methods above, some sort of network needs to be in place. This
can be a mobile hotspot.

The Raspberry Pi can be configured to connect automatically to a WiFi hotspot.
Then the mobile device or another device connected to the same network can
ssh to the Pi or scp files from the Pi to the phone. Do the following to make
this possible:

Modify the `wpa_supplicant.conf` file located at `/etc/wpa_supplicant/` to
include the hotspot network and password. An example of what should be added
is as follows:

```
network={
  ssid="WeatherNetwork"
  psk="password"
  key_mgmt=WPA-PSK
  priority=20
}
```

The Raspberry Pi must be restarted for the changes to take effect.

This will cause the Raspberry Pi to automatically connect to a network with the
name of "WeatherNetwork" and use the password "password" if the network is
present. Setting the priority to 20 (some arbitrarily large number) should
ensure that it will be the first network that it will try to connect to. Note
that the `install.sh` script will configure this network connection when it is
run.

On the mobile device, set up a hotspot with that name and password and turn it
on. The Pi should automatically connect to the hotspot.

The mobile hotspot should show that one device is connected. To view the IP
address of the Raspberry Pi, open up a terminal in the phone using something
like Termux and type the following:

```
ip neigh
```

This should show the IP address of the Raspberry Pi on the hotspot network.

Any of the previously mentioned methods should now work to connect to the
Raspberry Pi using the mobile device.

## Files

The following files are the primary files used in the weather and EMF sensing
station:

* weather_station.py - The main program loop
* bme280_sensor.py - Temperature, pressure, and humidity sensing
* emf.py - EMF sensing
* pyranometer.py - Solar radiation sensing (Shortwave sensing)
* wind_direction.py - Wind direction sensing

The following files are used for setting up and running the weather station:

* install.sh - Configures the Raspberry Pi to start the weather station on boot
* initializeWeatherStation.sh - Sources the Python3 virtual environment
* startWeatherStation.sh - Starts the weather station in a tmux session and
runs it in the background

The following files are used for developmental and testing purposes, but the
code from them is extracted into the `weather_station.py` file. The
documentation for these files is relevant for the code used in the
weather_station.py file:

* rainfall.py - Keeps track of precipitation
* vane_values.py - Utility file used for finding voltages to be mapped to
resistance values in for calculating the wind direction
* wind.py - Calculates the wind speed

### Primary Weather Station and EMF Sensing Files 

#### weather_station.py

This file contains the main program loop. It contains all the code for the
weather station with the exception of the following files, which are imported:

* bme280_sensor.py
* emf.py
* pyranometer.py
* wind_direction.py

As the weather station runs, it will gather and log readings from all of the
sensors at a configurable rate. The LOG_INTERVAL defines how often the readings
will be logged. The ACCUMULATION_INTERVAL defines how often samples should be
taken of some of the sensors in order to calculate and averages or maximums.
The ACCUMULATION_INTERVAL should be less than the LOG_INTERVAL.

#### bme280_sensor.py

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

#### wind_direction.py

Ensure the following connections:

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

See the vane_values.py documentation for more information about how this
file works.

#### pyranometer.py

This file uses the ADC to read the voltage from the Apogee SP-110 Pyranometer
sensor. This sensor will output a voltage between 0 and 250 mV where each
mV represents 5.0 W m^-2.

According to the sensor's documentation, full sunlight should yield a total
shortwave radiation on a horizontal plane at Earth's surface of approximately
1000 W m^-2.

Ensure the following connections to the Raspberry Pi 3 Model B:

Ground to pin 9 on the MCP3208 chip
BCM 8 (CE0) to pin 10 (CS/SHDN) on the MCP3208 chip
BCM 10 (MOSI) to pin 11 (Din) on the MCP3208 chip
BCM 9 (MISO) to pin 12 (Dout) on the MCP3208 chip
BCM 11 (SCLK) to pin 13 (CLK) on the MCP3208 chip
Ground to pin 14 (AGND) on the MCP3208 chip
3v3 to pin 15 on (Vref) the MCP3208 chip
3v3 to pin 16 on (Vdd) the MCP3208 chip
Black wire of the Pyranometer to Ground
White wire of the Pyranometer to pin 2 (CH1) of the MCP3208 chip

#### EMF-390

A command line interface tool has been written that allows the Raspberry Pi
to perform real-time logging of the readings from the EMF-390 sensor. This
tool was written by Davide Dal Farra.

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
not shielded and it will produce a lot of interference.

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

Some additional notes:
 
rfwatts and rfdbm are different forms of the same number. The problem is that it
appears that they are calculated sequentially. This means that the readings of
the sensor may be different for each reading reported in the output. This is not
ideal. They should not contradict each other. One or the other reading could be
taken and then converted to the other form if it's desirable to have both.

I believe that the power density value obtained from the sensor is calculated
using this formula: Power Density = (Pout * Gain) / (4 * PI * Distance^2)

The gain used by the sensor for the antennae is 10 (configurable in the sensor
settings, but the forum recommends to leave it at 10 unless using some sort of
external antenna). The distance can be calculated when D when a Power Density
is reported, however, this distance seems to change for different readings, so
it's unclear what's being used for the distance in the equation. Pout is
probably the rfwatts reading.

Since the gain and the distance (probably) is hard-coded, the power density is
not the value of a tower or something. It is just a relative value at the
current location.

It's unclear how total power density is being calculated. It might be some sort
of sum.

This forum is helpful and may be a good resource for clearing up some of the
questions mentioned above: https://www.gqelectronicsllc.com/forum/forum.asp?FORUM_ID=18

Although there are some discrepancies between the values obtained from the
emf390cli tool, these discrepancies are mitigated in the `weather_station.py`
file by collecting values and then reporting averages and maximums rather than
simply reporting each of the values directly reported by the tool.

#### logging.py

This file provides logging functionality. A path to the log file location is
passed to the intialize_logger function and then messages can then be logged
by calling the log function and passing a message. The message will be logged
with the current time.

### Developmental and Utility Files

The code from most of these files is extracted into the weather_station.py
file. The documentation for those code extracts is contained in each file
subsection below.

#### wind.py

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

#### rainfall.py

This file interfaces with the rain sensor to calculate how much rain has fallen
in inches. It counts how many times the bucket has tipped, where each bucket
tip signifies 0.011 inches of rain.

Ensure the following connections to the Raspberry Pi 3 Model B:

* Pin 3 on the RJ11 connector to Ground
* Pin 4 on the RJ11 connector to BCM 6

#### vane_values.py

A helper script for calculating the Vout values for each of 16 resistance values
contained in the wind direction sensor. To run the script, ensure that the
connections specified for the wind_direction.py script are in place.

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
33000 0.4
6570 1.4
8200 1.2
891 2.8
1000 2.7
688 2.9
2200 2.2
1410 2.5
3900 1.8
3140 2.0
16000 0.7
14120 0.8
120000 0.1
42120 0.3
64900 0.2
21880 0.6
```

As an important side note, these voltage values mapped to headings came from
the Raspberry Pi weather station tutorial mentioned previously. However, the
voltages came  from an incorrect voltage divider equation. In the tutorial,
they used the following equation: vout = (vin * r1) / (r1 + r2)

It should have been the following: vout = (vin * r2) / (r1 + r2)

However, with a vin of 3v3 and the external resistor of 4.7kohms
(r1 in their equation), there are 16 different values, so it works.
Due to limited resources and time, I left it as they had it rather
than find a different resistor value that would also work.

The voltages found above are then mapped to various headings in degrees as
follows:

```
0.4: 0.0
1.4: 22.5 
1.2: 45.0 
2.8: 67.5
2.7: 90.0 
2.9: 112.5 
2.2: 135.0 
2.5: 157.5
1.8: 180.0 
2.0: 202.5 
0.7: 225.0 
0.8: 247.5
0.1: 270.0 
0.3: 292.5 
0.2: 315.0 
0.6: 337.5
```

### Board Assembly Notes

Referring to the Raspberry Pi Weather Station tutorial mentioned earlier can
be helpful, but since this weather station has several modifications, these
are some additional notes of what I did that may be helpful while assembling
the board. Remember to turn off the Pi before taking off or putting on the
Pi HAT board. Sometimes bugs can crop up by leaving the Pi on while doing this
that can take a good while to figure out.

* I would start with placing the MCP3208 chip socket. After this
is placed, connect all the wires that go from the Pi to the chip.
* Connect the wind speed and wind direction sensors. This requires the RJ11
breakout board. I found it helpful to string the wires from the Pi and the
MCP3208 to the breakout board under the board and up through the slot on the
HAT board. This kind of holds them in place. I placed the RJ11 breakout board
so it would sit on top of the Ethernet port of the Pi. When doing this, it's
extremely important to insulate the bottom of the RJ11 breakout board and/or
the top of the Ethernet and USB ports, otherwise the connections on the RJ11
board will ground out on the metal. I just used some electrical tape. Also,
I just strung the resistor from the chip's pin 1 to the ground rail near the
5V power rail. And, don't be tempted to use the 5V power rail by accident. Be
sure to test that the wind speed and wind direction sensors work. I tested them
by slightly modifying the code to print out the values obtained in the
respective files. Be sure to undo the changes when done testing.
* Connect the Pyranometer. Again, I strung the wires through the slot on the
HAT board to the MCP3208. I clipped the bare metal end of the clear wire and
coiled it up so it wouldn't accidentally touch anything. We don't use it.
Again, test this to make sure it works before moving on.
* Connect the rain gauge. Like the others, I strung the wires from the Pi to
the RJ11 breakout board through the slot. I positioned the RJ11 connector to
sit on top of the USB ports. Remember to insulate the bottom of the RJ11
connector and/or the top of the USB ports.
* Solder on the two two-pin headers for the BME280 sensor. Make sure it works.
* Connect the Real Time Clock. This one is a little tricky because it needs
to be connected to the SDA and SCL pins which are already in use by the
BME280 sensor. I got around this by just soldering the end of the wires to the
stubs on the back of the Pi HAT of the two-pin header on those two pins. Take
care not to bridge the SDA and SCL pins when soldering the ends. Then I strung
it under over to the clock. I placed the clock between the ADC and the RJ11
connectors. Remember to test it out and set the clock. Again, make sure you
have the Pi off and start it after it's connected. Also, remember to follow
the set up instructions near the top of this readme to configure and set the
Real Time Clock.

# Diymore BME280 Humidity, Pressure, and Temperature Sensor Module
# 
# Reports the Relative Humidity as a percentage.
# Reports the Barometric Pressure in millibars calibrated to an elevation.
# Reports the Temperature in Celsius
#
# Ensure the following connections to the Raspberry Pi 3 Model B:
# 
# VIN connected to pin 17
# GND connected to pin 9
# SCL connected to pin 5
# SDA connected to pin 3

import bme280
import smbus2
from time import sleep

ELEVATION = 4534 # Elevation of Logan, Utah in feet
# TODO: Calibrate the barometer to the elevation
# TODO: Convert the temparature to degrees F? Or leave it at C?

port = 1
address = 0x76 # BME280 address (Diymore sensor. Adafruit would be 0x77)
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus, address)

# TODO: Change this to a function named read_all() and return the values
while True:
    bme280_data = bme280.sample(bus, address)
    humidity = bme280_data.humidity
    pressure = bme280_data.pressure
    ambient_temperature = bme280_data.temperature
    print(f"Humidity: {humidity}, Pressure: {pressure}, Temperature: {ambient_temperature}")
    sleep(1)

print("hello!")



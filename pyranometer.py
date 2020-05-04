# Pyranometer
#
# Uses the ADC to read the voltage from the Apogee SP-110 Pyranomter sensor.
#
# Ensure the following connections:
# 
# Ground to pin 9 on the MCP3208 chip
# BCM 8 (CE0) to pin 10 (CS/SHDN) on the MCP3208 chip
# BCM 10 (MOSI) to pin 11 (Din) on the MCP3208 chip
# BCM 9 (MISO) to pin 12 (Dout) on the MCP3208 chip
# BCM 11 (SCLK) to pin 13 (CLK) on the MCP3208 chip
# Ground to pin 14 (AGND) on the MCP3208 chip
# 3v3 to pin 15 on (Vref) the MCP3208 chip
# 3v3 to pin 16 on (Vdd) the MCP3208 chip
# Black wire of the Pyranometer to Ground
# White wire of the Pyranometer to pin 2 (CH1) of the MCP3208 chip

from gpiozero import MCP3208
# TODO: Remove this
# from gpiozero import MCP3304

import math

# How often the average wind direction should be logged
LOG_INTERVAL = 5 #900 # 15 Minutes

# Analog to Digital Converter
adc = MCP3208(channel=1)

# TODO: Remove this when we get the new chip
# adc = MCP3304(channel=1)

# Return the total shortwave radiation on a horizontal plane at Earth's surface
# in Watts per meter squared (W m^-2)
def get_shortwave_radiation():

    # Each millivolt represents 5.0 W m^-2
    calibration_factor = 5.0

    # Sensor voltage in millivolts
    sensor_voltage = round(adc.value * 3.3, 3) * 1000

    return round(calibration_factor * sensor_voltage, 1)


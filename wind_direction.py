# Wind Direction
#
# Uses the ADC to read the voltage from the wind direction sensor
# and maps it do the corresponding direction. It then averages the readings
# over a period of time and then logs the average.
#
# Ensure the following connections:
# 
# Anemometer connected into the Wind Direction Sensor
# Wind Direction Sensor connected to the RJ11 connector
# Pin 2 on the RJ11 connector to 3v3
# Pin 5 on the RJ11 connector to pin 1 (CH0) on the MCP3208
# Pin 3 on the RJ11 connector to Ground (For the anemometer)
# Pin 4 on the RJ11 connector to BCM 5 (For the anemometer)
# Ground to pin 9 on the MCP3208 chip
# BCM 8 (CE0) to pin 10 (CS/SHDN) on the MCP3208 chip
# BCM 10 (MOSI) to pin 11 (Din) on the MCP3208 chip
# BCM 9 (MISO) to pin 12 (Dout) on the MCP3208 chip
# BCM 11 (SCLK) to pin 13 (CLK) on the MCP3208 chip
# Ground to pin 14 (AGND) on the MCP3208 chip
# 3v3 to pin 15 on (Vref) the MCP3208 chip
# 3v3 to pin 16 on (Vdd) the MCP3208 chip
# 4.7kohm resistor from ground to pin 1 on the MCP3208 chip for voltage div

from gpiozero import MCP3208
# Remove this
from gpiozero import MCP3304

import math
import time

# How often the average wind direction should be logged
LOG_INTERVAL = 5 #900 # 15 Minutes

# Analog to Digital Converter
# adc = MCP3208(channel=0)
adc = MCP3304(channel=0)

count = 0
values = []
while True:
    # TODO: Chanbe this back to 3.3
    wind = round(adc.value * 5.0, 1)
    if not wind in values:
        values.append(wind)
        count += 1
        print(f"Count: {count}, Value: {adc.value}, Wind: {wind}")

#####
# The above code is for debugging and testing first

# # A map that maps voltage readings to wind directions in degrees
# volts = {2.9: 0.0, 
#          1.9: 22.5, 
#          2.1: 45.0, 
#          0.5: 67.5,
#          0.6: 90.0, 
#          0.4: 112.5, 
#          1.1: 135.0, 
#          0.8: 157.5,
#          1.5: 180.0, 
#          1.3: 202.5, 
#          2.6: 225.0, 
#          2.5: 247.5,
#          3.2: 270.0, 
#          3.0: 292.5, 
#          3.1: 315.0, 
#          2.7: 337.5}

# # Calculate the average angle from a list of angles
# def get_average(angles):
#     sin_sum = 0.0
#     cos_sum = 0.0

#     for angle in angles:
#         r = math.radians(angle)
#         sin_sum += math.sin(r)
#         cos_sum += math.cos(r)

#     flen = float(len(angles))
#     s = sin_sum / flen
#     c = cos_sum / flen
#     arc = math.degrees(math.atan(s / c))
#     average = 0.0

#     if s > 0 and c > 0:
#         average = arc
#     elif c < 0:
#         average = arc + 180
#     elif s < 0 and c > 0:
#         average = arc + 360

#     return 0.0 if average == 360 else average

# # Returns the average direction read over a period of time
# def get_value(time_period=LOG_INTERVAL):
#     data = []
#     print(f"Measuring wind direction for {time_period} seconds...")
#     start_time = time.time()

#     while time.time() - start_time <= time_period:
#         wind = round(adc.value * 3.3, 3)
#         if not wind in volts:
#             print('unknown value ' + str(wind))
#         else:
#             data.append(volts[wind])

#     return get_average(data)

# # while True:
#     # print(get_value())

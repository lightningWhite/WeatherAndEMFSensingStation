# ChronoDot 2.1 Real-Time Clock Module
# 
# Allows the Raspberry Pi to maintain an accurate clock without an internet
# connection and between power offs.
#
# This code was largely pulled from https://bradsrpi.blogspot.com/2013/04/reading-time-date-from-chronodot-using.html 
#
# Ensure the following connections to the Raspberry Pi 3 Model B:
# 
# GND of the RTC connected to pin 9 (Ground)
# VCC of the RTC connected to pin 17 (3v3 Power)
# SCL of the RTC connected to BCM 3 (SCL)
# SDA of the RTC connected to BCM 2 (SDA)

import smbus
import time

bus = smbus.SMBus(1)
address = 0x68

def get_date_time():
    data = bus.read_i2c_block_data(address, 0)

    ss = (data[0]/16*10) + (data[0]%16)
    mm = (data[1]/16*10) + (data[1]%16)
    hr = (data[2]/16*10) + (data[2]%16)
    day = (data[3]/16*10) + (data[3]%16)
    date = (data[4]/16*10) + (data[4]%16)
    month = (data[5]/16*10) + (data[5]%16)
    year = (data[6]/16*10) + (data[6]%16)

    # buffer = "%02d:%02d:%02d %02d/%02d/%02d" % (hr, mm, ss, month, day, year)
    date_time = f"{year}-{month}-{date} {hr}:{mm}:{ss}"

    print date_time
    return date_time

print(get_date_time())

# Argent Rain Sensor
# 
# Reports the rainfall in inches
#
# Ensure the following connections to the Raspberry Pi 3 Model B:
# 
# Pin 3 on the RJ11 connector to Ground
# Pin 4 on the RJ11 connector to BCM 6

from gpiozero import Button
import time

rain_sensor = Button(6)
BUCKET_SIZE = 0.011 # inches per bucket tip
LOG_INTERVAL = 900 # How often to log in seconds (15 min)
count = 0
precipitation = 0

def bucket_tipped():
    global count
    global precipitation
    count = count + 1
    precipitation = count * BUCKET_SIZE
    print("tipped")

def reset_rainfall():
    global count
    count = 0

rain_sensor.when_pressed = bucket_tipped

while True:
    print(precipitation)
    time.sleep(LOG_INTERVAL)

# TODO: clear the rainfall each day at midnight
# import datetime
# previous_day = datetime.datetime.now()
#
# # In loop check if the day has changed
# current_day = datetime.datetime.now()
# # When it's a new day, clear the rainfall total
# if int(current_day.strftime("%w")) != int(previous_day.strftime("%w)):
#     reset_rainfall()
#     previous_day = current_day


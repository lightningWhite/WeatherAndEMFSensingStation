# Argent Rain Sensor
# 
# Reports the rainfall in inches
#
# Ensure the following connections to the Raspberry Pi 3 Model B:
# 
# Pin 2 on the RJ11 connector to Ground
# Pin 4 on the RJ11 connector to BCM 6

from gpiozero import Button

rain_sensor = Button(6)
BUCKET_SIZE = 0.011 # inches per bucket tip
count = 0

def bucket_tipped():
    global count
    count = count + 1
    print (count * BUCKET_SIZE)

def reset_rainfall():
    global count
    count = 0

while True:
    rain_sensor.when_pressed = bucket_tipped


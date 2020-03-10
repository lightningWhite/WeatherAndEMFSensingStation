from gpiozero import Button

wind_speed_sensor = Button(5)
wind_count = 0

def spin():
    global wind_count
    wind_count = wind_count + 1
    print("spin" + str(wind_count))

# This won't be in a while loop here
while 1:
    wind_speed_sensor.when_pressed = spin

# TODO: Finish this


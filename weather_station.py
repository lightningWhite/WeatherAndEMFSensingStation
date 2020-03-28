from gpiozero import Button
import bme280_sensor
import database
import datetime
import math
import statistics
import time
import wind_direction

# How often the sensor readings should be logged
LOG_INTERVAL = 15 #900 # 15 Minutes in seconds

# How often readings should be taken to form the average that will be logged
ACCUMULATION_INTERVAL = 5 #180 # 3 minuntes

###############################################################################
# Anemometer
###############################################################################

CM_IN_A_MILE = 160934.4
SECS_IN_AN_HOUR = 3600
# Calibration factor used to report the correct wind speed
WIND_CALIBRATION = 2.3589722140805094
RADIUS_CM = 9.0 # Radius of the anemometer

wind_speed_sensor = Button(5) # BCM 5
wind_count = 0        # Number of half rotations for calculating wind speed
store_speeds = []     # Store speeds in order to record wind gusts
store_directions = [] # Store directions to calculate the avg direction

def reset_wind():
    global wind_count
    wind_count = 0

def spin():
    global wind_count
    wind_count = wind_count + 1

def calculate_speed(time_sec):
    global wind_count
    circumference_cm = (2 * math.pi) * RADIUS_CM
    rotations = wind_count / 2.0

    # Calcuate the distance travelled by a cup in cm
    dist_mile = (circumference_cm * rotations) / CM_IN_A_MILE

    # Report the wind speed in miles per hour
    miles_per_sec = dist_mile / time_sec
    miles_per_hour = miles_per_sec * SECS_IN_AN_HOUR

    # Clear the wind count so it will be ready for the next reading
    reset_wind()

    # The anemometer data sheet indicates that if the switch closes once per
    # second, a wind speed of 1.492 MPH should be reported
    # Multiply by the calibration factor to be accurate according to the
    # data sheet
    return miles_per_hour * WIND_CALIBRATION


# Call the spin function every half rotation
wind_speed_sensor.when_pressed = spin


###############################################################################
# Rain Guage
###############################################################################

BUCKET_SIZE = 0.011 # Inches per bucket tip

previous_day = datetime.datetime.now()

rain_sensor = Button(6)
rain_count = 0
precipitation = 0

def bucket_tipped():
    global rain_count
    global precipitation
    rain_count = rain_count + 1
    precipitation = rain_count * BUCKET_SIZE
    print("tipped")

def reset_rainfall():
    global rain_count
    rain_count = 0

rain_sensor.when_pressed = bucket_tipped

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


###############################################################################
# Main Program Loop
###############################################################################

# TODO: Remove temp
temp = 0

while True:
    start_time = time.time()

    # Accumulate wind direction and wind speeds every ACCUMULATION_INTERVAL
    # seconds, and log the averages every LOG_INTERVAL
    while time.time() - start_time <= LOG_INTERVAL:

        # Sample the wind directions for the duration of ACCUMULATION_INTERVAL
        # This is how we accumulate readings every ACCUMULATION_INTERVAL
        store_directions.append(wind_direction.get_value(ACCUMULATION_INTERVAL))

        # The speed will be calculated after the wind direction avg is obtained
        store_speeds.append(calculate_speed(ACCUMULATION_INTERVAL))

    # Log the wind gust and the average speed over the LOG_INTERVAL
    wind_gust = max(store_speeds)
    wind_speed = statistics.mean(store_speeds)
    # wind_direction = statistics.mean(store_directions)
    humidity, pressure, ambient_temp = bme280_sensor.read_all()
    current_time = datetime.datetime.now()

    print(f"Time: {current_time}")
    print(f"Avg. Wind Speed: {wind_speed}")
    print(f"Wind Gust:       {wind_gust}")
    # print(f"Wind Direction:  {wind_direction}")
    print(f"Precipitation:   {precipitation}")
    print(f"Humidity:        {humidity}")
    print(f"Pressure (mbar): {pressure}")
    print(f"Temperature (F): {ambient_temp}")

    # Clear the recorded speeds so the gust can be updated during the next log period
    store_speeds.clear()
    store_directions.clear()

    # Clear the rainfall each day at midnight
    # When it's a new weekday, clear the rainfall total
    if int(current_time.strftime("%w")) != int(previous_day.strftime("%w")):
        # TODO: Remove temp
        if temp > 4:
            reset_rainfall()
            previous_day = current_day
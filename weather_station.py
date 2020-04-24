from gpiozero import Button
import bme280_sensor
import datetime
import emf
import math
import os
import pyranometer
from pathlib import Path
import statistics
import time
import wind_direction

# TODO: Adjust the log interval when done testing

# How often the sensor readings should be logged
LOG_INTERVAL = 9 #15 #900 # 15 Minutes in seconds

# How often readings should be taken to form the average that will be logged
ACCUMULATION_INTERVAL = 3 #5 #180 # 3 minuntes in seconds

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
precipitation = 0.0

def bucket_tipped():
    global rain_count
    global precipitation
    rain_count = rain_count + 1
    precipitation = round(rain_count * BUCKET_SIZE, 4)

def reset_rainfall():
    global rain_count
    global precipitation
    rain_count = 0
    precipitation = 0.0

rain_sensor.when_pressed = bucket_tipped


###############################################################################
# Main Program Loop
###############################################################################

# Create a new file named by the current date and time
data_file = os.getcwd() + "/" +  "data" + "/" + datetime.datetime.now().strftime("%m-%d-%Y--%H-%M-%S") + ".data"
if not os.path.exists(os.path.dirname(data_file)):
    try:
        os.makedirs(os.path.dirname(data_file))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

with open(data_file, "w") as file:
    # Write the labels row
    file.write("Record Number, Time, Temperature (F), Pressure (mbar), " \
               "Humidity (%), Wind Direction (Degrees), Wind Direction (String), " \
               "Wind Speed (MPH), Wind Gust (MPH), Precipitation (Inches), " \
               "Shortwave Radiation (W m^(-2)), Avg. RF Watts (W), " \
               "Avg. RF Frequency (MHz), Peak RF Watts (W), " \
               "Frequency of RF Watts Peak (MHz), Peak RF Frequency (MHz), " \
               "Watts of RF Frequency Peak (W), Avg. EF (V/m), Max. EF (V/m), " \
               "Avg. EMF (mG), Max. EMF (mG)\n")
    
# TODO: Remove temp for resetting the rain after midnight
temp = 0

record_number = 1

###############################################################################
# The main program loop
###############################################################################
while True:
    start_time = time.time()

    store_directions = []
    store_speeds = []
    store_rf_watts = []
    store_rf_watts_frequencies = []
    store_ef_volts_per_meter = []
    store_emf_milligauss = []
    rf_watts = 0.0
    rf_watts_mhz_frequency = 0.0
    ef_volts_per_meter = 0.0
    emf_milligauss = 0.0

    # Accumulate wind direction and wind speeds every ACCUMULATION_INTERVAL
    # seconds, and log the averages every LOG_INTERVAL
    while time.time() - start_time <= LOG_INTERVAL:

        store_directions.append(wind_direction.get_current_angle())
        store_speeds.append(calculate_speed(ACCUMULATION_INTERVAL))
        
        rf_watts, rf_watts_mhz_frequency, ef_volts_per_meter, emf_milligauss = emf.get_emf()
        store_rf_watts.append(rf_watts) 
        store_rf_watts_frequencies.append(rf_watts_mhz_frequency)
        store_ef_volts_per_meter.append(ef_volts_per_meter)
        store_emf_milligauss.append(emf_milligauss)

        time.sleep(ACCUMULATION_INTERVAL)

    # Obtain the wind gust and the average speed over the LOG_INTERVAL
    wind_gust = round(max(store_speeds), 1)
    wind_speed = round(statistics.mean(store_speeds), 1)

    # Obtain the average wind direction over the LOG_INTERVAL 
    # TODO: Make sure the precision is right
    wind_direction_avg = wind_direction.get_average(store_directions)
    wind_direction_string = wind_direction.get_direction_as_string(wind_direction_avg)

    # Obtain the current humidity, pressure, and ambient temperature
    humidity, pressure, ambient_temp = bme280_sensor.read_all()

    # Obtain the current shortwave radiation
    shortwave_radiation = pyranometer.get_shortwave_radiation()

    # Obtain the max RF watts value and its associated frequency
    rf_watts_peak = max(store_rf_watts)
    frequency_of_rf_watts_peak = round(store_rf_watts_frequencies[store_rf_watts.index(max(store_rf_watts))], 1)

    # Obtain the max RF frequency and its associated power (watts)
    rf_frequency_peak = max(store_rf_watts_frequencies)
    watts_of_rf_frequency_peak = round(store_rf_watts[store_rf_watts_frequencies.index(max(store_rf_watts_frequencies))], 1)

    # Obtain the average RF power and the average frequency
    rf_watts_avg = statistics.mean(store_rf_watts)
    rf_freq_avg = round(statistics.mean(store_rf_watts_frequencies), 1)

    # Obtain the average and max EF values
    ef_volts_per_meter_avg = round(statistics.mean(store_ef_volts_per_meter), 1)
    ef_volts_per_meter_max = round(max(store_ef_volts_per_meter), 1)

    # Obtain the average and max EMF values
    emf_milligauss_avg = round(statistics.mean(store_emf_milligauss), 1)
    emf_milligauss_max = round(max(store_emf_milligauss), 1)

    current_time = datetime.datetime.now()

    print(f"Record Number:                    {record_number}")
    print(f"Time:                             {current_time}")
    print(f"Temperature (F):                  {ambient_temp}")
    print(f"Pressure (mbar):                  {pressure}")
    print(f"Humidity (%):                     {humidity}")
    print(f"Wind Direction (Degrees):         {wind_direction_avg}")
    print(f"Wind Direction (String):          {wind_direction_string}")
    print(f"Avg. Wind Speed (MPH):            {wind_speed}")
    print(f"Wind Gust (MPH):                  {wind_gust}")
    print(f"Precipitation (Inches):           {precipitation}")
    print(f"Shortwave Radiation (W m^-2):     {shortwave_radiation}")
    print(f"Avg. RF Watts (W):                {rf_watts_avg:.16f}")
    print(f"Avg. RF Frequency (MHz):          {rf_freq_avg}")
    print(f"Peak RF Watts (W):                {rf_watts_peak:.16f}")
    print(f"Frequency of RF Watts Peak (MHz): {frequency_of_rf_watts_peak}")
    print(f"Peak RF Frequency (MHz):          {rf_frequency_peak}")
    print(f"Watts of RF Frequency Peak (W):   {watts_of_rf_frequency_peak:.16f}")
    print(f"Avg. EF (V/m):                    {ef_volts_per_meter_avg}")
    print(f"Max. EF (V/m):                    {ef_volts_per_meter_max}")
    print(f"Avg. EMF (mG):                    {emf_milligauss_avg}")
    print(f"Max. EMF (mG):                    {emf_milligauss_max}")

    print("######################################################")

    # Log the data by appending the values to the data .csv file
    with open(data_file, "a") as file:
        file.write(f"{record_number}, {current_time}, {ambient_temp}, {pressure}, " \
                   f"{humidity}, {wind_direction_avg}, {wind_direction_string}, " \
                   f"{wind_speed}, {wind_gust}, {precipitation}, " \
                   f"{shortwave_radiation}, {rf_watts_avg:.16f}, {rf_freq_avg}, " \
                   f"{rf_watts_peak:.16f}, {frequency_of_rf_watts_peak}, " \
                   f"{rf_frequency_peak}, {watts_of_rf_frequency_peak:.16f}, " \
                   f"{ef_volts_per_meter_avg}, {ef_volts_per_meter_max}, " \
                   f"{emf_milligauss_avg}, {emf_milligauss_max},\n")

    # Clear the recorded values so they can be updated over the next LOG_INTERVAL
    store_speeds.clear()
    store_directions.clear()
    store_rf_watts.clear()
    store_rf_watts_frequencies.clear() 
    store_ef_volts_per_meter.clear()
    store_emf_milligauss.clear()


    # Clear the rainfall each day at midnight
    # When it's a new weekday, clear the rainfall total
    # if int(current_time.strftime("%w")) != int(previous_day.strftime("%w")):
    # TODO: Remove temp
    if temp > 0:
        print("Resetting precipitation")
        reset_rainfall()
        previous_day = current_time
        temp = 0
    temp = temp + 1

    record_number = record_number + 1


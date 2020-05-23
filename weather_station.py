from gpiozero import Button
import bme280_sensor
import datetime
import emf
import logging
import math
import os
import pyranometer
from pathlib import Path
import statistics
import subprocess
import sys
import time
import wind_direction

# How often the sensor readings should be logged
LOG_INTERVAL = 900 # 15 Minutes in seconds

# How often readings should be taken to form the average that will be logged
ACCUMULATION_INTERVAL = 10 # 10 seconds


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
    logging.log("Calculating the wind speed")
    global wind_count
    circumference_cm = (2 * math.pi) * RADIUS_CM
    rotations = wind_count / 2.0

    # Calculate the distance travelled by a cup in cm
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
# Rain Gauge
###############################################################################

BUCKET_SIZE = 0.011 # Inches per bucket tip

previous_day = datetime.datetime.now()

rain_sensor = Button(6)
rain_count = 0
precipitation = 0.0

def bucket_tipped():
    logging.log("Detected a rainfall bucket tip")
    global rain_count
    global precipitation
    rain_count = rain_count + 1
    precipitation = round(rain_count * BUCKET_SIZE, 4)

def reset_rainfall():
    logging.log("Resetting the accumulated rainfall")
    global rain_count
    global precipitation
    rain_count = 0
    precipitation = 0.0

rain_sensor.when_pressed = bucket_tipped


###############################################################################
# Main Program Loop
###############################################################################

# Create a new file named by the current date and time
time_name = datetime.datetime.now().strftime("%m-%d-%Y--%H-%M-%S")
data_file = "/home/pi/WeatherStation" + "/" +  "data" + "/" + time_name + ".csv"

logging.initialize_logger(f"/home/pi/WeatherStation/logs/{time_name}.log")

logging.log("The weather and emf sensing station has been started")
logging.log(f"Readings will be accumulated every {ACCUMULATION_INTERVAL} seconds")
logging.log(f"The data will be written every {LOG_INTERVAL} seconds")
logging.log(f"The data file is located here: {data_file}")

try:
    if not os.path.exists(os.path.dirname(data_file)):
        try:
            os.makedirs(os.path.dirname(data_file))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    
    with open(data_file, "w") as file:
        # Write the labels row
        file.write("Record Number, " \
                   "Time, " \
                   "Temperature (F), " \
                   "Pressure (mbar), " \
                   "Humidity (%), " \
                   "Wind Direction (Degrees), " \
                   "Wind Direction (String), " \
                   "Wind Speed (MPH), " \
                   "Wind Gust (MPH), " \
                   "Precipitation (Inches), " \
                   "Shortwave Radiation (W m^(-2)), " \
                   "Avg. RF Watts (W), " \
                   "Avg. RF Watts Frequency (MHz), " \
                   "Peak RF Watts (W), " \
                   "Frequency of RF Watts Peak (MHz), "\
                   "Peak RF Watts Frequency (MHz), " \
                   "Watts of RF Watts Frequency Peak (W), " \
                   "Avg. RF Density (W m^(-2)), " \
                   "Avg. RF Density Frequency (MHz), " \
                   "Peak RF Density (W m^(-2)), " \
                   "Frequency of RF Density Peak (MHz), "\
                   "Peak RF Density Frequency (MHz), " \
                   "Density of RF Density Frequency Peak (W m^(-2)), " \
                   "Avg. Total Density (W m^(-2)), " \
                   "Max Total Density (W m^(-2)), " \
                   "Avg. EF (V/m), " \
                   "Max EF (V/m), " \
                   "Avg. EMF (mG), " \
                   "Max EMF (mG)\n")
        
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
        store_rf_density = []
        store_rf_density_frequencies = []
        store_rf_total_density = []
        store_ef_volts_per_meter = []
        store_emf_milligauss = []
        rf_watts = 0.0
        rf_watts_mhz_frequency = 0.0
        rf_density = 0.0
        rf_density_frequency = 0.0
        rf_total_density = 0.0
        ef_volts_per_meter = 0.0
        emf_milligauss = 0.0
    
        # Accumulate wind direction and wind speeds every ACCUMULATION_INTERVAL
        # seconds, and log the averages every LOG_INTERVAL
        logging.log("Accumulating the sensor readings")
        while time.time() - start_time <= LOG_INTERVAL:
            bad_values = False

            store_directions.append(wind_direction.get_current_angle())
            store_speeds.append(calculate_speed(ACCUMULATION_INTERVAL))
            
            try:
                rf_watts, rf_watts_mhz_frequency, rf_density, rf_density_frequency, rf_total_density, ef_volts_per_meter, emf_milligauss = emf.get_emf()
            except Exception as e:
                logging.log(str(e.args))
                logging.log("Not accumulating the EMF sensor values because getting the values raised an exception")
                bad_values = True

            if not bad_values: 
                store_rf_watts.append(rf_watts) 
                store_rf_watts_frequencies.append(rf_watts_mhz_frequency)
                store_rf_density.append(rf_density)
                store_rf_density_frequencies.append(rf_density_frequency)
                store_rf_total_density.append(rf_total_density)
                store_ef_volts_per_meter.append(ef_volts_per_meter)
                store_emf_milligauss.append(emf_milligauss)
    
            time.sleep(ACCUMULATION_INTERVAL)
    
        # If any of the EMF lists are empty, they all are. Set the EMF sensor values to -1.
        if len(store_rf_watts) == 0:
            logging.log("Setting the EMF values to -1 because no values were obtained from the sensor over the log period")
            store_rf_watts.append(-1) 
            store_rf_watts_frequencies.append(-1)
            store_rf_density.append(-1)
            store_rf_density_frequencies.append(-1)
            store_rf_total_density.append(-1)
            store_ef_volts_per_meter.append(-1)
            store_emf_milligauss.append(-1)

        # Obtain the wind gust and the average speed over the LOG_INTERVAL 
        wind_gust = round(max(store_speeds), 1)
        wind_speed = round(statistics.mean(store_speeds), 1)
    
        # Obtain the average wind direction over the LOG_INTERVAL 
        wind_direction_avg = round(wind_direction.get_average(store_directions), 1)
        wind_direction_string = wind_direction.get_direction_as_string(wind_direction_avg)
    
        # Obtain the current humidity, pressure, and ambient temperature
        logging.log("Obtaining the humidity, pressure, and temperature readings from the bme280 sensor")
        humidity, pressure, ambient_temp = bme280_sensor.read_all()
    
        # Obtain the current shortwave radiation
        logging.log("Obtaining the shortwave radiation value from the pyranometer")
        shortwave_radiation = pyranometer.get_shortwave_radiation()
   
        logging.log("Calculating the max, peak, and averages of the EMF data")
    
        # Obtain the max RF watts value and its associated frequency
        rf_watts_peak = max(store_rf_watts)
        frequency_of_rf_watts_peak = round(store_rf_watts_frequencies[store_rf_watts.index(max(store_rf_watts))], 1)
    
        # Obtain the max RF watts frequency and its associated power (watts)
        rf_watts_frequency_peak = max(store_rf_watts_frequencies)
        watts_of_rf_watts_frequency_peak = store_rf_watts[store_rf_watts_frequencies.index(max(store_rf_watts_frequencies))]
    
        # Obtain the average RF power and the average frequency
        rf_watts_avg = statistics.mean(store_rf_watts)
        rf_watts_frequency_avg = round(statistics.mean(store_rf_watts_frequencies), 1)
    
    
        # Obtain the max RF density value and its associated frequency
        rf_density_peak = max(store_rf_density)
        frequency_of_rf_density_peak = round(store_rf_density_frequencies[store_rf_density.index(max(store_rf_density))], 1)
    
        # Obtain the max RF density frequency and its associated density (W m^-2)
        rf_density_frequency_peak = max(store_rf_density_frequencies)
        density_of_rf_density_frequency_peak = store_rf_density[store_rf_density_frequencies.index(max(store_rf_density_frequencies))]
    
        # Obtain the average RF power density and the average frequency
        rf_density_avg = statistics.mean(store_rf_density)
        rf_density_frequency_avg = round(statistics.mean(store_rf_density_frequencies), 1)
    
    
        # Obtain the average and max RF total density value
        rf_total_density_avg = statistics.mean(store_rf_total_density)
        rf_total_density_max = max(store_rf_total_density)
    
    
        # Obtain the average and max EF values
        ef_volts_per_meter_avg = round(statistics.mean(store_ef_volts_per_meter), 1)
        ef_volts_per_meter_max = round(max(store_ef_volts_per_meter), 1)
    
    
        # Obtain the average and max EMF values
        emf_milligauss_avg = round(statistics.mean(store_emf_milligauss), 1)
        emf_milligauss_max = round(max(store_emf_milligauss), 1)
    
        # This will pull from the Real Time Clock so it can be accurate
        # when there isn't an internet connection. See the readme for
        # instructions on how to configure the Real Time Clock correctly.
        current_time = datetime.datetime.now()
        
        logging.log("Printing the values obtained and calculated")
    
        print(f"Record Number:                                 {record_number}")
        print(f"Time:                                          {current_time}")
    
        # Weather
        print(f"Temperature (F):                               {ambient_temp}")
        print(f"Pressure (mbar):                               {pressure}")
        print(f"Humidity (%):                                  {humidity}")
        print(f"Wind Direction (Degrees):                      {wind_direction_avg}")
        print(f"Wind Direction (String):                       {wind_direction_string}")
        print(f"Avg. Wind Speed (MPH):                         {wind_speed}")
        print(f"Wind Gust (MPH):                               {wind_gust}")
        print(f"Precipitation (Inches):                        {precipitation}")
        print(f"Shortwave Radiation (W m^-2):                  {shortwave_radiation}")
    
        # RF Watts
        print(f"Avg. RF Watts (W):                             {rf_watts_avg:.16f}")
        print(f"Avg. RF Watts Frequency (MHz):                 {rf_watts_frequency_avg}")
        print(f"Peak RF Watts (W):                             {rf_watts_peak:.16f}")
        print(f"Frequency of RF Watts Peak (MHz):              {frequency_of_rf_watts_peak}")
        print(f"Peak RF Watts Frequency (MHz):                 {rf_watts_frequency_peak}")
        print(f"Watts of RF Watts Frequency Peak (W):          {watts_of_rf_watts_frequency_peak:.16f}")
    
        # RF Density
        print(f"Avg. RF Density (W m^-2):                      {rf_density_avg:.16f}")
        print(f"Avg. RF Density Frequency (MHz):               {rf_density_frequency_avg}")
        print(f"Peak RF Density (W m^-2):                      {rf_density_peak:.16f}")
        print(f"Frequency of RF Density Peak (MHz):            {frequency_of_rf_density_peak}")
        print(f"Peak RF Density Frequency (MHz):               {rf_density_frequency_peak}")
        print(f"Density of RF Density Frequency Peak (W m^-2): {density_of_rf_density_frequency_peak:.16f}")
    
        # RF Total Density 
        print(f"Avg. RF Total Density (W m^-2):                {rf_total_density_avg:.16f}")
        print(f"Max  RF Total Density (W m^-2):                {rf_total_density_max:.16f}")
    
        # EF
        print(f"Avg. EF (V/m):                                 {ef_volts_per_meter_avg}")
        print(f"Max  EF (V/m):                                 {ef_volts_per_meter_max}")
    
        # EMF
        print(f"Avg. EMF (mG):                                 {emf_milligauss_avg}")
        print(f"Max  EMF (mG):                                 {emf_milligauss_max}")
    
        print("##########################################################################")
        
        logging.log(f"Writing the data to {data_file}")
    
        # Log the data by appending the values to the data .csv file
        with open(data_file, "a") as file:
            file.write(f"{record_number}, {current_time}, {ambient_temp}, {pressure}, " \
                       f"{humidity}, {wind_direction_avg}, {wind_direction_string}, " \
                       f"{wind_speed}, {wind_gust}, {precipitation}, " \
                       f"{shortwave_radiation}, {rf_watts_avg:.16f}, {rf_watts_frequency_avg}, " \
                       f"{rf_watts_peak:.16f}, {frequency_of_rf_watts_peak}, " \
                       f"{rf_watts_frequency_peak}, {watts_of_rf_watts_frequency_peak:.16f}, " \
                       f"{rf_density_avg:.16f}, {rf_density_frequency_avg}, " \
                       f"{rf_density_peak:.16f}, {frequency_of_rf_density_peak}, " \
                       f"{rf_density_frequency_peak}, {density_of_rf_density_frequency_peak:.16f}, " \
                       f"{rf_total_density_avg:.16f}, {rf_total_density_max:.16f}, " \
                       f"{ef_volts_per_meter_avg}, {ef_volts_per_meter_max}, " \
                       f"{emf_milligauss_avg}, {emf_milligauss_max}\n")
    
        # Check if an external USB storage device is connected
        check_external_drive = subprocess.Popen(
            'df -h | grep /dev/sda1',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)    
        stdout, stderr = check_external_drive.communicate()
    
        # Copy the newly written file to the external USB drive if one is connected
        if len(stdout) > 0:
            file_name = time_name + '.csv'
            backup_name = time_name + '.csv' + '.bak'
            logging.log(f"Backing up the data to /mnt/usb1/{file_name}")
            
            # Change the name of the last backup so we don't overwrite it until
            # the latest backup is obtained
            rename_old_backup_data = subprocess.Popen(
                f"mv /mnt/usb1/{file_name} /mnt/usb1/{backup_name}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            stdout, stderr = rename_old_backup_data.communicate()
    
            # Get the latest data file to the external drive
            backup_data = subprocess.Popen(
                f"cp {data_file} /mnt/usb1/{file_name}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            stdout, stderr = backup_data.communicate()
        else:
            print("WARNING: The data is not being backed up. Ensure an external storage device is connected.")
            logging.log("WARNING: The data is not being backed up. Ensure an external storage device is connected.")
    
        # Clear the recorded values so they can be updated over the next LOG_INTERVAL
        store_speeds.clear()
        store_directions.clear()
        store_rf_watts.clear()
        store_rf_watts_frequencies.clear() 
        store_rf_density.clear()
        store_rf_density_frequencies.clear()
        store_rf_total_density.clear()
        store_ef_volts_per_meter.clear()
        store_emf_milligauss.clear()
    
        # Clear the rainfall each day at midnight
        # When it's a new weekday, clear the rainfall total
        if int(current_time.strftime("%w")) != int(previous_day.strftime("%w")):
            print("Resetting the accumulated rainfall")
            reset_rainfall()
            previous_day = current_time
    
        record_number = record_number + 1

except Exception as e:
    logging.log("An unhandled exception occurred causing a crash: " + str(e.args))


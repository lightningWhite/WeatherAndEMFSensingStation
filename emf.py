# EMF-390 Sensor
#
# Uses the EMF-390 sensor to read the following:
# - Radio Frequency Watts
# - Radio Frequency of the Watts value (MHz)
# - Radio Frequency Density and the associated frequency (W m^-2)
# - Radio Frequency Total Density (W m^-2)
# - Electric Field (V/m)
# - Electromagnetic Field (mG)
#
# Note that the reading for each value may occur at a different time. This
# means that the Watts value reported may not be the Watts value used in
# the calculation of the power density. This may be an artifact of the
# emf390cli tool sampling each reading individually.

import subprocess


def to_MHz(frequency, unit):
    """
    Given a freqeuncy and a unit, convert the frequency to MHz
    """

    if unit == 'Hz':
        return frequency / 1000000
    elif unit == 'kHz':
        return frequency / 1000
    elif unit == 'MHz':
        return frequency
    elif unit == 'GHz':
        return frequency * 1000


def get_rf_watts_and_mhz_frequency(rf_watts_words):
    """
    Return the RF watts value and the frequency in MHz
    """
   
    rf_watts = rf_watts_words[1]
    rf_watts_frequency = rf_watts_words[4]
    rf_watts_units = rf_watts_words[5].strip()

    rf_watts_mhz_frequency = to_MHz(rf_watts_frequency, rf_watts_units) 

    return rf_watts, rf_watts_mhz_frequency


def get_rf_density_and_mhz_frequency(rf_density_words):
    """
    Return the RF density value in W m^-2 and the frequency in MHz
    """
   
    rf_density = rf_density_words[1]
    rf_density_frequency = rf_density_words[4]
    rf_density_units = rf_density_words[5].strip()

    rf_density_mhz_frequency = to_MHz(rf_density_frequency, rf_density_units) 

    return rf_density, rf_density_mhz_frequency


def get_total_rf_density(rf_total_density_words):
    """
    Return the RF total density value in W m^-2 and the frequency in MHz
    """
  
    rf_total_density = rf_total_density_words[1]

    return rf_total_density


def get_serial_port():
    """
    Determine which USB serial port the device is plugged into since there
    may be other devices plugged into the USB ports.
    This will throw if no successful connection can be established.
    
    WARNING: This function is probably very buggy. I added it because on
    occasion the device may be /dev/ttyUSB0 and at other times it may show
    up as /dev/ttyUSB1. I don't know if this would change if there are
    other USB devices connected or not, such as an external hard drive.
    """ 

    # List the connected USB devices
    command = subprocess.Popen(
        'ls /dev/ttyUSB*',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)    

    # Obtain the output from the command
    stdout, stderr = command.communicate()

    # Convert the terminal output from bytes to utf-8
    output = stdout.decode('utf-8')

    # Place each outputted device into a list
    USBDevices = output.split('\n')

    # Remove the empty entry after splitting by '\n'
    USBDevices.remove('')

    # Attempt to connect to each device to determine which one works
    for device in USBDevices:
        try:
            command = subprocess.Popen([
                '/home/pi/WeatherStation/em390cli/build/arm-linux/emf390cli',
                '-p',
                device,
                '-f',
                '%w%d%e%t%k%E%M',
                '--csv'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            
            # Obtain the output from the command
            stdout, stderr = command.communicate()
        
            # Convert the terminal output from bytes to utf-8
            test_output = stdout.decode('utf-8')
            if len(test_output) > 0:
                test_output = test_output.split(', ')

                # The first word of the output should be rfwatts
                if test_output[0] == 'rfwatts':
                    # This is the device, return it
                    return device
        
        except:
            pass

    # If it gets here, no successful connection could be established 
    raise Exception('The EMF sensor may not be on or connected correctly. Exiting.')
    

def get_emf():

    # Get the serial port that the emf sensor is connected to
    try:
        USBDevice = get_serial_port()
    except Exception as e:
        print(e)
        exit(1)
        
    # Run the emf390cli application to obtain the EMF-390 sensor readings
    command = subprocess.Popen([
        '/home/pi/WeatherStation/em390cli/build/arm-linux/emf390cli',
        '-p',
        USBDevice,
        '-f',
        '%w%d%e%t%k%E%M',
        '--csv'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    # Obtain the output from the command
    stdout, stderr = command.communicate()

    # Convert the readings from bytes to utf-8
    readings = stdout.decode('utf-8')

    # Separate the output into separate lines
    lines = readings.split('\n')

    # Put the words of each line of interest into lists
    rf_watts_words = lines[0].split(', ')
    rf_density_words = lines[2].split(', ')
    rf_total_density_words = lines[3].split(', ')
    ef_words = lines[5].split(', ')
    emf_words = lines[6].split(', ')
   
    # Obtain the values of interest
    rf_watts, rf_watts_mhz_frequency = get_rf_watts_and_mhz_frequency(rf_watts_words)
    rf_density, rf_density_mhz_frequency = get_rf_density_and_mhz_frequency(rf_density_words)
    rf_total_density = get_total_rf_density(rf_total_density_words)
    ef_volts_per_meter = ef_words[1] 
    emf_milligauss = emf_words[1] 

    #print(f'rf_watts: {rf_watts}')
    #print(f'rf_watts_mhz_frequency: {rf_watts_mhz_frequency}')
    #print(f'ef_volts_per_meter: {ef_volts_per_meter}')
    #print(f'emf_milligauss: {emf_milligauss}')


    return float(rf_watts), float(rf_watts_mhz_frequency), \
           float(rf_density), float(rf_density_mhz_frequency), \
           float(rf_total_density), float(ef_volts_per_meter), \
           float(emf_milligauss)

#print(get_emf())


# rfwatts, 0.000000000158, 158, pW, 672, MHz
# rfdbm, -68, -68, dbm, 672, MHz
# rfdensity, 0.0001, 0.1, mW/m2, 672, MHz
# rftotaldensity, 0.06720000000000001, 67.2, mW/m2, 0, n/a
# rftotaldensitypeak, 0.6354, 635.4, mW/m2, 0, n/a
# ef, 11.8, 11.8, V/m, 0, n/a
# emf, 0.6, 0.6, mG, 0, n/a
# 
# 
# 
# RF Watts (W), RF Watts Frequency (MHz), RF dBm (dBm), RF dBm Frequency (MHz), RF Density (W/m2), RF Density Frequency (MHz), RF Total Density (W/m2), RF Total Density 15 min Peak (W/m2), EF (V/m), EMF (mG)
# 
# 
# A few notes:
# 
# rfwatts and rfdbm are different forms of the same number. The problem is that it appears
# that they are calculated sequentially. This means that the readings of the sensor may be
# different for each reading. This is no bueno. They should not contradict each other. I
# will probably want to take one or the other and then convert it to the other form if it's
# desirable to have both. Or I could just use one or the other. I may need to look into the
# rfdensity, because it's likely directly tied to the reading.
# 
# When I start preprocessing the data, I will probably want to look into binning the data.
# Since the frequency is directly related to the power (magnitude of the wave), I probably
# don't want those to be treated as independent values when machine learning with them.
# What I may end up doing is grouping the power readings into categories of common frequencies
# like 0-400MHz, 401-999MHz, 1000-3000MHz, etc. and then put the power values in each category.
# I can do that later though after I gather the data and know what binnings make the most sense.
# 
# The power density value obtained from the sensor is calculated using this formula:
# Power Density = (Pout * Gain) / (4 * PI * Distance^2)
# 
# The gain used by the sensor for the antennae is 10. The distance we calculated to be
# 0.0011213046 by solving for D when a Power Density was given. Pout is the rfwatts reading.
# 
# Since the gain and the distance is hard coded, it is not the value of a tower or something.
# It is just a relative value at the current location.
# 
# We aren't sure how the total power density is being calculated. It might be some sort of sum.
# 
# This forum is helpful: https://www.gqelectronicsllc.com/forum/forum.asp?FORUM_ID=18

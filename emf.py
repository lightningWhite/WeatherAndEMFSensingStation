# EMF-390 Sensor
#
# Uses the EMF-390 sensor to read 
#
#

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


def get_rfwatts_and_mhz_frequency(rf_watts_words):
    """
    Return the watts value and the frequency in MHz
    """
   
    rf_watts = rf_watts_words[1]
    rf_watts_frequency = rf_watts_words[4]
    rf_watts_units = rf_watts_words[5].strip()

    rf_watts_mhz_frequency = to_MHz(rf_watts_frequency, rf_watts_units) 

    return rf_watts, rf_watts_mhz_frequency


def get_emf():

    # Run the emf390cli application to obtain the EMF-390 sensor readings
    command = subprocess.Popen([
        './em390cli/build/arm-linux/emf390cli',
        '-p',
        '/dev/ttyUSB0',
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
    ef_words = lines[5].split(', ')
    emf_words = lines[6].split(', ')
   
    # Obtain the values of interest
    rf_watts, rf_watts_mhz_frequency = get_rfwatts_and_mhz_frequency(rf_watts_words)
    ef_volts_per_meter = ef_words[1] 
    emf_milligauss = emf_words[1] 

    print(f'rf_watts: {rf_watts}')
    print(f'rf_watts_mhz_frequency: {rf_watts_mhz_frequency}')
    print(f'ef_volts_per_meter: {ef_volts_per_meter}')
    print(f'emf_milligauss: {emf_milligauss}')


    return rf_watts, rf_watts_mhz_frequency, ef_volts_per_meter, emf_milligauss



get_emf()




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

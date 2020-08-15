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

import logger as logging
import subprocess
import sys

def to_MHz(frequency, unit):
    """
    Given a frequency and a unit, convert the frequency to MHz
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
    
    logging.log(f"USBDevices: {USBDevices}")

    # Attempt to connect to each device to determine which one works
    for device in USBDevices:
        try:
            logging.log(f"Attempting to connect to {device}")
            command = subprocess.Popen([
                '/home/pi/WeatherAndEMFSensingStation/em390cli/build/arm-linux/emf390cli',
                '-p',
                device,
                '-f',
                '%w%d%e%t%k%E%M',
                '--csv'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
          
            stdout = ""
            stderr = ""

            # Obtain the output from the command
            try:
                stdout, stderr = command.communicate(timeout=5)
            except:
                logging.log(f"Attempting to connect to {device} timed out. Exiting.")
                sys.exit(1)

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
    raise Exception('ERROR: The EMF sensor may not be on or connected correctly.')
    

def get_emf():

    # Get the serial port that the emf sensor is connected to
    try:
        logging.log("Obtaining the EMF device port")
        USBDevice = get_serial_port()
    except Exception as e:
        logging.log(e)
        sys.exit(1)
        
    # Run the emf390cli application to obtain the EMF-390 sensor readings
    logging.log("Obtaining the EMF sensor readings")
    command = subprocess.Popen([
        '/home/pi/WeatherAndEMFSensingStation/em390cli/build/arm-linux/emf390cli',
        '-p',
        USBDevice,
        '-f',
        '%w%d%e%t%k%E%M',
        '--csv'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    # Obtain the output from the command
    stdout = ""
    stderr = ""

    try:
        stdout, stderr = command.communicate(timeout=5)
    except:
        logging.log(f"Attempting to connect to {USBDevice} timed out. Exiting.")
        sys.exit(1)

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

    logging.log("Returning the EMF sensor readings")
    return float(rf_watts), float(rf_watts_mhz_frequency), \
           float(rf_density), float(rf_density_mhz_frequency), \
           float(rf_total_density), float(ef_volts_per_meter), \
           float(emf_milligauss)


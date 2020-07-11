# Preprocess Weather Data
#
# This file contains functions that can be used to clean up and preprocess
# the weather and EMF data. It removes unnecessary spaces after some of the
# commas in the CSV file, rounds the timestamps to the nearest quarter hour
# interval, and normalizes the data.


import csv
from datetime import datetime
from datetime import timedelta
import fileinput
import os
import shutil


def create_preprocessed_file(filename, preprocessed_filename):
    """
    Make a copy of the file and append a .bak to it's name.
    """
    shutil.copyfile(filename, preprocessed_filename)
    print(f"A a new file has been created and named {preprocessed_filename}")


def remove_spaces_after_commas(filename):
    """
    Removes unnecessary spaces after commas in a specified csv file.
    """
    text_to_search = ", "
    replacement_text = ","
    print("Replacing ', ' with ','")
    with fileinput.FileInput(filename, inplace=True) as file:
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')


def round_timestamps(filename):
    """
    Round the timestamps in a specified csv file to the nearest quarter hour
    interval starting from the hour (00, 15, 30, 45 minute endings).
    """
    print("Rounding timestamps to the nearest quarter hour increment...")
    # Make a temporary copy of the data file to read
    temp_filename = ".temp_reader_file"
    shutil.copyfile(filename, temp_filename)
    with open(temp_filename, newline='') as temp_reader_file:
        reader = csv.DictReader(temp_reader_file, delimiter=',')
        
        with open(filename, 'w', newline='') as csvfile_preprocessed:
            writer = csv.DictWriter(csvfile_preprocessed, fieldnames=reader.fieldnames)
            writer.writeheader()

            rounded_time = None
            previous = None
            zero_diff = 0
            thirty_diff = 0
            
            for row in reader:
                timestamp = datetime.strptime(row["Time"], "%Y-%m-%d %H:%M:%S.%f")
                
                # Round the time down
                floored_time = timestamp - timedelta(minutes=timestamp.minute % 15,
                                                     seconds=timestamp.second,
                                                     microseconds=timestamp.microsecond)
                
                # Get the difference between the actual time and the floored time
                time_diff = timestamp - floored_time

                # If the difference is over the half-way point, round upj
                if time_diff >= timedelta(minutes=7, seconds=30):
                    rounded_time = floored_time + timedelta(minutes=15)
                # Otherwise, round it down to the nearest 15 minute mark
                else:
                    rounded_time = floored_time

                # Write the row with the rounded time to the new csv file
                row["Time"] = rounded_time
                writer.writerow(row)

                # Count how many time gaps there are after rounding
                if previous:
                    if rounded_time - previous <= timedelta(minutes=0):
                        zero_diff += 1
                    elif rounded_time - previous > timedelta(minutes=15):
                        thirty_diff += 1
                
                # Update the previous time
                previous = rounded_time

            print(f"Duplicate Times: {zero_diff}")
            print(f"Time Gaps: {thirty_diff}")
    
    os.remove(temp_filename)

filename = "05-16-2020--16-23-44--present.csv"
preprocessed_filename = "05-16-2020--16-23-44--present--preprocessed.csv"

create_preprocessed_file(filename, preprocessed_filename)
remove_spaces_after_commas(preprocessed_filename)
round_timestamps(preprocessed_filename)
print("Done.")


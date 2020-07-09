import csv

print("Starting...")
with open('05-16-2020--16-23-44--present.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        print(row[" Time"])

print("Done.")


def remove_spaces_after_commas():
    with open('05-16-2020--16-23-44--present.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            print(row[" Time"])
   
    # Search and replace so I can get rid of the extra spaces in the file
    #import fileinput
    #
    #with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
    #    for line in file:
    #        print(line.replace(text_to_search, replacement_text), end='')


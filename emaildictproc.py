import pprint
import csv
import sys
import re

# Make Python ready to accept large field sizes:
csv.field_size_limit(sys.maxsize)

"""
Objectives:
1. Retrieving data from csv files and creating dictionaries.
2. Classifying the dictionaries.
3. Finding certain regular expressions.
"""

def read_csv_fieldnames(input_filename):
    """
    Inputs:
      csv filename
    Ouput:
      List of strings, each is a field name in the given CSV file.
    """
    print("Leyendo nombres de campos...")    
    # Open file and read text in file
    with open(input_filename, "r") as csvfile:
        reader = csv.DictReader(csvfile,
                               delimiter = ";",
                               quotechar = '"')
        reader.__next__()
        fieldnames = reader.fieldnames        
        for fieldname in fieldnames:
            print(fieldname)
    print("\n")
    return fieldnames

def csv_to_nesteddict(input_filename, keyfield):
    """
    Inputs:
        csv filename and keyfield
    Output:
        Returns a nested dictionary where the outer dictionary is a row in the CSV file.
        The inner dictionaries match the cells in that row to the field names.
    """
    nested_dict = {}
    
    # The keys in our dictionary will be the headers
    fieldnames = list(read_csv_fieldnames(input_filename))
    
    # Temporary list
    templist = []
    
    # Open file and read text
    with open(input_filename, "r") as csvfile:
        reader = csv.reader(csvfile,
                            delimiter = ";",
                            quotechar = '"')        

        for row in reader:
            rowlist = []
            for item in row:
                rowlist.append(item)
            templist.append(rowlist)
        
        for row in templist[1:]:  # Exclude the row with the field names
            if len(row) > 0:
                # Create an empty dictionary for each row
                row_dict = {}            
                for fieldname in fieldnames:
                    row_dict[fieldname] = row[fieldnames.index(fieldname)]                
                idx = row_dict[keyfield]
                nested_dict[idx] = row_dict
                        
    return nested_dict

test = csv_to_nesteddict("processedmails.csv", "id")
#pprint.pprint(test)

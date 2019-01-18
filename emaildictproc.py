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

def nesteddict_to_csv (input_dict, output_filename):
    """
    Objective: open a dictionary containing dictionaries and write it to a csv file
    Inputs:
        (1) dictionary containing dictionaries
        (2) output csv filename
    """
    print("\nCreando archivo", output_filename+"...")
    # Open (or create) csv file
    with open (output_filename, "w", encoding="utf8") as csvfile:
        writer = csv.writer (csvfile,
                             delimiter = ";",
                             quotechar = '"',
                             quoting = csv.QUOTE_MINIMAL)
        
        firstentry = input_dict[list(input_dict.keys())[1]]
        print ("Campos:", firstentry.keys())
        writer.writerow(firstentry.keys())
        
        for key in input_dict.keys():
            templist = []
            for field in input_dict[key]:
                templist.append((input_dict[key])[field])
            try:
                writer.writerow(templist)
            except:
                print("Corrección de codificación.")
                writer.writerow(templist.encode("utf8"))

    return None


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

# Test:
test = csv_to_nesteddict("processedmails.csv", "id")
#pprint.pprint(test)


def find_emails_in_body (input_dict):
    """
    Inputs:
        A dictionary where a field is a string.
    Objective:
        Find regular expressions that appear to be e-mails in a dictionary.
    Outputs:
        A dictionary where the key is the id in input_dict mapped to a set of e-mails.
        The dictionary is also exported as a csv file.
    """
    print("\nLos correos se analizarán a continuación.\n")
    searchfield = "body"    
    copiedfields = ("id", "from", "subject", "delivered-to", "year", "month", "day", "datetime")
    output_dict = {}
    
    for record in input_dict:
        # For each record a dictionary will be created 
        record_dict = {}
        
        # Original fields except the field we are searching is copied
        for field in copiedfields:
            record_dict[field] = input_dict[record][field]

        # A list with the searched expressions is created
        rawresults = list(
            re.findall("[0-9A-Za-z._]+@[0-9A-Za-z._]+\.[A-Za-z.]+",
                            input_dict[record][searchfield])
            )
#        print(rawresults, "\n")

        # The list is turned into a set which is then added to the dictionary
        result_set = set()        
        result_set.update(rawresults)
        record_dict["emails-in-body"] = result_set
        
        # The inner dictionary is appended to the outer dictionary
        output_dict[record_dict["id"]] = record_dict

        # Export findings to a csv file
        nesteddict_to_csv (output_dict, "emails_permessage.csv")
        
    return output_dict

# Test:
test2 = find_emails_in_body(test)
#pprint.pprint(test2)

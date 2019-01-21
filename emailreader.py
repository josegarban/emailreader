import pprint
import csv
import imaplib
import getpass
import urllib
from urllib import parse
from datetime import datetime
from datetime import timezone
import dateutil
from dateutil import parser
import email
from email.header import decode_header

"""
La contraseña no es la contraseña normal.
Se debe generar la contraseña en https://myaccount.google.com/security.
La opción es "contraseñas para aplicaciones" bajo "autenticación en dos pasos"
"""
####################################################################################################

def getcredentials():
    """
    Objective: obtaining e-mail and password in order to enter your e-mail
    """
    credentials = {}
    credentials["email"] = input ("Inserte correo electrónico:\n")
    print("Inserte contraseña: ")
    credentials["password"] = input("") 
    credentials["smtpserver"] = "imap.gmail.com"    
    return credentials

####################################################################################################

def readmail(credentials):
    """
    Objective: read your e-mails and process them
    Input: dictionary with credentials coming from user input to access their e-mail
    Output:
        (1) a nested dictionary with processed e-mails, where the inner dictionaries contain
            years, months and dates when the e-mail was sent
        (2) a nested dictionary with emails whose dates were not correctly processed
        (3) a list of e-mails that were not processed correctly
    
    """
    EMAIL      = credentials["email"]
    PASSWORD   = credentials["password"]
    SMTPSERVER = credentials["smtpserver"]
    
    try:
        print("Intentando acceder al correo...")
        mail = imaplib.IMAP4_SSL(SMTPSERVER)
        mail.login(EMAIL, PASSWORD)
    except:
        print("Posible error de autenticación.")
        print("""
Soluciones posibles:

1. Compruebe haber insertado el nombre de usuario y la contraseña correctas.

2. Si su cuenta es Gmail, entre en su cuenta de Google en la dirección
https://myaccount.google.com/security
y en la configuración busque «permitir aplicaciones menos seguras».

3. Si su cuenta es Gmail, se debe generar una contraseña especial en
https://myaccount.google.com/security.
La opción es «contraseñas para aplicaciones» bajo «autenticación en dos pasos».
            """)
        return None
    
    print("Se logró acceder al buzón de correo electrónico.\n")
    print("¿Desde cuál mensaje desea leer, contando desde el más reciente?")
    ref = input("Inserte un número o deje en blanco para leer a partir del mensaje más reciente. ")
    if ref == "": ref = -1 # Start from latest message
    print("¿Cuántos mensajes desea leer?")
    diff = input("Inserte un número: ")    
    if ref == -1: print("Se leerán los últimos", int(diff), "mensajes")
    else: print("Se leerán", int(diff), "mensajes a partir del", str(ref)+".")
    
    mail.select("inbox")    
    typ, data = mail.search(None, "ALL")
    
    id_list  = data[0].split()        
    earliest = int(id_list[int(ref)-int(diff)]) 
    latest   = int(id_list[int(ref)]) 
    
    outputdict = {}
    
    # Lists where the messages with errors in processing will be enumerated
    unprocesseddates = []
    unprocessedbodies = []
    unopened = []  
    
    interval = range(latest, earliest, -1)
    print("Se procesarán los mensajes entre el", latest-1, "y el", earliest)
    
    for i in interval:
        typ, data = mail.fetch(str(i), "(RFC822)" )
        # The following line will let the user know the progress of their request
        print("Leyendo mensaje", latest - i + 1, "de", latest - earliest)
        
        for item in data:                        
            if isinstance(item, tuple):
                try:
                    message = email.message_from_string(item[1].decode("utf-8", "ignore"))
    #                print(message) 
                    messagedict                 = {}
                    messagedict["id"]           = i

                    # Get "from" field in e-mail
                    try: # To prevent occasional encoding errors
                        temp                    = decode_header(message["from"])
                        messagedict["from"]     = str(temp[0][0])[2:-1] + str(temp[1][0])[2:-1]
                    except: # Most messages won't need a complicated treatment
                        messagedict["from"]     = str(message["from"])    
                    messagedict["from"] = messagedict["from"].replace('"', '')
                    
                    # Get "subject" field in e-mail
                    try: # To prevent occasional encoding errors
                        temp = decode_header(message["subject"])
                        messagedict["subject"] = ""
#                        print("try", len(temp), temp)
                        for tup in temp: # Some subjects may contain several tuples
                            piece = str(tup[0])
                            
                            if tup[1] == "utf-8": # There may be different encodings in each piece
                                piece = piece.encode().decode('unicode-escape').encode('latin-1').decode('utf-8')
                                piece = piece[2:-1]
                                
                            if piece[0] == "b" and (piece[1] == "'" or piece[1] == '"'):
                                piece = piece[2:-1]                                
#                            print(piece)
                            piece = piece.replace("''", "'").replace('""', '"').replace("\n","").replace("\r","")
                            messagedict["subject"] = messagedict["subject"] + piece    
                        
#                        print ("End", messagedict["subject"])
                    except: 
                        messagedict["subject"] = str(message["subject"])   
                    
                    messagedict["delivered-to"] = message ["delivered-to"]
                    messagedict["message-id"]   = message["message-id"]

                    messagedict["date"]         = message["date"]

                    # Extract year, month, day from datetime stamp on emails
                    try:
                        datetime_conv = dateutil.parser.parse(str(message["date"]))
    #                    print(message["date"])
    #                    print(datetime_conv)
                        # Convert datestamps to your local timezone
                        datetime_conv = datetime_conv.replace(tzinfo=timezone.utc).astimezone(tz=None)
    #                    print(datetime_conv)
    #                    print(message["date"], "→", datetime_conv) # Test the datetime conversion
                        messagedict["year"] = (datetime_conv.year)
                        messagedict["month"] = (datetime_conv.month)
                        messagedict["day"] = (datetime_conv.day)
                        messagedict["datetime"] = '{:%Y-%m-%d %H:%M}'.format(datetime(
                            datetime_conv.year,
                            datetime_conv.month,
                            datetime_conv.day,
                            datetime_conv.hour,
                            datetime_conv.minute))                
    #                    print(messagedict["year"], messagedict["month"],
    #                            messagedict["day"], messagedict["datetime"])                    
                    except:
                        # Print an error message and send the e-mail to the second dictionary
                        print("No se pudo procesar la fecha en el mensaje", i)
                        print("Fecha:", messagedict["date"])
                        unprocesseddates.append((i, messagedict["date"]))
                        messagedict["year"]     = "Year not read"      # Fields that were not parsed
                        messagedict["month"]    = "Month not read"     # are not left blank
                        messagedict["day"]      = "Day not read"       # so that the csv will have
                        messagedict["datetime"] = "Datetime not read"  # all fields in the same place
                        
                    # Get the message body
                    try:                                
                        if message.is_multipart():
                            messagedict["body"]     = ""
                            for payload in message.get_payload():
                                fragment = payload.get_payload()
                                messagedict["body"] = messagedict["body"] + str(fragment)
                        else:
                            messagedict["body"] = str(message)
                    
                        outputdict[messagedict["id"]] = messagedict
                    except:
                        # Print an error message and send the e-mail to the third dictionary
                        print("No se pudo procesar el cuerpo del mensaje", i)
                        messagedict["body"] = "Body not read"
                        unprocessedbodies.append(i)
                                                
                except:
                    print("No se pudo abrir el mensaje", i)
                    unopened.append(i)
                    
                # Fix encoding    
                    
                if "=\n" in messagedict["body"] or "=\r" in messagedict["body"]:
                    text = messagedict["body"].replace("=","%")
                    text = messagedict["body"].replace("%\n","").replace("%\r","")
                    text = messagedict["body"].replace("\n","").replace("\r","")
                    text = urllib.parse.unquote_to_bytes(text)
                    text = text.decode('unicode-escape').encode('latin-1').decode('utf-8')
                    messagedict["body"] = text
                    
    # Report to the user the result of their request
    print("Total de mensajes procesados:", len(outputdict), "(",
          round(100 * len(outputdict)/(latest - earliest) , 1)
          , "% )")
    print("")

    if len(unprocesseddates) == 0:
        print("Mensajes con fechas no procesadas:", len(unprocesseddates))
    else:
        print("Mensajes con fechas no procesadas:", len(unprocesseddates))
        pprint.pprint(unprocesseddates)
    print("")

    if len(unprocessedbodies) == 0:
        print("Mensajes con cuerpos no procesados:", len(unprocessedbodies))
    else:
        print("Mensajes con cuerpos no procesados:")
        print(unprocessedbodies)
    print("")

    if len(unopened) == 0:
        print("Mensajes no abiertos:", len(unopened))
    else:
        print("Mensajes no abiertos:")
        print(unopened)
    print("")

#    print(unprocesseddates, unprocessedbodies)

    return (outputdict, unprocesseddates, unprocessedbodies, unopened)

#test = readmail(getcredentials())

####################################################################################################

def dictlist_to_csv (input_list, output_filename):
    """
    Objective: open a list containing dictionaries and write it to a csv file
    Inputs:
        (1) list containing dictionaries
        (2) output csv filename
    """
    print("Creando archivo", output_filename+"...")
    # Open (or create) csv file
    with open (output_filename, "w", encoding="utf8") as csvfile:
        writer = csv.writer (csvfile,
                             delimiter = ";",
                             quotechar = '"',
                             quoting = csv.QUOTE_MINIMAL)
        
        firstentry = input_dict[list(input_dict.keys())[1]]
        print ("Campos:", firstentry.keys())
        writer.writerow(firstentry.keys())
                
        for row in input_list:
            writer.writerow(row)
    
    return None

def nesteddict_to_csv (input_dict, output_filename):
    """
    Objective: open a dictionary containing dictionaries and write it to a csv file
    Inputs:
        (1) dictionary containing dictionaries
        (2) output csv filename
    """
    print("Creando archivo", output_filename+"...")
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

def empty_to_csv (input_iterable, output_filename):
    """
    Objective: open an empty dictionary or list write it to a csv file
    Inputs:
        (1) empty dictionary or list
        (2) output csv filename
    """
    print("Creando archivo", output_filename+"...")
    # Open (or create) csv file
    with open (output_filename, "w", encoding="utf8") as csvfile:
        writer = csv.writer (csvfile,
                             delimiter = ";",
                             quotechar = '"',
                             quoting = csv.QUOTE_MINIMAL)
        
        writer.writerow(["No elements to display."])
    
    return None

def single_to_csv (input_single, output_filename):
    """
    Objective: write a single item to a csv file
    Inputs:
        (1) single item
        (2) output csv filename
    """
    print("Creando archivo", output_filename+"...")
    # Open (or create) csv file
    with open (output_filename, "w", encoding="utf8") as csvfile:
        writer = csv.writer (csvfile,
                             delimiter = ";",
                             quotechar = '"',
                             quoting = csv.QUOTE_MINIMAL)
        
        writer.writerow([input_single])
    
    return None

def list_to_csv (input_list, output_filename):
    """
    Objective: open a list and write it to a csv file
    Inputs:
        (1) empty dictionary or list
        (2) output csv filename
    """
    print("Creando archivo", output_filename+"...")
    # Open (or create) csv file
    with open (output_filename, "w", encoding="utf8") as csvfile:
        writer = csv.writer (csvfile,
                             delimiter = ";",
                             quotechar = '"',
                             quoting = csv.QUOTE_MINIMAL)
        
        for item in input_list:
            writer.writerow([item])
    
    return None


####################################################################################################

def save_mails_to_csvfiles ():
    """
    Objective: save the results of your inbox search to csv files
    Input: user credentials
    Returns: none
    """
    # Get user credentials to your e-mail account
    credentials = getcredentials()
    # Process the e-mails
    mails       = readmail(credentials)
    
    # Pair arrays to filenames
    processedmails    = mails[0]
    procmails_fn      = "processedmails.csv"

    unprocesseddates  = mails[1]
    udates_fn         = "unprocesseddates.csv"

    unprocessedbodies = mails[2]    
    ubodies_fn        = "unprocessedbodies.csv"

    unopened          = mails[3]    
    unopened_fn       = "unopened.csv"

    tups = [(processedmails,  procmails_fn),
            (unprocesseddates,   udates_fn),
            (unprocessedbodies, ubodies_fn),
            (unopened,         unopened_fn)
            ]
    
    # Write files depending on whether we have a dictionary or a list
    for tup in tups:
        if tup[0] is None:
            print("No se guardó un archivo. Posible error.")
        elif len(tup[0]) == 0:
            empty_to_csv (tup[0], tup[1])
            print("Se guardó el archivo", tup[1])
        elif isinstance (tup[0], int) or isinstance (tup[0], str):
            single_to_csv (tup[0], tup[1])
            print("Se guardó el archivo", tup[1])
        elif isinstance (tup[0], dict):
            nesteddict_to_csv (tup[0], tup[1])
            print("Se guardó el archivo", tup[1])
        elif isinstance (tup[0], list) and isinstance(tup[0][0], dict):
            dictlist_to_csv (tup[0], tup[1])
            print("Se guardó el archivo", tup[1])
        elif isinstance (tup[0], list):
            list_to_csv (tup[0], tup[1])
            print("Se guardó el archivo", tup[1])
        else:
            print("Error procesando el diccionario o lista.")
        
test = save_mails_to_csvfiles ()

#pprint.pprint (readmail(MYCREDENTIALS))

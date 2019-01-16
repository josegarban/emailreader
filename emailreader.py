import pprint
import csv
import imaplib
import getpass
from datetime import datetime
from datetime import timezone
import email

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
        mail = imaplib.IMAP4_SSL(SMTPSERVER)
        mail.login(EMAIL, PASSWORD)
        print("Intentando acceder al correo...")
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
        return
    
    print("Se logró acceder al buzón de correo electrónico.")
    print("¿Desde cuál mensaje desea leer, contando desde el más reciente?")
    diff = input("Inserte un número: ")
    print("Se leerán los últimos", diff, "mensajes")
    
    mail.select("inbox")    
    typ, data = mail.search(None, "ALL")
    
    id_list  = data[0].split()        
    earliest = int(id_list[-int(diff)-1]) 
    latest   = int(id_list[-1]) 
    
    outputdict = {}
    
    # Lists where the messages with errors in processing will be enumerated
    unprocesseddates = []
    unprocessedbodies = []
    
    interval = range(latest, earliest, -1)
    print("Se procesarán los mensajes entre el", latest, "y el", earliest + 1)
    
    for i in interval:
        typ, data = mail.fetch(str(i), '(RFC822)' )
        # The following line will let the user know the progress of their request
        print("Leyendo mensaje", latest - i + 1, "de", latest - earliest)
        
        for item in data:                        
            if isinstance(item, tuple):
                message = email.message_from_string(item[1].decode())
#                print(message) 
                messagedict                 = {}
                messagedict["id"]           = i
                messagedict["from"]         = message["from"]
                messagedict["subject"]      = message["subject"]
                messagedict["delivered-to"] = message ["delivered-to"]
                messagedict["message-id"]   = message["message-id"]

                messagedict["date"]         = message["date"]
                    
                # Convert string to datetime in some commonly found datetime patterns                
                try:
                    datetime_patt = "%a, %d %b %Y %H:%M:%S %z"
                    datetime_conv = datetime.strptime(messagedict["date"], datetime_patt)            
                except:
                    pass
                
                try:
                    datetime_patt = "%a %b %d %H:%M:%S %Z %Y"
                    datetime_conv = datetime.strptime(messagedict["date"], datetime_patt)
                except:
                    pass
                
                try:
                    datetime_patt = "%a, %d %b %Y %H:%M:%S %z (%Z)"
                    datetime_conv = datetime.strptime(messagedict["date"], datetime_patt)
                except:
                    pass

                try:
                    datetime_patt = "%a, %d %b %Y %H:%M:%S %z %Z"
                    datetime_conv = datetime.strptime(messagedict["date"], datetime_patt)
                except:
                    pass

                # Extract year, month, day from datetime stamp on emails
                try:
                    datetime_conv = datetime_conv.replace(tzinfo=timezone.utc).astimezone(tz=None)
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
                            messagedict["body"] = messagedict["body"] + str(payload.get_payload())
                    else:
                        messagedict["body"]     = str(message.get_payload())
                
                    outputdict[messagedict["id"]] = messagedict
                except:
                    # Print an error message and send the e-mail to the third dictionary
                    print("No se pudo procesar el cuerpo del mensaje", i)
                    messagedict["body"] = "Body not read"
                    unprocessedbodies.append(i)                        

    # Report to the user the result of their request
    print("Total de mensajes procesados:", len(outputdict), "(",
          round(100 * len(outputdict)/(latest - earliest) , 1)
          , "% )")

    if len(unprocesseddates) == 0:
        print("\nMensajes con fechas no procesadas:", len(unprocesseddates))
    else:
        print("\nMensajes con fechas no procesadas:", len(unprocesseddates))
        pprint.pprint(unprocesseddates)

    if len(unprocessedbodies) == 0:
        print("\nMensajes con cuerpos no procesados:", len(unprocessedbodies))
    else:
        print("\nMensajes con cuerpos no procesados:")
        print(unprocessedbodies)

    print(unprocesseddates, unprocessedbodies)

    return (outputdict, unprocesseddates, unprocessedbodies)

#test = readmail(getcredentials())

####################################################################################################

def dictlist_to_csv (input_list, output_filename):
    """
    Objective: open a list containing dictionaries and write it to a csv file
    Inputs:
        (1) list containing dictionaries
        (2) output csv filename
    """
    # Open (or create) csv file
    with open (output_filename, "w") as csvfile:
        writer = csv.writer (csvfile,
                             delimiter = ";",
                             quotechar = '"',
                             quoting = csv.QUOTE_MINIMAL)
        
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
    # Open (or create) csv file
    with open (output_filename, "w") as csvfile:
        writer = csv.writer (csvfile,
                             delimiter = ";",
                             quotechar = '"',
                             quoting = csv.QUOTE_MINIMAL)
        
        for key in input_dict.keys():
            templist = []
            for field in input_dict[key]:
                templist.append((input_dict[key])[field])
            writer.writerow(templist)
    
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

    tups = [(processedmails,  procmails_fn),
            (unprocesseddates,   udates_fn),
            (unprocessedbodies, ubodies_fn)
            ]
    
    # Write files depending on whether we have a dictionary or a list
    for tup in tups:
        if   isinstance (tup[0], dict):
            nesteddict_to_csv (tup[0], tup[1])
            print("Se guardó el archivo", tup[1])
        elif isinstance (tup[0], list):
            dictlist_to_csv   (tup[0], tup[1])
            print("Se guardó el archivo", tup[1])
        else:
            print("Error procesando el diccionario o lista.")
        
test = save_mails_to_csvfiles ()

#pprint.pprint (readmail(MYCREDENTIALS))

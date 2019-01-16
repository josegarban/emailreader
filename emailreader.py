import pprint
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

# User and pasword definitions
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
    
    print("¿Desde cuál mensaje desea leer, contando desde el más reciente?")
    diff = input("Inserte un número: ")
    print("Se leerán los últimos", diff, "mensajes")
    
    mail.select("inbox")    
    typ, data = mail.search(None, "ALL")
    
    id_list  = data[0].split()        
    earliest = int(id_list[-diff]) 
    latest   = int(id_list[-1]) 
    
    outputdict = {}
    
    # Lists where the messages with errors in processing will be enumerated
    unprocesseddates = []
    unprocessedbodies = []
    
    interval = range(latest, earliest, -1)
    print("Se procesarán los mensajes entre el", latest, "y el", earliest)
    
    for i in interval:
        typ, data = mail.fetch(str(i), '(RFC822)' )
        # The following line will let the user know the progress of their request
        print("Leyendo mensaje", latest - i + 1, "de", latest - earliest)
        
        for item in data:                        
                if isinstance(item, tuple):
                    message = email.message_from_string(item[1].decode())
#                    print(message) 
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
                        datetime_conv = datetime_conv.replace(tzinfo=timezone.utc).astimezone(tz=None)
#                        print(message["date"], "→", datetime_conv) # Test the datetime conversion
                        messagedict["year"] = (datetime_conv.year)
                        messagedict["month"] = (datetime_conv.month)
                        messagedict["day"] = (datetime_conv.day)
                        messagedict["time"] = (str(datetime_conv.hour) +":"+ str(datetime_conv.minute))                
#                        print(messagedict["year"], messagedict["month"], messagedict["day"], messagedict["time"])                    
                    except:
                        # Print an error message and send the e-mail to the second dictionary
                        print("No se pudo procesar la fecha en el mensaje", i)
                        print("Fecha:", messagedict["date"])
                        unprocesseddates.append((i, messagedict["date"]))
                    
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
        print("\nMensajes con cuerpos no procesadas:", len(unprocesseddates))
    else:
        print("\nMensajes con cuerpos no procesados:")
        print(unprocessedbodies)

    return outputdict, unprocesseddates, unprocessedbodies

test = readmail(getcredentials())

####################################################################################################


# emailreader
Look up your e-mail inbox and find any e-mail addresses in the body of your messages.
Revise su buzón de correo electrónico y encuentra cualquier dirección de correo electrónico en el cuerpo de su mensaje.

## Instructions:

1. If you have a Google account, allow "2-step verification" in https://myaccount.google.com/security. Then create a Google password by selecting "passwords for applications" under "2-step verification".
2. Run emailreader.py. You will be prompted for the following:
- Your account "name@domain.com".
- The password created in the previous step.
- The SMTP server, just leave it blank if you are using Gmail.
3. You will be shown the e-mail total and be prompted from which you want to start reading. E.g. if you have 5000 e-mails and want to read starting from the latest, you may leave a blank answer. If that is not the case, you have to answer with any integer like "4000". The oldest message is "1".
4. You will be asked how many e-mails you wish to read, counting towards the oldest one. The answer must also be an integer. If you selected "4000" and want to read 1000 e-mails, the script will process e-mails 4000 to 3001.
5. The script will generate several .csv files, including one with your processed e-mails  (`processedmails_[timestamp].csv)` and others with possible errors (`unprocessedbodies_[timestamp].csv`, `unprocesseddates_[timestamp].csv`, `unopened_[timestamp].csv`).
6. Run emaildictproc.py. This script will read the file `processedmails_[timestamp].csv)` from the previous step and return two files: `emails_permessage_[timestamp].csv` y `matched_emails_[timestamp].csv`. The first one will show the e-mail addresses in the body of each of your messages, and the second one is a consolidation of all the found addresses. Any strings with filenames like "icon_fb@2x.jpg" will be discarded. However, the user's own e-mail is likely to appear.

Notes:
- Messages with unprocessed dates (`unprocesseddates_[timestamp].csv`): in some cases there may be errors when extracting the year and month of the e-mail message. The body of the message (and almost always the date) will be processed anyway but there might still be an e-mail that won't be easily ordered by date in the final result. It will be saved with "Year not read" and "Month not read".
- Messages with unprocessed bodies (`unprocessedbodies_[timestamp].csv`): in some cases the decoding of the e-mail body may fail.
- Unopened messages (`unopened_[timestamp].csv`): in some cases an e-mail may not be opened, for example with unstable Internet connections.
- Timestamps in the names a set of files will be the same.


## Instrucciones:

1. Si tiene una cuenta Google, permitir «autenticación en dos pasos» en https://myaccount.google.com/security y cree una contraseña al seleccionar «contraseñas para aplicaciones» bajo «autenticación en dos pasos».
2. Ejecute emailreader.py. Se le solicitará lo siguiente:
- Su cuenta «name@dominio.com».
- La contraseña creada en el paso anterior.
- El servidor SMTP, sólo déjelo en blanco si está usando Gmail.
3. Se le mostrará el total de correos y se le preguntará a partir de cuál correo quiere leer. Ej.: si tiene 5000 correos y quiere leer desde el último, puede dejar la respuesta en blanco. Si no, debe responder con algún número, como «4000». El correo más antiguo es el «1».
4. Se le preguntará cuántos correos quiere leer, en dirección al más antiguo. La respuesta debe ser también un número. Si seleccionó «4000» y quiere leer 1000 mensajes, el script procesará los correos 4000 a 3001.
5. El script generará varios archivos .csv, incluyendo uno con los correos procesados (`processedmails_[fecha-hora].csv)` y otros con posibles errores (`unprocessedbodies_[fecha-hora].csv`, `unprocesseddates_[fecha-hora].csv`, `unopened_[fecha-hora].csv`).
6. Ejecute emaildictproc.py. Este script leerá el archivo `processedmails_[fecha-hora].csv` del paso anterior y devolverá dos archivos: `emails_permessage_[fecha-hora].csv` y `matched_emails_[fecha-hora].csv`. El primero muestra las direcciones de correo electrónico encontradas en cada uno de sus mensajes y el segundo es una consolidación de las direcciones encontradas. Se descartan las cadenas de texto con nombres de archivos como «icon_fb@2x.jpg». Sin embargo, puede salir el correo del usuario.

Notas:
- Mensajes con fechas no procesadas (`unprocesseddates_[fecha-hora].csv`): en algunos casos puede haber errores al extraer el año y el mes de la fecha del correo. El cuerpo del mensaje (y casi siempre la fecha) se procesa de todas formas pero pudiera existir algún correo que no se ordene fácilmente por fecha en el resultado final. Saldrá con «Year not read» y «Month not read».
- Mensajes con cuerpos no procesados (`unprocessedbodies_[fecha-hora].csv`): en algunos casos puede fallar la decodificación del cuerpo del correo.
- Mensajes no abiertos (`unopened_[fecha-hora].csv`): en algunos casos puede no abrirse el correo, por ejemplo con conexiones de Internet inestables.
- La fecha y hora en el nombre de un conjunto de archivos será igual.

##################################################################
# common definitions and global variables for IO client/server system
#

import socket

LOCALHOST = socket.gethostname()

# server always uses localhost

SERVERHOST = socket.gethostbyname( LOCALHOST ) 

# clients usually use a standard name
# (ioclient's -t swtich redirects to localhost )

SERVER = socket.gethostbyname( "igor" )

COMPORT=51001   # communications port
LOGPORT=51003   # log file access
SER0PORT=51010  # serial COMM port access (this and next few)

CMD_PREFIX = '$'


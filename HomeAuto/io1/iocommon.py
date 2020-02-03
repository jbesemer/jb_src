##################################################################
# common definitions and global variables for IO client/server system
#

import socket

SERVER=""
SERVER = socket.gethostbyname( SERVER )
SERVERHOST=""	# server always uses localhost

COMPORT=51001   # communications port
LOGPORT=51003   # log file access
SER0PORT=51010  # serial COMM port access (this and next few)

CMD_PREFIX = '$'


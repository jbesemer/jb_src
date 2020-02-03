
# fetch fully qualified domain name

import socket

HOST, DOMAIN = socket.getfqdn().split( ".", 1 )


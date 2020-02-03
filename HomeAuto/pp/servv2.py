from select import *
import socket
import sys
import os
from speak import *

HOST=""
PORT=5011

i = sys.stdin

s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
s.bind(( HOST, PORT ))

speak( "Voice server is ready" )
print "Ready..."

addr = 0

while 1:
	ri,ro,re = select([s,i], [], [])

	if i in ri:
		data = i.readline()
		print "SendTo", addr, s.sendto( data, 0, addr ), data,
		

	if s in ri:
		data, addr = s.recvfrom( 1024 )
		print "Recd from", addr, ":", data,
		rc = speak( data )
		print "sent", s.sendto( "Spoke " + `rc` + "\n", 0, addr ),
		

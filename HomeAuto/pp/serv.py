import socket
import sys
import speak
from select import *

i = sys.stdin

HOST=""
PORT=5009

s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
s.bind(( HOST, PORT ))

print "Ready..."

addr = 0

while 1:
	ri,ro,re = select([s,i], [], [])

	if i in ri:
		data = i.readline()
		if addr != 0:
			print "SendTo", addr, s.sendto( data, 0, addr ), data,

	if s in ri:
		data, addr = s.recvfrom( 1024 )
		print "Recd from", addr, ":", data,
		print "SendTo", addr, s.sendto( data, 0, addr ), data,

	speak.speak( data )	

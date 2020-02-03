import socket
import sys

HOST="cascade-sys.com"
PORT=50011

s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
# s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

s.connect(( HOST, PORT ))

while 1:
	data = sys.stdin.readline()
	if not data:
		break

	s.send( data );
	data2 = s.recv( 1024 )
	print "Recd:", data2

s.close()

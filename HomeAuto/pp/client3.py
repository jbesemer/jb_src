import socket
import sys
import thread

HOST="cascade-sys.com" # HOST="192.168.0.120" 
PORT=50011

if len( sys.argv ) > 1:
	HOST = sys.argv[ 1 ]

HOST = socket.gethostbyname( HOST )

print "connecting to", HOST, "..."

s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
s.connect(( HOST, PORT ))
# s.bind(( HOST, PORT ))


def sender():
	i = sys.stdin
	while 1:
		data = i.readline()
		if not data:
			break
		# s.sendto( data, 0,  ( HOST, PORT ))
		s.send( data )

def receiver():
	while 1:
		data, addr = s.recvfrom( 1024 )
		# data = s.recv( 1024 )
		print "Recd from", addr, ":", data,

thread.start_new_thread( receiver, ())
sender()

s.close()

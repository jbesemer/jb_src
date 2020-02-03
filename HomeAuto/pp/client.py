import socket
import sys
import thread

HOST="cascade-sys.com" # HOST="192.168.0.120" 
PORT=50011
HOST = socket.gethostbyname( HOST )

print "connecting to", HOST, "..."

s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
s.connect(( HOST, PORT ))
# s.bind(( HOST, PORT ))


def sender():
	i = sys.stdin
	while 1:
		data = i.readline()
		if not data:
			break
		s.send( data )

def receiver():
	while 1:
		data = s.recv( 1024 )
		if not data:
			break
		print "Recd from host:", data,

thread.start_new_thread( receiver, ())
sender()

s.close()

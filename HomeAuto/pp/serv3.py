import socket
import thread

HOST=""
PORT=50009

s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
# s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
s.bind(( HOST, PORT ))

poller = select.poll()

def connector( s, poller ):
	while 1:
		s.listen(1)
		conn, addr = s.accept()
		print "Accepting", addr
		poller.register( conn.fileno())

thread.start_new_thread( connector, ( s, poller ))

def receive( conn ):
	while 1:
		data = conn.recv( 1024 )
		if not data: 
			break
		print "Recd:", data

	conn.close()
	print "Closing"

while 1:
	p = poller.poll( 1000 )


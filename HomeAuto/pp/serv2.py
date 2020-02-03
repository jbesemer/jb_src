import socket

HOST=""
PORT=50009

s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
# s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
s.bind(( HOST, PORT ))

while 1:
	s.listen(1)
	conn, addr = s.accept()
	print "Accepting", addr

	while 1:
		data = conn.recv( 1024 )
		if not data: 
			break
		print "Recd:", data
		conn.send( data )
	conn.close()
	print "Closing"

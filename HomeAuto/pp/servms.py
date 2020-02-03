import os, sys, string
import socket, thread, time

HOST=""
PORT=50011
clients = []

def receiver( s, conn, addr ):
	clients.append( conn )

	while 1:
		data = conn.recv( 1024 )
		if not data: 
			break
		print "recv[", addr, "]:", data
		conn.send( data )

	clients.remove( conn )
	conn.close()
	print "Closing", addr

def server():
	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	s.bind(( HOST, PORT ))

	while 1:
		s.listen(1)
		conn, addr = s.accept()
		print "Accepting", addr

		thread.start_new_thread( receiver, ( s, conn, addr ))

def reader():
	while 1:
		line = sys.stdin.readline()
		for client in clients:
			client.send( line )

thread.start_new_thread( server, ())
thread.start_new_thread( reader, ())

while 1:
	time.sleep( 1000 )

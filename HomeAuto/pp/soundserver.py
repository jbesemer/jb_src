import sys, os
import socket, thread
import Queue
import string
import signal

from speak import *
from select import *
from playsounds import *

# server port offered on localhost
PORT1=50011	# entire message is 1 speech
PORT2=50012	# each line is spoken as it is read
HOST=""

# two queues connect three threads

ReaderQ1 = Queue.Queue()
ReaderQ2 = Queue.Queue()
SpeakerQ = Queue.Queue()


def readline( conn, pending ):
	line = ""

	while 1:
		while pending and '\n' in pending:
			pos = pending.index( '\n' )
			line = pending[ : pos ]
			pending = pending[ pos+1 : ]
			if line == "":
				continue
			return line, pending

		data = conn.recv( 666 )
		if not data:
			break

		pending += data

	return pending, ""


# Server threads accept socket connects and pass them on 
# to the appropriate Reader.  The idea is to accept sockets
# as fast as possible (FWIW).  

def Server( queue, port ):
	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	s.bind(( HOST, port ))

	speak( "Sound server is ready" )

	while 1:
		s.listen( 3 )
		conn, addr = s.accept()
		queue.put(( conn, addr ))

# Reader thread reads up all the data submitted by the client
# and forwards it to the Speaker thread.  

def Reader1():
	while 1:
		conn, addr = ReaderQ1.get()
		text = ""
		while 1:
			data = conn.recv( 1024 )
			if not data:
				break
			text += data
		
		if text:
			SpeakerQ.put(( None, text ))
		conn.close()

# Reader thread reads data line at a time,
# forwarding it to the Speaker thread.  

def Reader2():
	while 1:
		conn, addr = ReaderQ2.get()
		pending = ""
		while 1:
			line, pending = readline( conn, pending )
			if not line:
				break
		
			SpeakerQ.put(( None, line ))
		
#		print "Reader2 closing conn"
		conn.close()

# Speaker thread actually causes the speech to be emitted.
# This is done by an external exe.  Speaker can take several
# seconds to perform each action, so the queue here is essential.
# We send a return code back to the client before closing
# the connection.

def Speaker():
	while 1:
		rc = -1
		conn, data = SpeakerQ.get()
		items = data.split( "\n" )

		for item in items:
			if not item:
				continue

			# if it looks like a filename 
			# or has a "-f" prefix 
			# then play WAV file
			# else speech to text

			if item[0] in ['.', '/']:
				rc = playsounds( item )

			elif len( item ) > 2 and item[:2] == '-f':
				rc = playsounds( item[2:].strip())

			else:
				rc = speak( item )

			if 0 and conn:
				conn.send( str( rc ) + "\n" )
				conn.close()


# handle signals and clear running flag

Running = 1

def HandleSig( sig, frame ):
	global Running
	Running = 0
	if sig == signal.SIGHUP:
		print "Exiting due to hangup"
	elif sig == signal.SIGINT:
		print "Exiting due to Interrupt"
	else:
		print "Exiting due to Unk Sig"

# launch the threads
# (primary thread fields signals)

def main():
	signal.signal( signal.SIGHUP, HandleSig )
	signal.signal( signal.SIGINT, HandleSig )

#	speak( "Sound Server is starting" )

	try:
		thread.start_new_thread( Speaker, ())
		thread.start_new_thread( Reader1, ())
		thread.start_new_thread( Reader2, ())
		thread.start_new_thread( Server, ( ReaderQ1, PORT1 ))
		thread.start_new_thread( Server, ( ReaderQ2, PORT2 ))

		while Running:
			signal.pause()

	finally:
		speak( "Sound Server is exiting" )

main()

from __future__ import generators

import sys, os, string
import socket, thread
import signal
from ClientList import *
from common import *

###############################################
# skeleton server to test readline generator
###############################################

###############################################
# module global vars and constants

ECHOFLAG = 1	# => echo all comm with IO

###############################################
# one dedicated thread for each client connection.
# handle incoming commands and return results.

class ClientConn( Client ):

	def add( self ):
		pass

	def remove( self ):
		pass

	def close( self ):	
		self.sock.close()

	def getline( self ):
		pending = ""
		while 1:
			data = self.sock.recv( 666 )
			if not data:
				return
			pending += data
			if ECHOFLAG:
				print "recv:", data

			# only whole lines constitute a command

			while '\n' in pending:
				pos = pending.index( '\n' )
				cmd = pending[ : pos ]
				pending = pending[ pos+1 : ]
				yield cmd

	def Main( self ):
		self.add()
		print "New Comm Client:"

		for line in self.getline():
			print line

		print "End Comm Client:", self.name
		self.exit()


	def exit( self ):
		self.remove()
		self.close()


###############################################
# listen for connects and dispatch to dedicated 
#	thread to handle normal command ops

def CmdListener():
	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	s.bind(( SERVERHOST, COMPORT ))

	while 1:
		s.listen(3)
		conn, addr = s.accept()
		comm = ClientConn( conn, addr )
		thread.start_new_thread( comm.Main, ())

###############################################
# launch the threads
# main thread idles, waiting to handle external signals

def main():
	global ECHOFLAG

	if len( sys.argv ) > 1 and sys.argv[1] == '-e':
		ECHOFLAG = not ECHOFLAG
		if ECHOFLAG:
			shally = "will"
		else:
			shally = "will NOT"
		print shally, "echo serial port traffic"

	thread.start_new_thread( CmdListener, ())

	while 1:
		signal.pause()

main()

from __future__ import generators

import sys, os, string
import socket, thread
import signal
from select import select
from ClientList import *
from common import *
import selectqueue

###############################################
# skeleton server to test readline generator
###############################################

###############################################
# module global vars and constants

ECHOFLAG = 0	# => echo all comm with IO

queue = selectqueue.SelectQueue()

pi, po = os.pipe()

###############################################
# one dedicated thread for each client connection.
# handle incoming commands and return results.

class ClientConn( Client ):

	def getline( self ):
		pending = ""
		while 1:
			# ri, wi, ei = select( [self.sock, queue], [], [])
			ri, wi, ei = select( [self.sock, pi], [], [])
			if len( ri ) == 2:
				# item = queue.get()
				# print "queue:", item
				item = os.read( pi, 1 )
				print "pipe:", item
				continue

			data = self.sock.recv( 666 )
			if not data:
				return
			if ECHOFLAG:
				print "recv:", data
			pending += data

			# only whole lines constitute a command

			while '\n' in pending:
				pos = pending.index( '\n' )
				cmd = pending[ : pos ]
				pending = pending[ pos+1 : ]
				yield cmd

	def Main( self ):
		print "New Comm Client:"

		lines = self.getline()
		for line in lines:
			print line
			if line[:4] == "NAME":
				self.name = line[5:]
				continue
			if line == "quote":
				while 1:
					line = lines.next()
					print "quote:", line
					if line == "quote":
						break

		print "End Comm Client:", self.name
		self.exit()


	def exit( self ):
		self.sock.close()


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

def StdinListener():
	while 1:
		line = sys.stdin.readline().strip()
		print "line:", line
		# queue.put( line )
		os.write( po, line )

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
	thread.start_new_thread( StdinListener, ())

	while 1:
		signal.pause()

main()

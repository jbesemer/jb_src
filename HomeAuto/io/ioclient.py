#!/usr/local/bin/python2.2

import os, sys
import string
import socket
import signal
import thread
import time

sys.path.append( "/home/jb/lib/python" )

from iocommon import *
from getline_gen import gen_sock_getline
from GenericClient import *

##########################################
# todo:
#
#	get command
#	maybe have monitor start by sending current status
#	some kind of recovery attempt when no server
#	and when server goes away and comes back.
#
#	need a way to fetch bank's pin count


SOCKETTIMEOUT = 8

##########################################
# Command Client

class IoClient( GenericClient ):

	def __init__( self, name='IoClient', WaitFlag = 1, server=SERVER, port=COMPORT ):
		GenericClient.__init__( self, server, port, name )
		self.WaitFlag = WaitFlag

	def sendCommand( self, command ):
		# print "sendCommand", command
		self.s.send( command + "\n" )

	def sendRawCommand( self, command ):
		# print "sendRawCommand", command
		self.s.send( CMD_PREFIX + command + "\n" )

	def doit( self, data ):
		self.open()
		self.send( data )
		self.shutdown()

	def on( self, pins ):
		self.sendCommand( "1 " + pins )

	def off( self, pins ):
		self.sendCommand( "0 " + pins )

	def set( self, pins, value ):
		if value:
			self.on( pins )
		else:
			self.off( pins )

	def toggle( self, pins ):
		self.sendCommand( "T " + pins )

	def pulse( self, pins ):
		self.sendCommand( "P " + pins )

	def add( self, pins ):
		self.sendCommand( "ADD " + pins )

	def rem( self, pins ):
		self.sendCommand( "REM " + pins )

	def status( self ):
		self.sendCommand( "STAT" )

	def setmode( self, args ):
		self.sendCommand( "MODE " + args )

##########################################
# Log Client

class IoLogClient( GenericClient ):

	def __init__( self ):
		GenericClient.__init__( self, SERVERHOST, LOGPORT, "IoLogger" )


##########################################
# Unit Test / Command Mode

if __name__ == "__main__":
	WaitFlag = 1

	if "-t" in sys.argv:
		SERVER = SERVERHOST
		sys.argv.remove( "-t" )

	if "-w" in sys.argv:
		WaitFlag = not WaitFlag
		sys.argv.remove( "-w" )

	if "-l" in sys.argv:
		io = IoLogClient()
		io.useropen()

		print "Connected..."

		def quit( sig, stack ):
			print "Quitting..."
			io.close()
			sys.exit()

		signal.signal( signal.SIGINT, quit )

		while 1:
			data = io.recv()
			if not data:
				break
			sys.stdout.write( data )
		sys.exit()

	io = IoClient( WaitFlag=WaitFlag, server=SERVER )

	if len( sys.argv ) > 1:
		print "Sending Command Line"
		io.doit( string.join( sys.argv[1:]))
	else:
		io.useropen()
		io.start_watcher()
		while 1:
			if sys.stdin.isatty():
				sys.stdout.write( ">>> " )
			data = sys.stdin.readline().strip()
			if not data:
				break
			if data[0] == CMD_PREFIX:
				io.sendRawCommand( data[1:])
			else:
				io.sendCommand( data )
		io.shutdown()

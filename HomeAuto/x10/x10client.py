#!/usr/local/bin/python2.2

import os, sys
import string
import socket
import signal
import thread
import time

sys.path.append( "/home/jb/lib/python" )

from GenericClient import *
from x10common import *
import x10_parse
import logger

x10_parse.log = logger.Logger()

##########################################
# Command Client

class X10Client( GenericClient ):

	def __init__( self, name='X10Client', WaitFlag = 1 ):
		self.WaitFlag = WaitFlag
		self.name = name
		self.sock = None
		self.server = SERVER
		self.port = OPPORT

	def sendCommand( self, command ):
		# print "sendCommand", command
		self.send( command + "\n" )

	def sendRawCommand( self, command ):
		# print "sendRawCommand", command
		self.send( CMD_PREFIX + command + "\n" )

	def add( self, args ):
		args = x10_parse.parse_addresses( args )
		self.sendCommand( "add " + args )

	def rem( self, args ):
		args = x10_parse.parse_addresses( args )
		self.sendCommand( "add " + args )

	def get( self, args ):
		args = x10_parse.parse_addresses( args )
		self.sendCommand( "get " + args )

	def x10s( self, commands ):
		self.x10( commands.split())

	def x10( self, commands ):
		imm = x10_parse.parse( commands )
		res = x10_parse.generate( imm )
		self.sendCommand( "send " + res.join())


##########################################
# Log Client

class X10LogClient( GenericClient ):

	def __init__( self ):
		self.name = "X10Logger"
		self.sock = None
		self.server = SERVER
		self.port = LOGPORT


##########################################
# Unit Test / Command Mode

if __name__ == "__main__":
	WaitFlag = 1

	if "-w" in sys.argv:
		WaitFlag = not WaitFlag
		sys.argv.remove( "-w" )

	if "-l" in sys.argv:
		print "Log data..."

		x10 = X10LogClient()
		x10.open()

		def quit( sig, stack ):
			print "Quitting..."
			x10.close()
			sys.exit()

		signal.signal( signal.SIGINT, quit )

		while 1:
			data = x10.recv()
			if not data:
				break
			sys.stdout.write( data )
		sys.exit()


	x10 = X10Client( "X10Client", WaitFlag )
	x10.useropen()

	if len( sys.argv ) > 1:
		if sys.stdin.isatty():
			print "Sending Command Line"
		x10.x10( sys.argv[1:])
		x10.waitdone()

	else:

		x10.start_watcher()

		while 1:
			data = sys.stdin.readline()
			if not data:
				break
			data = data.strip()
			if not data:
				continue

			if data[:4] == "get ":
				x10.get( data[4:])

			elif data[:4] == "add ":
				x10.add( data[4:])

			elif data[:4] == "rem ":
				x10.rem( data[4:])

			else:
				x10.x10s( data )

		#	x10.waitdone()

	x10.shutdown()

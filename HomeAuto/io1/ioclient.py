
import os, sys
import string
import socket
import signal
import thread
import time

from iocommon import *

##########################################
# Command Client

class IoClient:
	def __init__( self, name=None, WaitFlag = 1 ):
		self.WaitFlag = WaitFlag
		self.name = name

	def open( self ):
		self.s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.dest = ( SERVER, COMPORT )
		self.s.connect( self.dest )
		self.pending = ""
		if self.name:
			self.sendName( self.name )

	def send( self, data ):
		self.s.send( data )

	def recv( self, len = 666 ):
		return self.s.recv( len )

	def readline( self ):

		while 1:
			if '\n' in self.pending:
				pos = self.pending.index( '\n' )
				line = self.pending[ : pos ]
				self.pending = self.pending[ pos+1 : ]
				# print "readline:", line
				return line

			data = self.recv()
			if not data:
				return self.pending
			self.pending += data
			# print "recv:",data

	def sendName( self, name ):
		# print "NAME", name
		self.sendCommand( "NAME " + name )

	def sendCommand( self, command ):
		# print "sendCommand", command
		self.s.send( command + "\n" )

	def sendRawCommand( self, command ):
		# print "sendRawCommand", command
		self.s.send( CMD_PREFIX + command + "\n" )

	def shutdown( self ):
		self.s.shutdown( 1 )

		while self.WaitFlag:
			data = self.s.recv( 1024 )
			if not data:
				break
			print data,
		self.close()

	def close( self ):
		self.s.close()

	def doit( self, data ):
		self.open()
		self.send( data )
		self.shutdown()

	def watch( self ):
		thread.start_new_thread( self.watcher, ())
	
	def watcher( self ):
		while 1:
			data = self.s.recv( 132 )
			if not data:
				break
			print data,
		
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

	def monitor( self, pins ):
		self.sendCommand( "ADD " + pins )

	def nomonitor( self, pins ):
		self.sendCommand( "REM " + pins )

	def status( self ):
		self.sendCommand( "STAT" )

	def setmode( self, args ):
		self.sendCommand( "MODE " + args )

##########################################
# Log Client

class IoLogClient:
	def __init__( self ):
		self.sock = None
		pass

	def open( self ):
		self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.dest = ( SERVER, LOGPORT )
		self.sock.connect( self.dest )

	def close( self ):
		self.sock.close()
	
	def recv( self ):
		return self.sock.recv( 999 )

##########################################
# Unit Test / Command Mode

if __name__ == "__main__":
	WaitFlag = 1

	if "-w" in sys.argv:
		WaitFlag = not WaitFlag
		sys.argv.remove( "-w" )

	if "-l" in sys.argv:
		print "Log data..."

		io = IoLogClient()
		io.open()

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

	io = IoClient( "IoClient", WaitFlag )

	if len( sys.argv ) > 1:
		print "Sending Command Line"
		io.doit( string.join( sys.argv[1:]))
	else:
		io.open()
		io.watch()
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
		time.sleep( 1 )

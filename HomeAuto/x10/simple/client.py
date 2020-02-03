#!/usr/local/bin/python2.1

import os, sys
import string
import socket
import signal
import thread
import time

from common import *

SOCKETTIMEOUT = 8

##########################################
# Command Client

class IoClient:
	def __init__( self, name=None, WaitFlag = 1 ):
		self.WaitFlag = WaitFlag
		self.name = name

	def open( self ):
		self.s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.dest = ( SERVER, COMPORT )
		self.connect()
		self.pending = ""
		if self.name:
			self.sendName( self.name )

	def connect( self ):
		t0 = time.time()
		while 1:
			try:
				self.s.connect( self.dest )
				break
			except socket.error:
				if ( time.time() - t0 ) > SOCKETTIMEOUT:
					raise
				continue

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

##########################################
# Unit Test / Command Mode

if __name__ == "__main__":
	WaitFlag = 1

	if "-w" in sys.argv:
		WaitFlag = not WaitFlag
		sys.argv.remove( "-w" )

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
			io.sendCommand( data )
		io.shutdown()
		time.sleep( 1 )

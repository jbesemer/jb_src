#!/usr/local/bin/python2.2

import os, sys
import string
import socket
import signal
import thread
import time

sys.path.append( "/home/jb/lib/python" )

from getline_gen import gen_sock_getline

SOCKETTIMEOUT = 8

##########################################
# Log Client

class GenericClient:

	def __init__( self, server, port, name=None ):
		self.name = name
		self.server = server
		self.port = port
		self.s = None

	def open( self, timeout=SOCKETTIMEOUT ):
		self.s = socket.socket( 
					socket.AF_INET, 
					socket.SOCK_STREAM )

		self.host = socket.gethostbyname( self.server )

		self.dest = ( self.host, self.port )
		self.connect( timeout )
		if self.name:
			self.sendName( self.name )

#	def readline()
		self.readline = gen_sock_getline( self.s )

	def useropen( self ):
		sys.stdout.write( "Connecting to %s:%s..." 
					% ( self.server, self.port ))
		sys.stdout.flush()
		while 1:
			try:
				self.open()
				print "Done"
				break
			except socket.error:
				sys.stdout.write( "." )
				sys.stdout.flush()
				time.sleep( 2 )
				continue

	def connect( self, timeout=SOCKETTIMEOUT ):
		t0 = time.time()
		while 1:
			try:
				self.s.connect( self.dest )
				break
			except socket.error:
				if not timeout or ( time.time() - t0 ) > timeout:
					raise
				time.sleep( 1 )
				continue

	def close( self ):
		self.s.close()

	def send( self, data ):
		self.s.send( data )

	def recv( self, len = 666 ):
		return self.s.recv( len )

	def sendName( self, name ):
		# print "NAME", name
		self.send( "NAME " + name + "\n" )

	def shutdown( self ):
		self.s.shutdown( 1 )

		while self.WaitFlag:
			data = self.recv()
			if not data:
				break
			print data,
		self.close()

	def start_watcher( self, watcher=None, args=() ):
		if watcher == None:
			watcher = self.watcher
		thread.start_new_thread( watcher, args )
	
	def watcher( self ):
		for line in self.readline:
			line = line.strip()
			print line

	def waitdone( self ):
		for line in self.readline:
			line = line.strip()
			if line == "#Done":
				return
			print line
			if line[:6] == "#Error":
				return



# UNIT TESTING

if __name__ == "__main__":

	import sys, signal
	from Connection import *

	argc = len( sys.argv )
	if argc > 1:
		host = sys.argv[1]
	else:
		host = "localhost"

	if argc > 2:
		port = int( sys.argv[2])
	else:
		port = 45321

	link = GenericClient( host, port, name="GenericClient Unit Test" )
	link.useropen()
	link.start_watcher()

	for line in sys.stdin:
		link.send( line )

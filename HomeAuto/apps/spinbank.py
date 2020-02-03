#!/usr/local/bin/python2.2

import os, sys
import string
import socket
import signal
import thread
import time

sys.path.append( "/home/jb/lib/python" )
sys.path.append( "/home/jb/io" )

import ioclient

DELAY = 0.02

# extend IOClient class to monitor IOs.
# mainly we just announce what happens.

class IOC( ioclient.IoClient ):

	def monitor( self ):
		for line in self.readline:
			# lines: "hh:mm:ss CHANGE unit [01]"

			line = line.strip()
			if line == "#Done":
				continue
			print line

			if line[:6] == "#Error":
				continue

	def start_monitor( self ):
		thread.start_new_thread( self.monitor, ())

##########################################
# Unit Test / Command Mode

if __name__ == "__main__":


	if len( sys.argv ) > 1:
		args = sys.argv[1:]
	else:
		print "You must specifiy one or more bank letters"
		sys.exit()

	if 1:
		def allbank( s ):
			if len( s ) > 1:
				s = s[0]
			s = s.upper()
			return [ "%s%d" % (s, i) 
					for i in xrange(16)]

		PinList = []
		for a in args:
			if a[0] <> '-':
				PinList.extend( allbank( a ))

	TestFlag = ( '-t' in args )

	Pins = string.join( PinList )
#	print "Pins:", Pins
#	print "PinList:", PinList

	# instantiate client connections for X10 and IO.
	# in this case, io is redirected to alternate server.
	# start receive monitors

	if TestFlag:
		io = IOC( "PinTest", server="cascade" )
	else:
		io = IOC( "PinTest" )

	io.useropen()
	io.off( Pins )
#	io.add( Pins )
	io.start_monitor()

	def stop( a, b ):
		print "Cleaning up..."
		io.off( Pins )
		sys.exit()

	signal.signal( signal.SIGINT, stop )

	while 1:
		for pin in PinList:
			io.on( pin )
			time.sleep( DELAY )

		for pin in PinList:
			io.off( pin )
			time.sleep( DELAY )




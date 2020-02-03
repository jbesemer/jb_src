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

DELAY = 0.25

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
			"convert single letter to entire bank"
			if len( s ) == 1:
				return s + "*"
			else:
				return s

		PinList = [ allbank( a ) 
				for a in args 
					if a[0] <> '-' ]

	TestFlag = ( '-t' in args )

	Pins = string.join( PinList )
	# print "Pins:", Pins
	# print "PinList:", PinList

	# instantiate client connections for X10 and IO.
	# in this case, io is redirected to alternate server.
	# start receive monitors

	if TestFlag:
		io = IOC( "PinTest", server="cascade" )
	else:
		io = IOC( "PinTest" )

	io.useropen()
#	io.add( Pins )
	io.start_monitor()

	while 1:
		for pin in PinList:
			io.on( pin )
			time.sleep( DELAY )
			io.off( pin )
			time.sleep( DELAY )




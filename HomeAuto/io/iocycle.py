# iocycle -- cycle IO lines as a test

import os, sys
import socket
import time
import thread

sys.path.append( "/home/jb/lib/python" )
import whereami
# sys.path.append( "/home/jb/io" )

import ioclient

# constants

SELF = "IOCycle Tester"

if whereami.HOST == "igor":
	default_pins = [ "M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7" ]
else:
	default_pins = [ "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7" ]

pulse_width = 0
cycle_time = 5*60
initial_cycle_time = 2
initial_cycle_count = 30

# connect to clients, library objects

io = ioclient.IoClient( SELF )

def cycle( pin, delay ):
	print "# on/off:"
	io.on( pin )
	if pulse_width:
		time.sleep( pulse_width )
	io.off( pin )
	time.sleep( delay )

def watcher():
	print "# watcher starts"
	try:
		while 1:
			data = io.recv()
			if not data:
				break
			print data,
	finally:
		print "# watcher exits"

def engage( pins ):
	"""connect, operate, disconnect"""

	io.open()
	io.monitor( " ".join( pins ))

	print "# Connected"

	thread.start_new_thread( watcher, ())

	try:
		print "# cycle time:", initial_cycle_time 
		index = 0
		for t in xrange( initial_cycle_count ):
			cycle( pins[ index ], 
				initial_cycle_time )
			index = ( index + 1 ) % len( pins )

		print "# cycle time:", cycle_time 
		index = 0
		while 1:
			cycle( pins[ index ], cycle_time )
			index = ( index + 1 ) % len( pins )
	finally:
		io.close()

def server( pins ):
	"""server process"""

	print "#####################################"
	print "# Starting", SELF
	print "#####################################"

	while 1:
		engage( pins )
		print "Disconnected (exited)"
		time.sleep( 2 )

	print "#####################################"
	print "# Stopping", SELF
	print "#####################################"

if __name__ == "__main__":

	if len( sys.argv ) > 1:
		pins = sys.argv[1:]
	else:
		pins = default_pins

	print "# pins:", pins
	server( pins )


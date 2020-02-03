# Sun daemon -- turn selected lights on at dusk 
# and off at dawn.

import os, sys
import socket
import time

sys.path.append( "/home/jb/lib/python" )
sys.path.append( "/home/jb/x10" )
sys.path.append( "/home/jb/io" )

import ioclient
import x10client
import daemonize
import logfile

logfile.DEBUG = daemonize.DEBUG = 0

# constants

LOGPORT = 51201
LOGHOST = "localhost"

dark_sensor = "C03"
east_lights = "L0"

x10_dawn = "off porch lr fr_all bath1\n"
x10_dusk = "on porch lr bath1 fr\n"

SELF = "Sun Daemon"

# connect to clients, library objects


io = ioclient.IoClient( SELF )
x10 = x10client.X10Client( SELF )


def dox10( cmds ):
	x10.open()
	x10.x10s( cmds )
	x10.waitdone()
	x10.close()

def action( setting ):
	if setting:
		print "dusk", time.asctime()
		io.on( east_lights )
		dox10( x10_dusk )
	else:
		print "dawn", time.asctime()
		io.off( east_lights )
		dox10( x10_dawn )

def connect():
	""" try forever to connect """
	print "Connecting..."
	while 1:
		try:
			io.open()
			break
		except socket.error:
			time.sleep( 2 )
			continue

def engage():
	io.add( dark_sensor )

	while 1:
		data = io.recv()
		if not data:
			print "eof on socket"
			break

		print data
		
		# data format should be:
		# hh:mm:ss CHANGE C03 x, where "x" is 0 or 1
		field = data.split()

		if ( field[1] <> "CHANGE" 
		and field[2] <> dark_sensor ):
			print "unexpected data:", data
			continue

		setting = int( field[3])
		action( setting )

	io.close()

def server():
	"""server process"""

	print "#####################################"
	print "# Starting"
	print "###########"

	Connected = 0

	while 1:
		try:
			connect()
			print "Connected..."
			Connected = 1
			engage()
		except:
			import traceback
			traceback.print_exc()
			break

		if Connected:
			Connected = 0
			print "Disconnected..."

	print "###########"
	print "# Stopping"
	print "#####################################"

if __name__ == "__main__":
	if len( sys.argv ) > 1:
		io.open()
		if sys.argv[1] == "-0":
			action( 0 )
		elif sys.argv[1] == "-1":
			action( 1 )
		io.close()
	else:
		log = logfile.LogFile( "sund.log" )
		daemonize.Daemonize()
		server()
		# never returns


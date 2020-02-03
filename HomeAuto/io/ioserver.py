#!/usr/local/bin/python2.2

import sys, os, string
import socket, thread
import signal, time
import Queue
import re

sys.path.append( "/home/jb/lib/python" )

from ConnectionList import *
from Connection import *
from select import *
from DevTab import *
from iocommon import *
import Serial
from util import *
import iom
import tty
import daemonize, logfile

###############################################
# server to coordinate multiple clients commanding 
# and monitoring 'io' subsystem.
###############################################

###############################################
# TODO list:
#
#	io watchdog
#	serial ports
#	reflect state results back to clients
#
#	find and FIX source of data loss

###############################################
# module global vars and constants

ECHOFLAG = 1		# => echo all comm with IO
ENABLESOUND = 0		# => start/stop sounds

logfile.DEBUG = 0
daemonize.DEBUG = 0

daemonize.Daemonize()

log = logfile.LogFileServer( "io.log", LOGPORT, SERVERHOST )

# enable connection to SoundServer or else bypass

if ENABLESOUND:
	import soundclient
	Sound = soundclient.SoundServer()
else:
	class SoundServer: 
		def sendspeech( self, text ):
			pass
	Sound = SoundServer()

# I/O queues for serial I/O

CommQOut = Queue.Queue()

def queueCmd( cmd ):
	if 0 and ECHOFLAG:
		print "queueCmd:", cmd
	CommQOut.put( "\n" + cmd + "\n" )


###############################################
# one dedicated thread for each client connection.
# only responsibility is to handle incoming commands.

class CommClient( CommandConnection ):

	def Dispatch( self, cmd ):
#		print "dispatch", cmd
		if cmd[0] == CMD_PREFIX:
			# commands to hardware get queued
			queueCmd( cmd[1:])
		else:
			# other commands handled directly
			HandleCommand( self, cmd )

# maintain a list of all active clients

ListOfClients = ConnectionList( COMPORT, SERVERHOST, CommClient )

########################################
# commands

def cmdon( self, pin ):
	queueCmd( 'A' + pin + '1' )

def cmdoff( self, pin ):
	queueCmd( 'A' + pin + '0' )

def cmdGet( self, pin ):
	pass

def cmdtoggle( self, pin ):
	queueCmd( 'N' + pin )

def cmdpulse( self, pin ):
	queueCmd( 'M' + pin )	# count?

def cmdAddMonitor( self, pin ):
	Devices.AddMonitor( self, pin )

def cmdRemMonitor( self, pin ):
	Devices.RemMonitor( self, pin )

def cmdStatus( self, pin ):
	# ?? this should send answer back to client??
	print "Clients:", len( ListOfClients )
	Devices.Status()

def cmdMode( self, args ):
	if args[0] == '0':
		# polling
		if not args[1] in "012":
			raise ArgError

	elif args[0] == '1':
		# enable events
		if not args[1] in "01":
			raise ArgError

	elif args[0] == '2':
		# enable serial and control refresh rate
		if int( arg[1:]) > 255:
			raise ArgError

	elif args[0] == '3':
		# enable scope outputs on H0-H2
		if not args[1] in "01":
			raise ArgError

	else:
		raise ArgError

	queueCmd( 'Q', args )

def cmdName( self, name ):
	self.name = name
	print "# New Comm Client Named:", self.name

def parsePinRange( arg ):
	#pin range is like 'A3-5'

	a, b = arg.split( '-', 1 )
	bank = a[0]
	a = a[ 1: ]
	if b[0] in string.letters:
		b = b[ 1: ]

	if not re.match( '^\\d+$', a ) \
	or not re.match( '^\\d+$', b ):
		raise ArgError

	r = []
	for i in xrange( int( a ), int( b ) + 1 ):
		r.append( bank + i2pin( i ))

	return r

def ParseArgs1( cmdfn, self, args ):
	def ParsePin( arg ):
		if arg[1] == '*':
			if len( arg ) > 2:
				raise ArgError

			return [ arg[0].upper() + '*' ]

		if '-' in arg:
			return parsePinRange( arg )

		return [( arg[0].upper() + s2pin( arg[ 1: ]))]

	# two pass so errs block entire command
	# and to provide for 1:n expansion

	res = []
	for arg in args.split():
		res.extend( ParsePin( arg ))

	for arg in res:
		cmdfn( self, arg )

def ParseArgs0( cmdfn, self, args ):
	cmdfn( self, [ args ])

CmdTab = { 
	'0': ( ParseArgs1, cmdoff ), 
	'1': ( ParseArgs1, cmdon ), 
	'T': ( ParseArgs1, cmdtoggle ), 
	'P': ( ParseArgs1, cmdpulse ), 
	'GET': ( ParseArgs1, cmdGet ),
	'ADD': ( ParseArgs1, cmdAddMonitor ),
	'REM': ( ParseArgs1, cmdRemMonitor ),
	'STAT': ( ParseArgs0, cmdStatus ),
	'MODE': ( ParseArgs0, cmdMode ),
	'NAME': ( ParseArgs0, cmdName ),
	}

def HandleCommand( self, command ):
	# print command
	cmd = command.strip().upper()

	if ' ' in cmd:
		cmd, args = cmd.split( ' ', 1 )
	else:
		args = None

	if not cmd in CmdTab.keys():
		print "ERROR: Illegal command:", command
		return

	argfn = CmdTab[ cmd ][0]
	cmdfn = CmdTab[ cmd ][1]

	try:
		args = argfn( cmdfn, self, args )
	except ArgError:
		print "arg error:", command
		return


###############################################
# read serial port and process incoming

def PortReader():
	while 1:
		# all IO input comes through this read
		line = tty.ttyi.readline()

		if 0 and ECHOFLAG:
			print "recv:", line,
		try:
			iom.ProcessLine( line )
		except RuntimeError:
			print "IO Subsystem Restarted"
			Sound.sendspeech( "IO Subsystem Restarted" )
			send_defaults()

	# conn.send( str( rc ) + "\n" )

###############################################
# handle queued output for serial port 

def PortWriter():
	def trimleading( s ):
		if s and s[0] == "\n":
			return s[1:]
		else:
			return s

	while 1:
		cmd = CommQOut.get()
		if ECHOFLAG:
			print "send:", trimleading( cmd )

		# all output to IO goes through here...
		tty.send( cmd )

###############################################
# send default commands

Defaults = [ "Q30", "Q11" ]

def send_defaults():
	# turn off oscilliscope mode; turn on events
	for cmd in Defaults:
		queueCmd( cmd )

###############################################
# handle signals

Running = 1

def HandleSig( sig, frame ):
	global Running
	Running = 0
	if sig == signal.SIGHUP:
		print "Hup"
	elif sig == signal.SIGINT:
		print "Interrupt"
	else:
		print "Unk Sig"

###############################################
# launch the threads
# main thread idles, waiting to handle external signals

def main():
	global ECHOFLAG

	print "################################"
	print "# IOServer is starting" 
	print "################################"

	if len( sys.argv ) > 1 and sys.argv[1] == '-e':
		ECHOFLAG = not ECHOFLAG
		print "will echo serial port traffic"

	tty.Init()
	iom.Init()
	send_defaults()

	if not daemonize.DEBUG:
		signal.signal( signal.SIGHUP, HandleSig )
		signal.signal( signal.SIGINT, HandleSig )

	# these threads must start in this order:

	thread.start_new_thread( PortReader, ())
	thread.start_new_thread( PortWriter, ())

	Serial.Init( CommQOut  )

	print "IO Server is starting"
	Sound.sendspeech( "IO server is starting" )

	try:
		while Running:
			signal.pause()
	finally:
		print "IO Server is exiting"
		Sound.sendspeech( "IO Server is exiting" )

main()

import sys, os, string
import socket, thread
import signal, time
import Queue
import re

from ClientList import *
from playsounds import *
from select import *
from DevTab import *
import soundclient
from iocommon import *
import LogFile
import Serial
from util import *
import iom
import tty

###############################################
# server to coordinate multiple clients commanding and monitoring
# 'io' subsystem.
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

ECHOFLAG = 0	# => echo all comm with IO

# maintain a list of all active clients

ListOfClients = Clients()
ListOfLoggers = Clients()

Sound = soundclient.SoundServer()

# I/O queues for serial I/O

CommQOut = Queue.Queue()

def queueCmd( cmd ):
	# print "queueCmd:", cmd
	CommQOut.put( "\n" + cmd + "\n" )

###############################################
# one dedicated thread for each client connection.
# only responsibility is to handle incoming commands.

class CommClient( Client ):

	def add( self ):
		ListOfClients.append( self )

	def remove( self ):
		ListOfClients.remove( self )

	def close( self ):	
		self.sock.close()

	def Main( self ):
		self.add()
		LogFile.outcs( "New Comm Client" )
		print "New Comm Client:"

		pending = ""
		while 1:
			data = self.sock.recv( 666 )
			if not data:
				break
			pending += data
#			print "recv:", data

			# only whole lines constitute a command

			while '\n' in pending:
				pos = pending.index( '\n' )
				cmd = pending[ : pos ]
				pending = pending[ pos+1 : ]

				self.Dispatch( cmd )

		LogFile.outcs( "End Comm Client: " + self.name )
		print "End Comm Client:", self.name
		self.exit()

	def Dispatch( self, cmd ):
#		print "dispatch", cmd
		if cmd[0] == CMD_PREFIX:
			# lower level commands get queued
			queueCmd( cmd[1:])
		else:
			HandleCommand( self, cmd )

	def exit( self ):
		Devices.Withdraw( self )
		self.remove()
		self.close()

########################################
# commands

def cmdon( self, pin ):
	queueCmd( 'A' + pin + '1' )

def cmdoff( self, pin ):
	queueCmd( 'A' + pin + '0' )

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
	print "Loggers:", len( ListOfLoggers )
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
	LogFile.outcs( "New Comm Client Named: " + self.name )

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

def ParsePins1( args ):
	def ParsePin( arg ):
		if arg[1] == '*':
			if len( arg ) > 2:
				raise ArgError

			return [ arg[0].upper() + '*' ]

		if '-' in arg:
			return parsePinRange( arg )

		return [( arg[0].upper() + s2pin( arg[ 1: ]))]

	res = []
	for arg in args.split():
		res.extend( ParsePin( arg ))

	return res

def ParsePins0( args ):
	return [ args ]

CmdTab = { 
	'0': ( ParsePins1, cmdoff ), 
	'1': ( ParsePins1, cmdon ), 
	'T': ( ParsePins1, cmdtoggle ), 
	'P': ( ParsePins1, cmdpulse ), 
	'ADD': ( ParsePins1, cmdAddMonitor ),
	'REM': ( ParsePins1, cmdRemMonitor ),
	'STAT': ( ParsePins0, cmdStatus ),
	'MODE': ( ParsePins0, cmdMode ),
	'NAME': ( ParsePins0, cmdName ),
	}

def HandleCommand( self, cmd ):
	# print cmd
	cmd = cmd.strip().upper()
	if ' ' in cmd:
		cmd, args = cmd.split( ' ', 1 )
		if not cmd in CmdTab.keys():
			return
		try:
			args = CmdTab[ cmd ][0]( args )
		except ArgError:
			print "arg error"
			return
	else:
		args = None

	fn = CmdTab[ cmd ][1]
	if args:
		for arg in args:
			fn( self, arg )
	else:
		fn( self, args )


###############################################
# one dedicated thread for each client connection.
# only responsibility is to forward logfile data.

class LoggerClient( Client ):

	def Main( self ):
		print "New Logger Client:", self
		ListOfLoggers.append( self )

	def send( self, data ):
		try:
			self.sock.send( data )
		except:
			self.close()

	def close( self ):
		print "End Logger Client:", self
		ListOfLoggers.remove( self )
		self.sock.close()

###############################################
# listen for connects and dispatch to dedicated thread
# 	to handle normal command ops

def CmdListener():
	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	s.bind(( SERVERHOST, COMPORT ))

	while 1:
		s.listen(3)
		conn, addr = s.accept()
		comm = CommClient( conn, addr )
		thread.start_new_thread( comm.Main, ())

###############################################
# listen for connects and dispatch to dedicated thread
#	to handle logfile traces

def LogListener():
	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	s.bind(( SERVERHOST, LOGPORT ))

	while 1:
		s.listen(3)
		conn, addr = s.accept()
		LoggerClient( conn, addr ).Main()
		# no thread -- just keep track of socket

###############################################
# read serial port and process incoming

def PortReader():
	while 1:
		# all IO input comes through this read
		line = tty.ttyi.readline()

		if ECHOFLAG:
			print "ttyi:", line,
		try:
			iom.ProcessLine( line )
		except RuntimeError:
			Sound.sendspeech( "IO Subsystem Restarted" )
			send_defaults()

	# conn.send( str( rc ) + "\n" )

###############################################
# handle queued output for serial port 

def PortWriter():
	while 1:
		cmd = CommQOut.get()
		if ECHOFLAG:
			print "ttyo:", cmd

		# all output to IO goes through here...
		tty.send( cmd )

###############################################
# echo log data, if any, to log clients, if any

def LogWriter():
	while 1:
		data = LogFile.LogQ.get()
		ListOfLoggers.sendAll( data )

###############################################
# send default commands

def send_defaults():
	# turn off oscilliscope mode; turn on events
	defaults = "Q30\nQ11"	
	queueCmd( defaults )

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

	if len( sys.argv ) > 1 and sys.argv[1] == '-e':
		ECHOFLAG = 1
		print "will echo serial port traffic"

	tty.Init()
	iom.Init()
	send_defaults()

	thread.start_new_thread( PortReader, ())
	thread.start_new_thread( PortWriter, ())
	thread.start_new_thread( LogWriter, ())
	thread.start_new_thread( CmdListener, ())
	thread.start_new_thread( LogListener, ())

	Serial.Init( SERVERHOST, SER0PORT, CommQOut  )

	signal.signal( signal.SIGHUP, HandleSig )
	signal.signal( signal.SIGINT, HandleSig )

	Sound.sendspeech( "IO server is starting" )

	try:
		while Running:
			signal.pause()
	finally:
		Sound.sendspeech( "IO Server is exiting" )

main()

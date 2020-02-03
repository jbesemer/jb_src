from __future__ import generators

###############################################
# server to coordinate multiple clients commanding 
# and monitoring x10 subsystem.
###############################################

import sys, os, string
import socket, thread
import signal, time
import Queue
import re
sys.path.append( "/home/jb/lib/python" )

import logfile
from LockedList import *
from ConnectionList import *
from Connection import *
from x10common import *
from TimeoutCalc import *
import ttyrawio
from util import *
import soundclient
from Tracker import *
import daemonize


###############################################
# TODO list:
#

##############################
# global parameters/constants
#

log_filename = "x10.log"

tty_filename = "/dev/ttyS1"

ECHOFLAG = 0	# => echo all socket input

ENABLE_SOUND = 0

logfile.DEBUG = daemonize.DEBUG = 1


#################################
# instantiate/initialize subordinate objects
#

# master logfile
log = logfile.LogFile( SERVERHOST, LOGPORT, log_filename )

# redirect all I/O to log file and detach from tty
daemonize.Daemonize( log )

# object to track signal states as we discover them
tracker = Tracker()

for h in "ABCDEFGHIJKLMNOP":
	for u in xrange( 16 ):
		tracker.addunit( Unit( "%s%02d" % ( h, u+1 )))

# serial port I/O authority
tty = ttyrawio.RawTtyIO( tty_filename )

# calculate expected timeouts for various commands
calc_timeout = TimeoutCalculator()

# Queues for commands to the hardware
CommQOut = Queue.Queue()

# provision for speech
if ENABLE_SOUND:
	Sound = soundclient.SoundServer()
	def say( text ): Sound.sendspeech( text )
else:
	def say( text ): pass



###############################################
# one dedicated thread for each client connection.
# The Dispatch() method handles incoming commands 
# and return results.

class ClientConn( Connection ):

	def Dispatch( self, command ):
		cmd, args = command.split( " ", 1 )
		cmd = cmd.lower()

		try:

			if cmd == "name":
				self.setname( args )

			elif cmd == "add":
				# add watchers
				for unit in args.split():
					tracker[ unit ].add( self )
				self.Reply()

			elif cmd == "rem":
				# remove watchers
				for unit in args.split():
					tracker[ unit ].rem( self )
				self.Reply()

			elif cmd == "get":
				# query status
				res = ""
				print "get:", args
				for unit in args.split():
					res += `tracker[ unit ]` + "\n"
				print "get.res:", res
				self.Reply( res )

			elif cmd == "send":
				CommQOut.put(( self, args ))

			else:
				print "# Unrecognized command:", command

		except Exception, ex:
			self.Error( `ex` )


	def exit( self ):
		tracker.remall( self )
		Connection.exit( self )

# maintain a list of all active clients

ListOfClients = ConnectionList( SERVERHOST, OPPORT, ClientConn )


###############################################
# coordination between PortReader and PortWriter
#

monitor = LockedList()
monitor.add( tracker )	# tracker is a permanant listener


###############################################
# read serial port, echo and process incoming status

def PortReader():
	while 1:
		# all X10 input comes through this read
		line = tty.getline( timeout=None )

		if line:
			print "# recv: " + line + "\n",
			monitor.put( line )


###############################################
# handle queued output for serial port 

ReaderQ = Queue.Queue()

def PortWriter():
	while 1:
		# get an incomming command
		sender, args = CommQOut.get()

		# send command and sender sees all results
		monitor.add( ReaderQ )
		logfile.add( sender )

		# execute the commands one by one
		for code in args.split():
				send_x10( code )

		# no longer need these two listeners
		logfile.rem( sender )
		monitor.rem( ReaderQ )

		# reply to sender and restore default timeout
		sender.Reply()
		tty.settimeout( 1.0 )


##################################
# command / response protocol

def send_x10( cmd, maxRetries=9 ):
	"""	send a command and retry until a proper 
		reply is received from the hardware or
		the retry count is exhausted.
	"""

	for retry in xrange( maxRetries ):

		if retry:
			time.sleep( 1.0 )

		# all output to X10 goes through here...
		# send the command and fetch return response

		tty.settimeout( calc_timeout( cmd ))
		print "# send:", cmd
		tty.send( cmd )

		# the response we're looking for necessarily passes
		# through a dedicated reader thread.  We set up this
		# temporary queue so that copies are forwarded here
		# until we ultimately provoke and see the results 
		# we need (or we give up trying after many failures).

		res = ReaderQ.get()

		# check X10's response and interpret result.
		# most cases are unlikely, fall through and 
		# result in a retry.

		if res == None:
			# timed out waiting for response
			print "#", "recv: tty.getline() timed out"

		elif res == ( "?" + cmd ):
			# this means the command was a syntax error;
			# we will retry but not as many times.
			print "# recv: -- ERROR returned from X10:", quote( res )
			if retry >= 2:
				print "# recv: Retry count exceeded"
				break	# <<<<<<<<<<<< ERROR RETURN

		elif res[0] == "?":
			# command probably was garbled on output
			print "# recv: -- ERROR returned from X10:", quote( res )

		elif res == ">XXX":
			# probably a collision
			print "# recv: -- command was garbled:", quote( res )

		elif res == ( "!" + cmd ) or res == ( ">" + cmd ):
			# expected response -- echoing back our command in 1 of 2 ways
					#  <<<<<<<<<<<<<<<<<<<<<<<<<<<<
			break	#  <<<<<<<<<<<<<< NORMAL RETURN
					#  <<<<<<<<<<<<<<<<<<<<<<<<<<<<

		elif res[0] == ">":
			# unexpected response -- some other command
			# in lieu of expected
			monitor.put( line )
			pass

		else:
			print "# recv: -- unexpected result (", quote( res ), ")"


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
	sys.stdout.flush()


###############################################
# launch the threads
# main thread idles, waiting to handle external signals

def main():
	global ECHOFLAG

	if len( sys.argv ) > 1 and sys.argv[1] == '-e':
		ECHOFLAG = not ECHOFLAG
		print "will echo serial port traffic"

	signal.signal( signal.SIGHUP, HandleSig )
	signal.signal( signal.SIGINT, HandleSig )

	print "\n#####################################"
	print "### X10 server is starting"
	say( "X10 server is starting" )

	# these threads must start in this order:

	thread.start_new_thread( PortWriter, ())
	thread.start_new_thread( PortReader, ())

	try:
		while Running:
			signal.pause()
	finally:
		print "### X10 server is exiting"
		say( "X10 Server is exiting" )

main()

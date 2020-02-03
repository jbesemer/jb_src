#! /usr/local/bin/python2.2

#########################################################
# LogFile -- manage daemons' log files
#
#	this class implements the several output functions necessary
#	to imitate a "file" object, as used by system print functions.
#	When instantiated, it intercepts all "print" commands, plus 
#	writes to stdout and stderr.
#
#	For maximum reliability, the file is opened, data is written
#	(appended) to and the file is closed.  In modern computers,
#	file/buffer/inode data presumably is cached so performance is
#	not an issue.
#
# LogFileServer -- launch a ConnectionList server for external 
#		logfile access
#
#	This class extends LogFile to provide for third parties to hook 
#	in and receive a copy of all the logged data.  Writes to the log
#	are addtionally queued to a separate LogWrite thread.  The LogWriter
#	then forwards the log data to all remote clients.  This means clients 
#	get slightly slower service but the main app runs unimpeded.  
#
#	In addition to Connections, which are automatically added and
#	removed, per external socket connects, Watchers can be any object that 
#	implements a method named "put()" which accepts a string argument.
#	These watchers have to be manually added via the add() and rem()
#	methds in the LockedList superclass.  
#
#

########################
# TODO:
#
#	Refine LogFileServer.LogConnection so that clients can 
#	scroll back to prior history.
#
#	Print commands normally generate multiple writes, one for 
#	each element, PLUS an extra one for the trailing newline.
#	As exhibited in test2, the present implementation allows
#	interleaved threads to intermingle the output from their 
#	individual prints.
#	Solution would be to revise LogFile.write() to cache partial
#	lines on a per-thread basis and output them with a single _write().
#	IIRC, there's some hack for per-thread variables.
#	However, the problem does not arise all that often and the risk
#	of some data getting lost makes it rather unattrtactive.

from __future__ import nested_scopes

import os, sys, time, re
import thread
import socket
import Queue

from ConnectionList import *
from Connection import *

DEBUG = 0

#########################################################
# Re-route stdout and stderr to an external log file.
# Prefix each line with a timestamp.
# Insert date stamps when to indicate day change.
# Guard writes with thread lock, so that multiple threads
# do not muck up data.
# Echo all traffic to console in DEBUG mode.

class LogFile( object ):

	"""special version of file class for logging info"""

	def __init__( self, filename ):

		# req'd properties of file-like object (most we don't use):

		self.name = filename
		self.mode = "a"
		self.softspace = 0
		self.closed = 0		# externally we say we're NOT closed

		# extra state for timestamps, etc.

		self.file = None
		self.complete = 1
		self.prev_day = None
		self.isclosed = 1	# actual state of self.file

		# semaphore to serialize multi threaded writes
		
		self.mutex = thread.allocate_lock()

		# reroute outputs to error log
		# (arguably, caller should do this surgery)

		sys.stdout = self
		if not DEBUG: 
			sys.stderr = self

	def close( self ):
		self.closed = 1
		assert( 0 )		# nobody should close stdout

	def _open( self ):
		"""	acquire mutex and open file """

		self.mutex.acquire()
		assert( self.isclosed )
		self.isclosed = 0
		self.file = open( self.name, self.mode )

	def _close( self ):
		"""	flush and close file and release mutex """

		assert( not self.isclosed )
		self.isclosed = 1
		self.file.flush()
		self.file.close()
		self.mutex.release()

	def _write( self, str ):
		""" actually write to logfile """

		self._open()
		self.file.write( str )
		self._close()

	def _ts( self ):
		"""	generate timestamp prefix and 
			additionally a datestamp when clock rolls over
		"""

		t = time.localtime()
		ts = "%02d:%02d:%02d " % ( t[3], t[4], t[5] )

		# if date has changed since last record,
		# prefix this line with a day-time stamp

		this_day = ( t[0], t[1], t[2], t[8])
		if self.prev_day != this_day:
			self.prev_day = this_day
			ts = ( ts
				+ "# "
				+ time.asctime( t )
				+ "\n"
				+ ts )
		return ts

	def write( self, str ):

		""" write, prefixing each line with a timestamp """

		# if prev output line ended with nl then prepend with timestamp
		
		if self.complete:
			str = self._ts() + str

		if DEBUG: 
			try:	sys.__stdout__.write( str )
			except:	pass

		self._write( str )

		self.complete = ( len( str ) > 0 and str[-1] == "\n" )

class obsolete_LogFile_methods:

	# these are valid file functions but they evidently
	# aren't used by print, so I left them out.  

	def append( self, str ):
		""" write, omitting timestamp prefixes """

		self._write( str )

	def writelines( self, list ):
		""" write multiple lines, omitting timestamp prefixes """

		for item in list:
			self.write( item )

	def tell( self ):
		""" tell file position """
		
		# when opening for append, this is the same as file size
		# (although tell() returns 0 if seek is omitted)

		RELATIVE_TO_ENDFILE = 2
		self._open()
		self.file.seek( 0, RELATIVE_TO_ENDFILE )
		offset = self.file.tell()
		self._close()
		return offset

	def flush( self ):
		pass

#########################################################
# A LogFileServer performs all the functions as a LogFile.
# Additionally, it launches a socket listener thread, which
# echos all log data to third parties so long as they maintain
# a connection to the LogFileServer.
# 

class LogFileServer( LogFile, ConnectionList ):

	def __init__( self, filename, port=None, host="" ):

		# init logfile
		LogFile.__init__( self, filename )

		# create queue
		self.LogQ = Queue.Queue()

		# start writer (which sleeps on LogQ)
		self.StartWriter()

		# now we're ready to launch the ConnectionList 
		# to handle incoming requests

		ConnectionList.__init__( self, port, host, self.LogConnection )


	# refine LogFile's _write to additionally queue 
	# data to the LogWriter.

	def _write( self, str ):

		LogFile._write( self, str )
		self.LogQ.put( str )
		

	###############################################
	# LogWriter is a thread that copies data from
	# log queue to each of any log file listeners.

	def LogWriter( self ):

		""" thread: copy log data to file and to log clients """
		
		print "Started LogWriter"

		while 1:
			data = self.LogQ.get()
			self.put( data )		# forward to watchers, if any

	def StartWriter( self ):
	 	thread.start_new_thread( self.LogWriter, ())

	###############################################
	# one dedicated connection for each client connection.
	# only responsibility is to forward log data and
	# delete themselves when socket closes.

	class LogConnection( Connection ):

		def __init__( self, sock, addr ):
			Connection.__init__( self, sock, addr, "LogWatcher" )

		def main_thread( self ):
			self.commands = gen_sock_getline( self.sock )
			for cmd in self.commands:
				print cmd	
					# there are no specific commands for now



###############################################
# unit test

if __name__ == "__main__":
	import threading

	N = 10

	class Countdown:
		def __init__( self, N ):
			self.K = N
			self.lock = thread.allocate_lock()
			self.done = threading.Event()
			self.done.clear()

		def down( self ):
			self.lock.acquire()
			self.K -= 1
			res = ( self.K == 0 )
			if res:
				self.done.set()
			self.lock.release()
			return res

		def wait( self ):
			self.done.wait()

	def test1():
		print "################################### Test1:"

	#	log = LogFile( "out" )
		log = LogFile( "/dev/tty" )
		sys.stdout = log

		countdown = Countdown( N )

		def fn( id ):
			log.write( "Starting #%d\n" % id )
			if id & 1:
				time.sleep( 1 )
			else:
				time.sleep( 3 )
			log.write( "Middle #%d\n" % id )
			time.sleep( 1 )
			log.write( "Exiting #%d\n" % id )

			countdown.down()

		log.write( "Begin Test1...\n" )
		for id in xrange( N ):
			thread.start_new_thread( fn, ( id, ))

		countdown.wait()
		log.write( "Test1 Finished...\n" )

	def test2():
		print "################################### Test2:"

	#	log = LogFile( "out" )
		log = LogFile( "/dev/tty" )
		sys.stdout = log

		countdown = Countdown( N )
		log.prefix = "test2 "
		
		def fn( id ):
			print "Starting #", id
			if id & 1:
				time.sleep( 1 )
			else:
				time.sleep( 3 )
			print "Middle #", id
			time.sleep( 1 )
			print "Exiting #", id

			countdown.down()

		print "Test2 Begin..."
		for id in xrange( N ):
			thread.start_new_thread( fn, ( id, ))

		countdown.wait()
		print "Finished Test2..."
	
	def test3():
		print "################################### Test3:"

		import GenericClient ; Con = GenericClient.GenericClient
		import time
		host="localhost"
		port = 40001

		schedule = (( 1.5, 2 ),
					( 3.0, 3 ),
					( 1.0, 3 ),
					( 4.0, 5 ),
					( 1.0, 5 ),
					( 1.0, 5 ),
					( 1.0, 5 ),
					( 7.0, 5 ),
					( 1.0, 3 ),
					( 1.0, 1 ),
					)
		
		N = 0
		for delay, count in schedule:
			N += delay
		N += int( count ) + 5


		def test3child():

			# Unless VERBOSE flag is set, children are silent
			# except when errors arise.

			VERBOSE = 0	# echo all inputs
			
			def test3thread( m, n, id ):
				# connect, expect n lines, starting with number m
				# Con = GenericClient.GenericClient
				con = Con( host, port, "child%d" % id )
				try:
					con.open()
				except:
					print "thread %d" % id, "cannot connect"
					countdown.down()
					return
				print "thread %d" % id, "connected"

				for i in xrange( m, m+n ):
					time.sleep( 1 )
					for line in con.readline:
						if VERBOSE:
							print ( "Thread%d " % id ) + "reads: " + line + "\n",
						fields = line.split()
						if fields[1] == "!!!":
							break
					num = int( fields[2])
					if i <> num:
						print "??? thread%d " %id, "expected", i, "got", line

				print "thread %d" % id, "exits"
				con.close()
				countdown.down()

			countdown = Countdown( len( schedule ))
			t = 0
			id = 1
			for delay, count in schedule:
				if delay:
					time.sleep( delay )
					t += delay
				start = int( t ) + 1
				print "starting thread", id, "at", t, "for", count
				thread.start_new_thread( test3thread, ( start, count, id ))
				id += 1

			countdown.wait()

		def test3parent():
			log = LogFileServer( "/dev/tty", port, host )
		#	log = LogFileServer( "out", port, host )

			print "Test3 duration:", N

			for i in xrange( N ):
				log.write( "!!! %03d\n" % i )
				time.sleep( 1 )

		pid = os.fork()
		if pid:
			print "child PID:", pid
			test3parent()
			os.wait()
			print "test3 parent exits"
		else:
			test3child()
			print "test3 child exits"
			sys.exit(0)

	def test4():
		print "################################### Test4:"
		# raise an exception -- should appear in log file
		x=y
		
	test1()
	test2()
	test3()
	test4()

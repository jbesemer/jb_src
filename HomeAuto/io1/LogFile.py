########################################
# output

import os, sys
from time import time, localtime, asctime
from string import *
from UserFile import UserFile 
import thread
import Queue

########################################
# config options

# EchoFlag = 1

########################################
# logfilename, default modes

LogFilename = "io.log"
LogFileMode = "a"

LogQ = Queue.Queue()

########################################
# logfile properties

class LogFile( UserFile ):

	def __init__( self, filename = None ):
		UserFile.__init__( self )
		self.Filename = filename
		self.mutex = thread.allocate_lock()

	def open( self ):
		self.mutex.acquire()

		UserFile.open( self, self.Filename, LogFileMode )
		if not self.File:
			print "Cannot open log file:", LogFilename
		# else:
	 	#	print "Opened log file:", self.File

		return self.File

	def close( self ):
		self.File.close()
		self.mutex.release()

	def writeline( self, s ):
		line = ts() + s + "\n"

		self.open()

		if self.File:
			UserFile.write( self, line )
			self.flush()

		self.close()

#		if EchoFlag:
#			print line,
		LogQ.put( line )

	def writelines( self, list ):
		self.open()
		for item in list:
			self.writeline( self, item )
		self.close()


# one and only logfile

Logfile = LogFile( LogFilename )

# various output conventions

def outs( str ):

	"output string"

	Logfile.writeline( str )

def outcs( str ):

	"output comment string"

	outs( "# " + str )

def outes( str ):

	"echo input line"

	outs( "! " + str )


########################################
# form a timestamp

prev_tv = (0,0,0,0)

def ts():
	global prev_tv

	t = localtime( time())
	next_tv = ( t[0], t[1], t[2], t[8])
	if prev_tv != next_tv:
		prev_tv = next_tv
		outcs( asctime( t ))
		t = localtime( time())
	return "%02d:%02d:%02d " % ( t[3], t[4], t[5] )



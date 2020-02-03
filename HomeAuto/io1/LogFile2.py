########################################
# output

import os, sys
from time import time, localtime, asctime
from string import *
from UserFile import UserFile 

########################################
# config options

EchoFlag = 1

########################################
# logfilename, default modes

LogFilename = "io.log"
LogFileMode = "a"

########################################
# logfile properties

class LogFile( UserFile ):

	def __init__( self, file = None ):
		UserFile.__init__( self, file )

	def open( self ):
		UserFile.open( self, LogFilename, LogFileMode )
		if not self.File:
			print "Cannot open log file:", LogFilename
		# else:
	 	#	print "Opened log file:", self.File

		return self.File

	def writeline( self, s ):
		line = ts() + s + "\n"
		if self.File:
			UserFile.write( self, line )
			self.flush()

		if EchoFlag:
			print line,

	def writelines( self, list ):
		for item in list:
			self.writeline( self, item )


# one and only logfile

Logfile = LogFile()

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



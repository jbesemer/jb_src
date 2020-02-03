########################################
# output

import os, sys
from time import time, localtime, asctime, sleep
from string import *
from UserFile import UserFile 

########################################
# logfilename, default modes

LogFilename = "io.log"
LogFileMode = "a"

EchoFlag = 1

########################################
# logfile properties

class LogFile( UserFile ):

	def __init__( self, filename ):
		UserFile.__init__( self )
		self.filename = filename

	def open( self ):
		UserFile.open( self, LogFilename, LogFileMode )
		if not self.File:
			print "Cannot open log file:", LogFilename
		# else:
	 	#	print "Opened log file:", self.File

		return self.File

	def close( self ):
		self.File.close()

	def _writeline( self, item ):
		line = ts() + item + "\n"
		if self.File:
			UserFile.write( self, line )
			self.flush()

		if EchoFlag:
			print line,

	def writeline( self, item ):
		self.open()
		self._writeline( item )
		self.close()

	def writelines( self, list ):
		self.open()
		for item in list:
			self._writeline( item )
		self.close()


########################################
# form a timestamp

prev_tv = (0,0,0,0)

def ts():
	global prev_tv

	t = localtime( time())
	next_tv = ( t[0], t[1], t[2], t[8])
	if prev_tv != next_tv:
		prev_tv = next_tv
		# outcs( asctime( t ))
		t = localtime( time())
	return "%02d:%02d:%02d " % ( t[3], t[4], t[5] )

def test():
	Logfile = LogFile( LogFilename )
	while 1:
		sleep( 1.0 )
		Logfile.writelines([ "tweedle dee", "tweedle dum" ])

test()

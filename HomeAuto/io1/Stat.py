########################################
# track various statistics

from time import time, localtime, asctime
from string import *

from util import *


class Stat:
	def __init__( self ):
		self.lines = self.bytes = 0
		self.t0 = time()


	def InLine( self, line ):
		self.lines = self.lines + 1
		self.bytes = self.bytes + len( line )


	def BlockBegin( self, line ):
		if len( line ) > 1:
			k = c2b( line[ 1 ])
		else:
			k = 4
		if len( line ) > 2:
			l = 1 << c2b( line[ 2 ])
		else:
			l = 128
		if l > 1024:
			l = 1024
		m = k * 1024 / l

		# print "line[1,2]:", line[1], line[2]

		outcs( "DIAG Absorbing block serial data, " 
			+ i2s( k ) + "K, " 
			+ i2s( m ) + " * " + i2s( l ) + " char lines" )

		self.t0 = time()
		self.BeginLines = self.lines
		self.BeginBytes = self.bytes


	def BlockEnd( self ):

		t1 = time()
		dt = t1 - self.t0
		lines = self.lines - self.BeginLines
		bytes = self.bytes - self.BeginBytes

		outcs( "DIAG Absorbed " + i2s( lines ) + " lines, " 
			+ i2s( bytes ) + " bytes, " 
			+ i2s( dt ) + " sec, " 
			+ f2s( bytes / dt ) + " bytes/sec, " 
			+ f2s( lines / dt ) + " lines/sec" )



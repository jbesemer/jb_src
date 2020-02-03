## status / error logger

import sys
import time
from util import *

class Logger:
	"funnel various program outputs through a single stream"

	def __init__( self, stream=sys.stdout):
		self.setstream( stream )
		self.errors = 0

	def setstream( self, stream ):
		self.stream = stream

	def ts( self ):
		year,month,day,hour,min,sec,wd,jd,dst = time.localtime()
		return "%02d:%02d:%02d" % ( hour, min, sec )

	def write( self, string ):
		self.stream.write( string )

	def echo( self, where, what ):
		ts = self.ts()
		self.write( "%s %s %s\n" % ( ts, where, quote( what )))

	def echo_send( self, what ):
		self.echo( 'send:', what )

	def echo_recv( self, what ):
		if what == None:
			self.echo( 'recv:', "[Timeout]" )
		else:
			self.echo( 'recv:', what )

	def err( self, fmt, *args ):
		self.echo( "Error:", fmt % args )
		self.errors += 1

	def warn( self, fmt, *args ):
		self.echo( "Warning:", fmt % args )

class SLogger( Logger ):
	"capture program outputs in string buffer"

	def __init__( self ):
		Logger.__init__( self, StringIO.StringIO())

	def value( self ):
		return self.stream.getvalue()

	def append( self ):
		file = open( log_file, "a" )
		file.write( self.value())
		file.close()

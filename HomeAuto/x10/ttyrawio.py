
import os
import time
import rawio;	RawIO=rawio.RawIO

# tty parameters

echodefault = 0

default_tty_name = "/dev/ttyS1"
default_stty_flags = ( "2400 cs8 cstopb -echo -echoctl -ignbrk"
		+ " -ignpar icrnl -isig -icanon -tostop" )
default_timeout = 1.5

class dumblog:
	def echo_recv( self, text ):
		print "ttyi:", text

	def echo_send( self, text ):
		print "ttyo:", text


class nonelog:
	def echo_recv( self, text ):	pass
	def echo_send( self, text ):	pass


##################################
# tty I/O

class RawTtyIO( RawIO ):

	def __init__( self, 
				tty_name=default_tty_name, 
				log=dumblog(), 
				timeout=default_timeout,
				stty_flags=default_stty_flags ):
		
		if log == None:
			self.log = nonelog()
		else:
			self.log = log

		self.tty_name = tty_name
		self.stty_flags = stty_flags
		self.timeout = timeout


		# set proper speed, etc.

		rv = os.system( "stty <%s %s" % ( self.tty_name, self.stty_flags ))
		if ( rv >> 8 ) != 0:
			self.log.warn( "unable to stty %s", self.tty_name )

		RawIO.__init__( self, self.tty_name, exception=1 )
		self.settimeout( self.timeout )

		# I believe the X10 device is powered by RS232 lines
		# that are "off" until the device is open.  And the 
		# device is not ready to use immediately after being 
		# powered up.  Previous attempts to send/recv usually
		# (always) resulted in a timeout and masked the problem.
		# anyway, sending without the delay introduces errors.

		time.sleep( 0.25 )

		# self.send( "\0" )
		# self.getline( ignoreblanks=echodefault )

		startTime = time.time()

	def send( self, cmd, echo=0 ):
		self.put(  cmd + "\r" )
		# if cmd and echo:
		if echo:
			self.log.echo_send( cmd )

	def getline( self, timeout=None, ignoreblanks=1, echo=None ):
		if echo==None: echo = echodefault
		try:
			res = RawIO.getline( self, 
						timeout=timeout, 
						ignoreblanks=ignoreblanks )
		except rawio.RawIOTimeout, ex:
			res = None

		if echo and res:
				self.log.echo_recv( res )
		return res

	def watch( self ):
		while 1:
			res = RawIO.getline( self, wait=0 )
			self.log.echo_recv( res )


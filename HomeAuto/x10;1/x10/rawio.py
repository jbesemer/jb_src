import select, termios, sys, os

DEFAULT_TIMEOUT = 0.5

_members_ = []

class RawIOTimeout:
	def __init__( self, line="", timeout=0 ):
		self.line = line
		self.timeout = timeout

def cleanup_console():
	for member in _members_:
		member._close()

class RawIO:

	def __init__( self, 
			devicename=None, 
			timeout=DEFAULT_TIMEOUT,
			exception = 0 ):

		self.timeout = timeout 

		if devicename:
			self.open( devicename )

		if exception:
			self.timeout_result = self.timeout_result_raise
		else:
			self.timeout_result = self.timeout_result_noraise

	def timeout_result_raise( self, line, timeout ):
		raise RawIOTimeout( line, timeout )

	def timeout_result_noraise( self, line, timeout ):
		return None  # note: this is similar to "" but different

	def open( self, devicename, timeout=None ):
		self.filename = devicename
		if timeout:
			self.timeout = timeout 

		self.ifile = open( devicename, "r", 1 )
		self.ofile = open( devicename, "w", 1 )
		self.ifd = self.ifile.fileno()
		self.ofd = self.ofile.fileno()
		self.old = termios.tcgetattr( self.ifd )
		self.new = termios.tcgetattr( self.ifd )

		self.new[3] = ( self.new[3]
				& ~termios.ICANON
				& ~termios.ECHO )
		self.new[6][termios.VMIN] = 1
		self.new[6][termios.VTIME] = 0
		termios.tcsetattr( 
				self.ifd, 
				termios.TCSANOW, 
				self.new )

		# restore terminal modes on exit...
		_members_.append( self )
		sys.exitfunc = cleanup_console

	def close( self ):
		_members_.remove( self )
		self._close()

	def _close( self ):
		termios.tcsetattr( 
				self.ifd, 
				termios.TCSAFLUSH, 
				self.old )
		self.ifile.close()
		self.ofile.close()

	def getkey( self ):
		c = os.read( self.ifd, 1 )
		return c

	def put( self, s ):
		os.write( self.ofd, s )

	def settimeout( self, timeout ):
		self.timeout = timeout

	def gettimeout( self ):
		return self.timeout

	def owait( self ):
		termios.tcdrain( self.ofd )

	def iwait( self, timeout = None ):
		if not timeout:
			timeout = self.timeout
		i, o, e = select.select( [self.ifd], [], [], timeout )
		return not i	# true if timeout

	def getline( self, timeout=None, ignoreblanks=1, ignorenulls=1, wait=1 ):
		line = ""
		while 1:
			if wait:
				if self.iwait( timeout ):
					return self.timeout_result( line, timeout )
			ch = self.getkey()
			if ch in [ '\r', '\n' ]:
				if ignoreblanks and not line:
					continue
				# if not line:
				# 	print "BLANK LINE"
				return line
			if ignorenulls and ch == '\0':
				continue
			line += ch


if __name__ == "__main__":

	tty = RawIO( "/dev/tty" )

	while 1:
		ch = tty.getkey()
		# print ch.upper()
		tty.put( ch.upper())
		if ch == 'x':
			break
		if ch == "g":
			tty.put( chr( 7 ))
			line = tty.getline( 3 )
			tty.put( chr( 7 ))
			print "\nline:", line


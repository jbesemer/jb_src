import os, sys
import string
import socket
import thread

# SPEECH_SERVER="cascade-sys.com" 
SPEECH_SERVER=""   # local host, same as client
	# SPEECH_SERVER="192.168.0.1" 
	# SPEECH_SERVER="192.168.0.120" 
SPEECH_SERVER = socket.gethostbyname( SPEECH_SERVER )
BATCH_PORT=50011
IMMED_PORT=50012

class SoundServer:
	def __init__( self, WaitFlag = 0 ):
		self.wait = WaitFlag

	def open( self, verbose = 0 ):
		self.s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		# print "connecting to", SPEECH_SERVER, "..."
		
		self.dest = ( SPEECH_SERVER, BATCH_PORT )

		self.s.connect( self.dest )

		if verbose:
			self.say( "connected to speech server" )

	def say( self, data ):
		self.s.send( data )

	def close( self, verbose = 0 ):
		if verbose:
			self.say( "disconnecting from speech server" )

		self.s.shutdown( 1 )

		while self.wait:
			data = self.s.recv( 666 )
			if not data:
				break
#			print "Recd:", data,

		self.s.close()

	def sendspeech( self, data ):
		self.open()
		self.say( data )
		self.close()

class SoundServerImmed( SoundServer ):
	def __init__( self, WaitFlag = 0 ):
		self.wait = WaitFlag

	def open( self, verbose = 0 ):
		self.s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		# print "connecting to", SPEECH_SERVER, "..."
		
		self.dest = ( SPEECH_SERVER, IMMED_PORT )

		self.s.connect( self.dest )

		if verbose:
			self.say( "connected to speech server" )

	def say( self, data ):
		self.s.send( data + '\n' )


if __name__ == "__main__":
	WaitFlag = 1
	ImmedFlag = 0

	def reader():
		text = ""
		while 1:
			if sys.stdin.isatty():
				sys.stdout.write( ">>> " )
			data = sys.stdin.readline()
			if not data:
				break
			text += data
		return text

	def getspeech():

		if len( sys.argv ) > 1:
			return string.join( sys.argv[1:])
		else:
			return reader()

	if "-w" in sys.argv:
		WaitFlag = not WaitFlag
		sys.argv.remove( "-w" )
	
	if "-i" in sys.argv:
		ImmedFlag = not ImmedFlag
		sys.argv.remove( "-i" )

	if ImmedFlag:
		server = SoundServerImmed( WaitFlag )
		server.open()
		while 1:
			if sys.stdin.isatty():
				sys.stdout.write( ">>> " )
			data = sys.stdin.readline()
			if not data:
				break
			server.say( data )
		server.close()
	else:
		server = SoundServer( WaitFlag )
		server.sendspeech( getspeech())


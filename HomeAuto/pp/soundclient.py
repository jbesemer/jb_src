import os, sys
import string
import socket
import thread

WaitFlag = 1

SPEECH_SERVER="cascade-sys.com" 
	# SPEECH_SERVER="192.168.0.1" 
	# SPEECH_SERVER="192.168.0.120" 
SPEECH_SERVER = socket.gethostbyname( SPEECH_SERVER )
BATCH_PORT=50011
IMMED_PORT=50012

class SoundServer:
	def __init__( self, WaitFlag = 0 ):
		self.wait = WaitFlag
		pass

	def open( self, immediate=0, verbose = 0 ):
		self.s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		# print "connecting to", SPEECH_SERVER, "..."
		
		self.immediate = immediate

		if immediate:
			self.dest = ( SPEECH_SERVER, IMMED_PORT )
		else:
			self.dest = ( SPEECH_SERVER, BATCH_PORT )

		self.s.connect( self.dest )

		if verbose:
			self.say( "connected to speech server" )

	def say( self, data ):
		if self.immediate:
			self.s.send( data + '\n' )
		else:
			self.s.send( data )

	def close( self, verbose = 0 ):
		if verbose:
			self.say( "disconnecting from speech server" )

		self.s.shutdown( 1 )

		while WaitFlag:
			data = self.s.recv( 666 )
			if not data:
				break
#			print "Recd:", data,

		self.s.close()


def sendspeech( data, WaitFlag = 0 ):

	server = SoundServer( WaitFlag )
	server.open()
	server.send( data )
	server.close()

if __name__ == "__main__":
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
		global WaitFlag

		if "-w" in sys.argv:
			WaitFlag = not WaitFlag
			sys.argv.remove( "-w" )

		if len( sys.argv ) > 1:
			return string.join( sys.argv[1:])
		else:
			return reader()

	sendspeech( getspeech(), WaitFlag )

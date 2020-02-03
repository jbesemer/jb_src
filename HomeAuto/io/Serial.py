########################################
# handle I/O to serial ports

import tty
import thread
import socket

import iocommon

# quote and newline characters

NL = "\n"
QUOTE = chr( 0x80 )
QUOTE_QUOTE = QUOTE + QUOTE
QUOTE_NL = QUOTE + NL

# serial command prefixes

CMD_SEND_0 = 22
CMD_SEND_1 = 23
CMD_SEND_B = 24

MAX_PORTS = 3

# globals, filled in from Init()

CommQOut = None

# Serial Comm objects

class SerialComm:

	def __init__( self, index ):
		self.index = index
		self.cmd = CMD_SEND_0 + index
		self.sock = None

	def active( self ):
		return self.sock != None
	
	def activate( self, sock ):
		self.sock = sock

	def deactivate( self ):
		self.sock = None

	def quote( self, data ):
		data = replace( data, QUOTE, QUOTE_QUOTE )
		data = replace( data, "\\n", QUOTE_NL  )
		return data

	def unquote( self, data ):
		if data[ -1 ] == QUOTE:
			data += "\n" 
		data = replace( data, QUOTE_NL, "\\n" )
		data = replace( data, QUOTE_QUOTE, QUOTE )
		return data
		
	def send( self, data ):		# from io to client
		# if error then deactivate
		self.sock.send( self.quote( data ))

	def recv( self ):		# from client to io
		# if error then deactivate
		data = self.sock.recv( 666 )
		return self.unquote( data )
	
	def doCopy( self ):
		while 1:
			data = recv()
			CommQOut.put( self.cmd + data + NL )


# create an array of comm objects

Comms = [ SerialComm( i ) for i in xrange( MAX_PORTS )]

# called by input side when chars received

def HandleIncoming( data ):
	if len( data ) < 3:
		return

	port = ord( data[ 1 ]) - ord( 'A' )

	if port < len( Comms ) and Comms[ port ].active:
		Comms[ port ].send( data[ 2: ])

###############################################
# listen for connects and dispatch to dedicated thread
#	to handle serial comm connections

def SerialListener( port ):
	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	s.bind(( iocommon.SERVERHOST, port ))

	while 1:
		s.listen(3)
		conn, addr = s.accept()
		Comms[ index ].activate( conn )
		Comms[ index ].doCopy()



# launch serial listeners

def Init( OutQ ):
	global CommQOut

	CommQOut = OutQ

	for i in xrange( MAX_PORTS ):
		thread.start_new_thread( 
			SerialListener, 
			( iocommon.SER0PORT + i , ))

	pass

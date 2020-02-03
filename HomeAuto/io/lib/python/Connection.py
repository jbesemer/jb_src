from __future__ import generators
import socket, thread
from getline_gen import gen_sock_getline

class Connection( object ):

	"""	read commands from a socket, dispatch them to a 
		command interpreter, maintain some internal state,
		and forward results back to originating client.
	"""

	def __init__( self, sock, addr=None, name="Unk" ):
		self.sock = sock
		self.addr = addr
		self.name = name

	def put( self, data ):
		"""send data over socket"""
		try:
			self.sock.send( data )
		except:
			return 1 #signal error

	def main_thread( self ):
		self.commands = gen_sock_getline( self.sock )
		for cmd in self.commands:
			self.Dispatch( cmd )

	def Dispatch( self, cmd ):
		pass


class CommandConnection( Connection ):

	def __init__( self, sock, addr=None, name="Unk" ):
		Connection.__init__( self, sock, addr, name )
		self.ECHOFLAG = 0

	def start( self ):
		peer = self.sock.getpeername()
		name = socket.getfqdn( peer[0] )
		self.setname( "%s %s" % ( peer[0], name ))

	def exit( self ):
		print "# End Client:", self.name
		self.sock.close()

	def setname( self, name="" ):
		"""remember the name of the client"""
		self.name = name
		print "# New Client:", name

	def main_thread( self ):
		self.start()
		Connection.main_thread( self )
		self.exit()

	def Reply( self, response=None ):
		"""send reply to client"""
		if response <> None:
			self.put( response )
		self.put( "\n#Done\n" )

	def Error( self, message="" ):
		"""send error message to client"""
		self.put( "\n#Error -- " + message + "\n" )

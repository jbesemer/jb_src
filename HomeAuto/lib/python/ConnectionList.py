###############################################
# A ConnectionList starts a thread which listens
# for connects on a particular socket and dispatchs
# a dedicated thread to handle subsequent traffic.
#
# A new object is created to handle each connection.
# Typically this object is a subclass of Connection().
#
#	If the object has a method named "main_thread", a
#	thread is launched which calls the main thread and
#	which removes the object from the ConnectionList 
#	when the main thread exits.  A thread is created
#	ONLY in this case.
#
#	If the object has no main thread then it must assume
#	responsibility for removing itself from this list 
#	when it exits.  The following will suffice:
#
#		self.ContainingList.rem( self )
#
#	The object MUST include a put(str) method, unless
#	the ConnectionList's put() method never will be called.
#	Note that an exception from the put() method will 
#	cause the member to be removed from the ConnectionList.
#
# Connection objects are added to self.list when activated
# and removed when they exit.
#

from __future__ import generators
import socket
import thread

from LockedList import *

class ConnectionList( LockedList ):

	def __init__( self, port=None, host="", handler_class=None ):

		LockedList.__init__( self )

		self.handler_class = handler_class
		self.host = host
		self.port = port

		self.StartListenerThread()
		
	def StartListenerThread( self ):
		thread.start_new_thread( self.ListenerThread, ())

	def ListenerThread( self ):

		"""	Open a socket and listen for incoming connects.
			Each connect is assigned to a unique object.
		"""

		print "Starting Listener %s:%d" % ( self.host, self.port )

		s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
		s.bind(( self.host, self.port ))

		while 1:
			s.listen( 5 )
			conn, addr = s.accept()
			
			print "Connection accepted"

			# create the new handler, 
			# add it to this list,
			# mark the handler instance with an attribute
			#	that points to the containing list, and
			# call the handler's entrypoint

			handler = self.handler_class( conn, addr )
			self.add( handler )
			handler.ContainingList = self

			if self.has_main_thread( handler ):
				thread.start_new_thread( 
					self.ThreadWrapper, 
					( handler, ))

	def ThreadWrapper( self, handler ):

		"""	call handler entry point and
			remove it from this list when through
		"""

		print "Connection handler Starts"

		handler.main_thread()
		self.rem( handler )

		print "Connection handler Exits"


	def has_main_thread( self, obj ):
		"""	return true iff an object's Class has callable 
			function fname
		"""

		try:
			return callable( obj.main_thread )
		except:
			return 0


# UNIT TESTING

if __name__ == "__main__":
	import sys, signal
	from Connection import *

	argc = len( sys.argv )
	if argc > 1:
		host = sys.argv[1]
	else:
		host = "localhost"	
		
	host = socket.gethostbyname( host )

	if argc > 2:
		port = int( sys.argv[2])
	else:
		port = 45321

	class Hand( Connection ):
		# simply echo input, locally and back to sender
		def Dispatch( self, cmd ):
			print cmd
			self.put( cmd )

	con = ConnectionList( port, host, Hand )

	for line in sys.stdin:
		con.put( line )
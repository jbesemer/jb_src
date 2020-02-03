from __future__ import generators

import socket, thread

ECHOFLAG = 0


# ClientList -- maintain a list of items, with access protected by a lock

class Clients:
	"""General client behavior"""

	def __init__( self ):
		self.lock = thread.allocate_lock()
		self.list = []

	def __len__( self ):
		self._acquire()
		n = len( self.list )
		self._release()
		return n
		
	def __getitem__( self, index ):
		return self.list[ index ]

	def _acquire( self ):
		self.lock.acquire()

	def _release( self ):
		self.lock.release()

	def add( self, item ):
		self._acquire()
		self.list.append( item )
		self._release()

	def rem( self, item ):
		self._acquire()
		self.list.remove( item )
		self._release()
	
	def put( self, data ):
		# individual puts may call back to remove
		# so we iterate on a copy of the list
		self._acquire()
		list = self.list[:]
		self._release()

		for item in list:
			item.put( data )

	def sendAll( self, data ):
		self.put( data )

class Client:
	def __init__( self, sock, addr=None ):
		self.sock = sock
		self.addr = addr
		self.name = "unk"

	def put( self, data ):
		self.sock.send( data )

	def getline( self ):
		pending = ""
		while 1:
			data = self.sock.recv( 666 )
			if not data:
				return
			pending += data

			# only whole lines constitute a command

			while '\n' in pending:
				pos = pending.index( '\n' )
				cmd = pending[ : pos ]
				pending = pending[ pos+1 : ]
				if ECHOFLAG:
					print "# get:", cmd
				yield cmd

	def setname( self, name="" ):
		self.name = name
		print "# New Client:", name

	def Main( self ):
		self.start()

		commands = self.getline()
		for cmd in commands:
			self.Dispatch( cmd )

		self.exit()

	def Reply( self, response=None ):
		if response <> None:
			self.put( response )
		self.put( "\n#Done\n" )

	def Error( self, message="" ):
		self.put( "\n#Error -- " + message + "\n" )


class Listener:
	def __init__( self, client, mask ):
		self.client = client
		self.mask = mask

	def put( self, data ):
		self.client.put( data )


class Listeners:
	"""Client who is listening for qualified events"""

	def __init__( self ):
		self.lock = thread.allocate_lock()
		self.dict = {}

	def __len__( self ):
		self._acquire()
		n = len( self.dict )
		self._release()
		return n

	def __getitem__( self, client ):
		return self.dict[ client ]

	def __setitem__( self, client, value ):
		self.acquire()
		self.dict[ client ] = value
		self.release()
		
	def _acquire( self ):
		self.lock.acquire()
		return self.dict

	def _release( self ):
		self.lock.release()

	def add( self, client, bits = 0 ):
		self._acquire()
		if client in self.dict.keys():
			self.dict[ client ] |= bits
		else:
			self.dict[ client ] = bits
		self._release()

	def rem( self, client, bits = 0 ):
		self._acquire()
		if client in self.dict.keys():
			self.dict[ client ] &= ~bits
			if self.dict[ client ] == 0:
				del self.dict[ client ]
		self._release()

	def withdraw( self, client ):
		self._acquire()
		if client in self.dict.keys():
			del self.dict[ client ]
		self._release()
	
	def sendMatching( self, bits, data ):
		self._acquire()
		items = self.dict.items()
		self._release()

		for client, mask in items:
			if bits & mask:
				try:
					client.put( data )
				except:
					self.rem( client )


###############################################
# listen for connects and dispatch to dedicated 
#	thread to handle normal command ops
#
# handler typically is a subclass of Client
#

def CmdListener( handler, host, port ):
	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	s.setsockopt( 
		socket.SOL_SOCKET, 
		socket.SO_REUSEADDR,
		1 )
	s.bind(( host, port ))

	while 1:
		s.listen( 5 )
		conn, addr = s.accept()
		comm = handler( conn, addr )
		thread.start_new_thread( comm.Main, ())


def StartCmdListener( handler, host, port ):
	thread.start_new_thread( CmdListener, ( handler, host, port ))


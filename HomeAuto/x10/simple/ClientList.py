import thread

# ClientList -- maintain a list of items, with access protected by a lock

class Clients:
	def __init__( self ):
		self.list = []
		self.lock = thread.allocate_lock()

	def __len__( self ):
		self.lock.acquire()
		n = len( self.list )
		self.lock.release()
		return n
		
	def __getitem__( self, index ):
		return self.list[ index ]

	def acquire( self ):
		self.lock.acquire()
		return self.list

	def release( self ):
		self.lock.release()

	def append( self, item ):
		self.lock.acquire()
		self.list.append( item )
		self.lock.release()

	def remove( self, item ):
		self.lock.acquire()
		self.list.remove( item )
		self.lock.release()
	
	def applyAll( self, fn ):
		self.acquire()
		for item in self.list:
			fn( item )
		self.release()

	def sendAll( self, data ):
		self.acquire()
		for item in self.list:
			item.send( data )
		self.release()

class Client:
	def __init__( self, sock, addr=None ):
		self.sock = sock
		self.addr = addr
		self.name = "unk"

	def send( self, data ):
		self.sock.send( data )

	def Main( self ):
		pass


class Listener:
	def __init__( self, client, mask ):
		self.client = client
		self.mask = mask

	def send( self, data ):
		self.client.send( data )


class Listeners:

	def __init__( self ):
		self.lock = thread.allocate_lock()
		self.dict = {}

	def __len__( self ):
		self.lock.acquire()
		n = len( self.dict )
		self.lock.release()
		return n

	def __getitem__( self, client ):
		return self.dict[ client ]

	def __setitem__( self, client, value ):
		self.acquire()
		self.dict[ client ] = value
		self.release()
		
	def acquire( self ):
		self.lock.acquire()
		return self.dict

	def release( self ):
		self.lock.release()

	def add( self, client, bits = 0 ):
		self.acquire()
		if client in self.dict.keys():
			self.dict[ client ] |= bits
		else:
			self.dict[ client ] = bits
		self.release()

	def rem( self, client, bits = 0 ):
		self.acquire()
		if client in self.dict.keys():
			self.dict[ client ] &= ~bits
		else:
			self.dict[ client ] = bits
		self.release()

	def withdraw( self, client ):
		self.acquire()
		if client in self.dict.keys():
			del self.dict[ client ]
		self.release()
	
	def sendMatching( self, bits, data ):
		self.acquire()
		for client, mask in self.dict.items():
			if bits & mask:
				client.send( data )
		self.release()

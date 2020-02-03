from __future__ import generators

import socket

import thread


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
		print "Listener.add"
		self._acquire()
		if client in self.dict.keys():
			self.dict[ client ] |= bits
		else:
			self.dict[ client ] = bits
		self._release()

	def rem( self, client, bits = 0 ):
		print "Listener.rem"

		if 0:
			import traceback,sys
			traceback.print_exc(file=sys.stdout)

		self._acquire()
		if client in self.dict.keys():
			self.dict[ client ] &= ~bits
			if self.dict[ client ] == 0:
				del self.dict[ client ]
		self._release()

	def withdraw( self, client ):
		print "Listener.withdraw"
		self._acquire()
		while client in self.dict.keys():
			del self.dict[ client ]
		self._release()
	
	def sendMatching( self, bits, data ):
		self._acquire()
		items = self.dict.items()
		self._release()

		for client, mask in items:
			if bits & mask:
				if client.put( data ):
					self.rem( client )

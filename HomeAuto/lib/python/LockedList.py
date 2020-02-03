###########################################################
# Maintain a list of items, interlocked so that members
# may be added or removed by multiple threads with impunity.
#
# A "put()" method forwards data to all list members via 
# their own respective put() methods.  Items may include any
# object that implements put(), INCLUDING other LockedList 
# instances themselves!  Instances of the system Queue() 
# class also fit this requirement.
#
# This allows for arbitrary thread safe dataflow topologies.
#
# If an element's put() method raises an exception when
# called, then that element is permanatly removed from
# the list.  This is an important feature, as many members
# implement put() by writing on sockets, and rely on the
# exception to shut down the entire connection.  
#
# Members who do NOT wish exceptions to remove them from the
# list must intercept the exceptions in their own put() method
# and prevent them from propigating upward.

from __future__ import generators

import thread

class LockedList( object ):

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
			# a true return code indicates an error. where appropriate, 
			# clients must map exceptions to return codes.
			if item.put( data ):
				self.rem( item )

	def sendAll( self, data ):
		self.put( data )


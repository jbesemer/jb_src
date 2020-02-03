
# select queue -- a queue that can be 
# included to select() system call, along
# with other selectable objects

import Queue
import os

class SelectQueue( Queue.Queue ):
	def __init__( self, maxsize=0 ):
		Queue.Queue.__init__( self, maxsize )
		self.r, self.w = os.pipe()

	def fileno( self ):
		return self.r

	def put( self, item ):
		Queue.Queue.put( self, item )
		os.write( self.w, "x" )

	def get( self ):
		os.read( self.w, 1 )
		return Queue.Queue.get( self )

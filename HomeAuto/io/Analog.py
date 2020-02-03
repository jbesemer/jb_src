########################################
# track time varying values

from string import *
from util import *


class IntStats:
	def __init__( self, n ):
		self.len = n
		self.count = n*[ 0 ]
		self.prev = n*[ 0 ]
		self.mean = n*[ 0 ]

	def add( self, index, value ):
		if 0 <= index < self.len:
			value = atoi( value )
			if self.count[ index ]:
				self.mean[ index ] = \
					( value + self.mean[ index ]) / 2
			else:
				self.mean[ index ] = value
			self.count[ index ] += 1
			self.prev[ index ] = value
			

class FloatStats:
	def __init__( self, n ):
		self.len = n
		self.count = n*[ 0 ]
		self.prev = n*[ 0.0 ]
		self.mean = n*[ 0.0 ]

	def add( self, index, value ):
		if 0 <= index < self.len:
			value = atof( value )
			if self.count[ index ]:
				self.mean[ index ] = \
					( value + self.mean[ index ]) / 2.0
			else:
				self.mean[ index ] = value
			self.count[ index ] += 1
			self.prev[ index ] = value
			
class Analog:

	def __init__( self, n = 0 ):
		self.len = n
		self.cald = FloatStats( n )
		self.raw = IntStats( n )
		self.slope = FloatStats( n )
		self.offset = IntStats( n )
		self.data = [self.cald, self.raw, self.slope, self.offset]

	def add( self, type, chan, value ):
		if 0 <= type < 4 and 0 <= chan < self.len:
			self.data[ type ].add( chan, value )

	def prev( self, type, chan ):
		if 0 <= type < 4 and 0 <= chan < self.len:
			return self.data[ type ].prev[ chan ]

	def mean( self, type, chan ):
		if 0 <= type < 4 and 0 <= chan < self.len:
			return self.data[ type ].mean[ chan ]

	def count( self, type, chan ):
		if 0 <= type < 4 and 0 <= chan < self.len:
			return self.data[ type ].count[ chan ]


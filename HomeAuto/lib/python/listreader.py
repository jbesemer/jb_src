
## peek/get list traversal -- lexical for parser

class ListReader:
	"add list elements one at a time, allow peeking"

	def __init__( self, args=None ):
		if args == None:
			self.args = []
		else:
			self.args = args
		self.index = 0

	def __len__( self ):
		return len( self.args )

	def __getitem__( self, item ):
		return self.args[ item ]

	def _nextindex( self ):
		self.index += 1
		return self.index - 1

	def tell( self ):
		return self.index

	def seek( self, index=0 ):
		self.index = index

	def rewind( self ):
		self.seek()

	def peek( self ):
		if self.index >= len( self.args ):
			return None
		else:
			return self.args[ self.index ]

	def next( self ):
		if self.index >= len( self.args ):
			raise IndexError # StopIteration
		return self.args[ self._nextindex() ]

class ListIO( ListReader ):
	def append( self, item ):
		self.args.append( item )

	def last( self ):
		if self.args:
			return self.args[ -1 ]
				# may raise IndexError

	def join( self ):
		return " ".join( self.args )

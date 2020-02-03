# parse arbitrary number streams

from util import *

def isarbnum( arg ):
	if arg:
		if   numeric( arg ):			return 1
		elif arg[:2].lower() == '0x':	return 2
		elif arg[0] == '"':				return 3
	return 0

class arbnum:
	def more( self ):
		return self.data
		
	def next_hex( self ):
		res = self.data[:2]
		self.data = self.data[2:]
		return "0x"+ res

	def next_num( self ):
		res = self.data
		self.data = None
		return "0x%02x" % int( res )

	def next_str( self ):
		res = self.data[0]
		self.data = self.data[1:]
		return "0x%02x" % ord( res )

	def __init__( self, args ):
		self.type = isarbnum( args )

		if self.type == 1:
			self.data = args
			self.next = self.next_num

		elif self.type == 2:
			self.data = args[2:]
			self.next = self.next_hex

		elif self.type == 3:
			self.data = args[1:-1]
			self.next = self.next_str


# PYISAM -- Indexed Sequential Access Method
#
# ISAM implements a way to read and write arbitrary
# strings of data which are indexed by 0 or more
# indicies.
#
# file representation on disk is as follows:
#
#	magic	= a magic string to uniquely id the file type
#	record	= zero or more data records
#
# data records are as follows:
#
#	header	= data length + flags
#	data	= data bytes
#
# data length = byte count rounded up to the next DWORD
#				(low 2 bits are ignored)
# flags = low 2 bits of data length word.
#
#		bit 0 <=> unused/deleted record
#		bit 1 <=> reserved, must be zero
#

import struct

FLAGS			= 0x3
FLAG_DELETED	= 0x1

DEFAULT_MAGIC = "PY_ISAM\n\z"

class ISAM:
	def __init__( self, filename, magic=DEFAULT_MAGIC ):
		self.filename = filename
		self.magic = magic

		if not exists( filename ):
			self.file = file( filename, "w" )
			self.file.write( self.magic )
			self.write_dword( 0 )
			self.file.close()
			
		self.file = file( filename, "wr" )
		self.check_magic()
		self.load_index()

	def check_magic( self ):
		self.file.seek( 0, 0 )
		magic = self.file.read( len( self.magic ))
		assert( magic == self.magic )

	def read_dword( self ):
		N = struct.calcsize( "i" )
		s = self.file.read( N )
		if len( s ) < N:
			return None
		return struct.pack( "i", s )[0]

	def write_dword( self, dword ):
		self.file.write( struct.pack( "i", int( dword )))
		
	def read_header( self ):
		pos = self.file.tell()
		len = self.read_dword()
		if len:
			return ( pos, len & ! FLAGS, len & FLAGS )
		else:
			return ( 0, 0, 0 )

	def load_index( self ):
		pass

	def rebuild_index( self ):
		self.index = []
		self.freelist = []
		self.check_magic()
		while 1:
			pos, length, flags = self.read_header()
			if not pos:
				break

			if flags & FLAG_DELETED:
				self.freelist.append(( pos, length ))
			else:
				self.index.append(( pos, length ))
		
			self.file.seek( length, 1 )

	def read_at( self, pos ):
		pass

	def write_at( self, pos, data ):
		pass

	def get( self, index ):

	def put( self, index, data ):
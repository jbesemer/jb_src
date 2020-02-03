
# User class that emulates a file, for refinement purposes

class UserFile:

	def __init__( self, file = None ):

		self.SEEK_ABS = 0
		self.SEEK_REL = 1
		self.SEEK_END = 2

		self.BUFSIZE_DEFAULT = -1
		self.BUFSIZE_UNBUFFERED = 0
		self.BUFSIZE_LINEBUFFERED = 1

		self.File = file

		if self.File != None:
			self.closed = file.closed
			self.mode = file.mode
			self.name = file.name
			self.softspace = file.softspace
		else:
			self.closed = 1
			self.mode = 0
			self.name = "UserFile('')"
			self.softspace = 0


	def open( self, filename, mode="r", bufsize = -1 ):
		self.File = open( filename, mode, bufsize )
		return self.File

	def close( self ):
		return self.File.close()

	def flush( self ):
		return self.File.flush()

	def isatty( self ):
		return self.File.isatty()

	def fileno( self ):
		return self.File.fileno()

	def read( self, size = -1 ):
		return self.File.read( size )

	def readline( self, size = -1 ):
		return self.File.readline( size )

	def readlines( self, sizehint = -1 ):
		return self.File.readlines( sizehint )

	def seek( self, offset, whence=0 ):
		return self.File.seek( offset, whence )

	def tell( self ):
		return self.File.tell()

	def truncate( self, size = 0 ):
		return self.File.truncate( size )

	def write( self, str ):
#		print "UserFile.write(,", str, ")"
		return self.File.write( str )

	def writelines( self, list ):
		return self.File.writelines( list )


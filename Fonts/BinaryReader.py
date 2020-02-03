
import os, sys
import struct
import StringIO


# #### Byte-Stream Binary I/O #############################

class ByteReader( StringIO.StringIO ):
	""" sequential and random access I/O on a string of bytes """
	
	BIGENDIAN = ">" # proper struct encoding for PTV

	def __init__( self, data ):
		StringIO.StringIO.__init__( self, data )

	def Get(self, count=1):
		data = self.read( count )
		if len( data ) < count:
			raise "premature EOF"
		return data
		
	def AsString( self ): return self.getvalue()
	def AsBytes( self ): return [ ord( ch ) for ch in self.AsString()]
		
	def Tell( self ): return self.tell()
	def Seek( self, pos=0 ): self.seek( pos )
	def Rewind( self ):	return self.Seek()

	def GetI16( self ):	return struct.unpack( self.BIGENDIAN + "h", self.Get( 2 ))[ 0 ]
	def GetI32( self ):	return struct.unpack( self.BIGENDIAN + "i", self.Get( 4 ))[ 0 ]
	def GetI8( self ):	return ord( self.Get( 1 ))
	

class ByteReaderFromFile( ByteReader ):
	""" ByteReader initialized by file's contents """
	
	def __init__( self, filename ):		
		ByteReader.__init__( self, file( filename, "rb" ).read())

class ByteWriter( ByteReader ):
	""" sequential and random access I/O on a string of bytes """
	
	def PutI16( self, n ):	self.write( struct.pack( self.ENDIAN + "h", n ))
	def PutI32( self, n ):	self.write( struct.pack( self.ENDIAN + "i", n ))
	def PutByte( self, byte ):	self.write( byte )
	def PutBytes( self, bytes ): 
		for byte in bytes:
			self.PutByte( byte )
		return self 			#often the last op before passing result elsewhere
		
		
#   Bit-Stream Binary I/O ################################
#
#	The underlying implementation now uses Long integers (arbitrary precision), rather
#	than strings or lists of ints.
#
#	The base class implements read-only bit stream in Little-Endian format.
#	There are sub-classes for writing and for Big-Endian format.

class SeekOffset( object ):
	""" implement a fileio-like seek offset, and related ops """
	# inheriting from this class, allows the subclass to reference self.pos directly.
	
	def __init__( self, pos=0 ):
		self.pos = pos
		self.stack = []

	def Rewind( self ):				self.Seek()
	def Seek( self, pos=0 ):		self.pos = pos
	def Tell( self ): 					return self.pos

	def SavePos( self, pos=-1 ):
		""" save current position, and possibly change it """
		self.stack.append( self.pos )
		if pos >= 0: 
			self.pos = pos
			
	def RestorePos( self ): 
		""" restore current position from previous Push, and return it """
		self.pos = self.stack.pop()
		return self.pos

	def AdvancePos( self, width=1, pos=-1 ):
		"""	optionally move to a pos, and then advance over a width, 
			returning starting pos 
		"""
		if pos >= 0:
			self.pos = pos
		pos = self.pos
		self.pos += width
		
		return pos			# previous value is used in most cases
		
class NibbleAccess( object ):
	""" optional add-in for 4-bit nibbles """
	
	def GetNibble( self ):
		return int( self.GetBits( 4 ))

	DEFAULT_MAP = " 123456789ABCDEF" 
	
	def GetNibbleAsStr( self, map=DEFAULT_MAP ):
		return map[ self.GetNibble()]

	def GetNibblesAsBytes( self, length ):
		return [
			self.GetNibble()
				for i in xrange( length )]

	def GetNibblesAsStr( self, length ):
		return "".join([
				self.GetNibbleAsStr()
					for i in xrange( length )])

def ConvertToDataWidth( data, width=-1 ):
	""" convert a variety of incoming value types to an explicit long data and a width """
	# an explicit width is required for some data types (where referenced below)

	if type( data ) == type(""):
		data = 0L
		width = 8 * len( data )
		for ch in data:
			data <<= 8
			data |= ord( ch ) & 0xFFL
		
	elif type( data ) == long:
		assert width >= 0					# width is mandatory for longs

	elif isinstance( data, BitReaderBase ):
		return data.data, data.width
		
	elif type( data ) in [ type([]), type(())]:
		result = 0L
		width = 0
		for item in data:
			d2, w2 = ConvertToDataWidth( item )
			result <<= w2
			result |= d2
			width += w2
		return result, width
	
	elif type( data ) == int:
		if True:
			return data & 0xFFL, 8
		else:
			return data & 0xFFFFFFFFL, 32
		
	else:
		raise "unsupported Bit data type:", type( data )
		
	return data, width



class BitReaderArithmetic( object ):

	""" optional, reader arithmetic mix-in class """
	# Yields a new, read-only object with the results, the type of which matches the left argument.
	# Ops are read-only and do not change either arg.
	
	# custom ops
	
	def __add__( self, other ):
		""" add for these ops means 'append bits' -- extend the value with extra, incoming bits """
		data, width = ConvertToDataWidth( other )
		result = self.__class__( self )
		result.AppendBits( data, width )
		return result

	def __cmp__( self, other ):		
		data, width = ConvertToDataWidth( other )
		return cmp( self.data, data )	# ignoring width seems right
		
	# intuitive functionality
	
	def __and__( self, other ):
		data, width = ConvertToDataWidth( other )
		result = self.__class__( self )
		result.data &= other.data
		result.width = min( self.width, width )
		return result
		
	def __or__( self, other ):
		data, width = ConvertToDataWidth( other )
		result = self.__class__( self )
		result.data |= other.data
		result.width = max( self.width, width )
		return result

	def __xor__( self, other ):
		data, width = ConvertToDataWidth( other )
		result = self.__class__( self )
		result.data ^= other.data
		result.width = max( self.width, width )
		return result

	def __lshift__( self, count ):
		result = self.__class__( self )
		result.data <<= count
		result.width += count
		return result
		
	def __rshift__( self, count ):
		assert self.width >= count
		result = self.__class__( self )
		result.width -= count
		result.data >>= count 
		return result
		
		


class BitWriterArithmetic( object ):
	""" optional, writer arithmetic mix-in class """
	# Modify self, per op and right arg
	
	# custom ops

	def __iadd__( self, other ):
		""" append more bits to self """
		data, width = ConvertToDataWidth( other )
		self.AppendBits( data, width )
		return self

	# intuitive ops
	
	def __iand__( self, other ):
		data, width = ConvertToDataWidth( other )
		self.width = min( self.width, width )
		self.data &= data
		return self

	def __ior__( self, other ):
		data, width = ConvertToDataWidth( other )
		result.width = max( self.width, width )
		self.data |= other.data
		return self

	def __ixor__( self, other ):
		data, width = ConvertToDataWidth( other )
		result.width = max( self.width, width )
		self.data ^= other.data
		return self

	# dunno if these should change length or not...
	
	def __ilshift__( self, count ):
		self.data <<= count 
		result.width += count
		return self

	def __irshift__( self, count ):
		self.data >>= count 
		result.width -= count
		return self


		
class BitReaderBase( SeekOffset, BitReaderArithmetic, NibbleAccess  ):
	""" An abstract class with all fundamental behavior for read-only Bit Streams """
	# bits are encoded as a single long integer; interpretation of bit positions are up to sub-class

	def __init__( self, data="", width=0 ):
		BitReaderArithmetic.__init__( self )
		NibbleAccess.__init__( self )
		SeekOffset.__init__( self )
		
		self.data = 0L
		self.width = 0
		
		# append data and ancestors must not change .pos else SeekOffset will have to be rewound after.
		self.AppendData( data, width )
		
		# an explicit len, overrides any implicit in the data
		if width:
			self.width = width

	def AppendData( self, data, width=-1 ):
		""" append bits to self """
		data, width = ConvertToDataWidth( data, width )
		self.AppendBits( data, width )
		
	# basic properties
	
	def __len__( self ): 			
		""" number of bits """
		return self.width
		
	def __str__( self ):
		""" string rep for debugging """
		return ( "%s( @%d /%d: 0x%x )" % ( self.__class__.__name__, self.pos, self.width, self.data )
#				+	"  # " + " ".join(([ "%02x" % byte for byte in self.AsBytes()]))
				)

	# conversions

	def __int__( self ): 		return int( self.data )	# may throw exception if result > 32-bits
	def __long__( self ):		return long( self.data )
		
	# read-only access to bits
	
	def __getslice__( self, lo, hi ):
		""" return a new instance of this class, initialized to bits [lo:hi] from self """
		# Convention says __getslice__ return type should be same as self 
		#	(though we might argue for it being a long or something else).

		# Slices that overlap (but do not go beyond) the last bit in the stream, return the remaining bits.
		# This method returns them right-justified in the "width," which is correct for Little-Endian,
		# but which has to be left-shifted for the Big-Endian case.
		
		# TODO: hi==maxint => self.width

#		print "    BitReaderBase.__getslice__( %d, %d ):" % ( lo, hi ), self

		width = hi - lo
		if 0 <= lo <= hi <= self.width + width:
			pass
		else:
			print "    BitReaderBase.__getslice__( %d, %d ): assertion error:" % ( lo, hi ), self
		assert 0 <= lo <= hi <= self.width + width		# off by one???

		Lo, Hi = self.GetLoHi( lo, hi )
		data = ( self.data >> Lo ) & rmask( width )

#		print "    BitReaderBase.__getslice__( %d, %d ) -> ( %d %d / %d ):" % ( lo, hi, Lo, Hi, width ), hex( data )
	
		return self.__class__( data, width )

	def GetBits( self, width=1 ):
		""" get bits AND advance the pointer """
		pos = self.AdvancePos( width )
		return self[ pos : self.pos ]

	GetBit = GetBits	# backwards-compatible synonym for when these were different

	def GetBitsAsInt( self, width=1 ):		return int( self.GetBits( width ) & 0xFFFFFFFFL )
	def GetBitsAsByte( self, width=1 ):		return int( self.GetBits( width ) & 0xFFL )

	def GetBitsAsBytes( self, width ):
		""" return width bits at the current position, parceled into bytes """

		return ([ self.GetBitsAsByte( 8 )
						for i in xrange( 0, width, 8 )]
				or [0])

	def AsBytes( self ):
		""" return entire bitstream as a sequence of bytes """
		self.SavePos( 0 )
		bytes = self.GetBitsAsBytes( self.width )
		self.RestorePos()
		return bytes

	FG_CHAR = "#"
	BG_CHAR = " "
	
	def GetBitsAsStr( self, length, map=[ BG_CHAR, FG_CHAR ]):
		""" return a sequence converted to text """

		return "".join([ 
			map[ self.GetBit()] 
				for i in xrange( length )])


# the corresponding writer class.....

class BitWriterBase( BitReaderBase, BitWriterArithmetic ):
	
	""" sequential and random access I/O on a string of bits """
	# bits are encoded as a single long integer; interpretation of bit positions are up to sub-class

	def __setslice__( self, lo, hi, bits ):
		""" replace self[lo:hi] with bits """
		
		assert 0 <= lo <= hi < self.width + 8

		# if bits are another BitReader or Writer, then we can actually replace the range 
		# with a different-sized number of bits; Otherwise our only choice is to overwrite 
		# the bits implied by the slice
		# But this is a FUTURE feature, and for now slices only match the intended bits.
		
		data, width = ConvertToDataWidth( bits )
		
		lo, hi = self.GetLoHi( lo, hi )
		mask = mmask( lo, hi )
		print "SetSlice:", lo, hi, self.width, hex( self.data ), hex( bits ), hex( mask )
		self.data = ( self.data & ~mask ) | (( bits << lo ) & mask )
		
		return self
		
	def AdvancePos( self, width=1, pos=-1 ):
		""" writers have to widen themselves when writing past the end """
		pos = BitReaderBase.AdvancePos( self, width, pos )
		if self.pos > self.width:
			self.Widen( self.pos - self.width )
	
		return pos # previous position

	def PutBit( self, bit=1, pos=-1 ):
		if True:	# this is probably faster than PutBits( bit )
			pos = self.AdvancePos( pos=pos )
			if bit:	self.data |=  self.Bit( pos )
			else:	self.data &= ~self.Bit( pos )
		else:
			return PutBits( bit )

	def PutBits( self, bits, width=1, pos=-1 ):
		pos = self.AdvancePos( width, pos )
		self[ pos : self.pos ] = bits

	def InsertBits( self, bits=0L, width=1, pos=-1 ):
		"""	
			Insert width bits at the current position, 
			advancing the position to just past the insertion point 
		"""
		# TODO: reconcile with corrected set bits
		
		pos = self.AdvancePos( width, pos )
		
#		print "InsertBits( %d @%d ): " % (width, pos), hex(bits)
		left = self[ 0 : pos ]
		right = self[ pos :  self.width ]
			
#		print "InsertBits.left: ", left
#		print "InsertBits.right: ", right
			
		left.AppendBits( bits, width )
#		print "InsertBits.appended: ", left
		left += right
#		print "InsertBits.added: ", left
		
		self.data = left.data
		self.width = left.width
		

	def DeleteBits( self, width ):
		raise "Unimplemented"
		
	if 0:
		def __str__( self ): return "%d/%d: 0x%x" % ( self.pos, self.width, self.data )


# ######## Little-Endian versions ###########################


class BitReaderLittleEndian( BitReaderBase ):
	""" sequential and random read-only access to a string of bits, 
		using LITTLE-Endian Indicies 
	"""

	def GetLoHi( self, lo, hi ): return lo, hi	# lo,hi don't change

	def AppendBits( self, bits, width= 1 ):
		""" Append Bits on the LEFT, LITTLE-Endian style """
		# must not change self.pos
		if width > 0:
			self.data |= long( bits ) << self.width
			self.width += width

class BitWriterLittleEndian( BitWriterBase ):
	""" sequential and random read-write access to a string of bits, 
		using LITTLE-Endian Indicies 
	"""

	def Widen( self, width=1 ):	
		self.width = max( self.pos, self.width )

	def Bit( self, pos ):				return 1L << pos


# ######## Big-Endian versions ###########################

class BitReaderBigEndian( BitReaderBase ):
	""" sequential and random read-only access to a string of bits, 
		using BIG-Endian Indicies 
	"""
	def GetLoHi( self, lo, hi ): 		return max( 0, self.width - hi ), self.width - lo

	def AppendBits( self, bits, width= 1 ):
		""" Append Bits on the RIGHT, BIG-Endian style """
		# must not change self.pos	# TODO: who relies?
		if width > 0:
			self.data <<= width
			self.data |= bits
			self.width += width
		
	def __getslice__( self, lo, hi ):
		""" return a new instance of this class, initialized to bits [lo:hi] from self """

#		print "  BigEndian.__getslice__( %d, %d ):" % (lo, hi ), self
		result = BitReaderBase.__getslice__( self, lo, hi )
#		print "  BigEndian.__getslice__: -> ", result

		# Slices that overlap (but do not go beyond) the last bit in the stream, return the remaining bits.
		# BitReaderBase returns them right-justified in the "width," which is correct for Little-Endian,
		# but we have to left-shift them for the Big-Endian case.
		
		shift = hi - self.width
		if shift > 0:
#			print "  BigEndian.__getslice__: Shifting by %d:" % shift, result
			result.AppendBits( 0, shift )
#			print "  BigEndian.__getslice__: Shifting ->:", result
			result.width = hi - lo
			result.data &= rmask( result.width )
			
#		print
		return result


class BitWriterBigEndian( BitReaderBigEndian, BitWriterBase ):
	""" sequential and random read-only access to a string of bits, 
		using BIG-Endian Indicies 
	"""	
	def Bit( self, pos ):					return 1L << self.width - pos

	def Widen( self, width=1 ):
		self.width = max( self.pos, self.width )
		self.data <<= width

# Utils ############################################
# masks for left and right parts of a long split at bitnum (0 => LSB),
# and mask for slice of bits:

def mmask( lo, hi ):		return rmask( hi ) & ~rmask( lo )
def rmask( bitnum ):			return ( 1L << bitnum ) - 1
def lmask( bitnum ):			return ~rmask( bitnum )

# legacy external names

BitReader = BitReaderBigEndian
BitWriter = BitWriterBigEndian

# unit testing ###############################################

if __name__ == "__main__":

	def test1( bits, nbits, init=[]):
		print "\nTest1(", hex( bits ), ", ", nbits, ")"
		bw = BitWriter( init )
		print "Before:", bw 
		bw.InsertBits( bits, nbits )
		return bw

	def test3( bits, nbits, init=[]):
		print "\nTest3(", hex( bits ), ", ", nbits, ")"
		bw = BitWriter( init )
		print "Before:", bw 
		bw.PutBits( bits, nbits )
		return bw

	def test2( bits, pos, init ):
		print "\nTest2(", hex( bits ), ", ", pos, ")"
		bw = BitWriter( init )
		print "Before:", bw
		bw.Seek( pos )
		bw.InsertBits( bits, nbits )
		return bw

	def test4( bits, nbits, pos = 0, init=[]):
		print "\nTest4(", hex( bits ), ", ", nbits, ",", pos, ")"
		bw = BitWriter( init )
		bw.Seek( pos )
		print "Before:", bw 
		bw.InsertBits( bits, nbits )
		return bw
		
	def Verify1( actual, expected ):
		if actual != expected:
			print "\t!!!!!!!!!!!!! EXPECTED:", expected, "!!!!!!!!!!!!!!!!!!"
		else:
			print "\t++++++ OK ++++++"
		print

	def Verify( actual, expected ):
		print "Actual:", actual
		print "Expected:", expected
		Verify1(  actual.data, expected )

	initial = "\x70\xFF\x05\x44" 
	bits = 0x987659L
	nbits = 24

	if 1:
		Verify( test1( bits, nbits ), 0x987659L )
	if 1:
		Verify( test3( 0xFFF, 4, [ 0, 0, 0 ]), 0xf00000L )
		Verify( test3( 0xFFF, 12, [ 0, 0, 0 ]), 0xfff000L )
		Verify( test3( bits, 24, [ 0, 0, 0 ]), 0x987659L )
		Verify( test3( bits, 24, [ 0xFF, 0xFF, 0xFF ]), 0x987659L )

	if 1:
		data = "\x10\x0f\xfa\xfb"
		Verify( test4( 0, 1, 4, data), 0x200ffafbL )
		Verify( test4( 1, 1, 7, data), 0x220ffafbL )
		Verify( test4( 1, 1, 11, data), 0x202ffafbL )
		Verify( test4( 1, 1, 31, data), 0x201ff5f7L )
		Verify( test4( 5, 4, 8, data), 0x1050ffafbL )
		Verify( test4( 5, 4, 4, data), 0x1500ffafbL )

	if 1:
		Verify( test2( bits, 12, initial ), 0x70f987659f0544L )
		Verify( test2( bits, 16, initial ), 0x70ff9876590544L )
		
	if 1:
		Verify1( test2( bits, 16, initial ).AsBytes(), [ 0x70, 0xff, 0x98, 0x76, 0x59,  0x5, 0x44 ])
		Verify1( test4( 1, 1, 7, data).AsBytes(), [ 0x11,  0x7, 0xfd, 0x7d, 0x80 ])
	
	
#EOF #######################################################


import os, sys
import struct
import StringIO

from BinaryReader import *

class PTVGlyph1( object ):
	""" read, represent and render a glyph several ways """
	
	def __init__( self, font, data, offset=0 ):
		self.font = font
		self.offset = offset
		data.seek( self.offset )
	
		self.code = data.GetI16()
		self.yoff = data.GetI16()
		self.width = data.GetI16()
		self.height = data.GetI16()
		self.xoff = data.GetI16()
		self.advance = data.GetI16()

		self.length = self.CalcNumBytes()
		self.bits = BitReader( data.read( self.length ))
		
	def GetBitDepth( self ): return 1
		
	def CalcNumBytes( self ):
		return int(( self.width * self.height ) / 8 ) + 1

	def GetWidth( self ):
		return max( self.width, self.advance )

	def GetOverallWidth( self ):
		if self.font.SHOW_ADVANCE_AS_WIDTH:
			return self.GetWidth()
		else:
			return self.width

	def GetArea( self ):
		return self.height * self.width
				
	def GetLeftMargin( self ):
		""" calculate the number of empty columns on the left side of the glyph """
		margin = self.GetWidth()
		
		if self.GetArea():
			for row in self.RowsAsList():
				margin = min( margin, self.CalcMargin( row ))
				
		return margin

	def GetRightMargin( self ):
		""" calculate the number of empty columns on the right side of the glyph """
		margin = self.GetWidth()

		if self.GetArea():
			for row in self.RowsAsList():
				margin = min( margin, self.CalcMargin( reversed( row ))

		return margin

	def CalcMargin( self, row ):
		""" calculate the number of leading blanks in row """
		m = 0		# TODO: do the calc in binary
		for char in row:
			if char != BitReaderBase.BG_CHAR:
				break
			m += 1
		return m
		
	def EnsureMinimumRightMargin( self, margin=1 ):
		""" increase advance to ensure glyph has a minimum amount of space on the right """
		# This operation is easy.  The corresponding Left op is much harder.

		rightMargin = self.GetRightMargin()
		if rightMargin < margin and ( self.advance - self.width ) < margin:
			self.advance = margin + self.width - rightMargin

	def InsertLeftMargin( self, margin=1 ):
		""" insert bits on the left of each row, thereby increasing the margin """
		
		bits = BitWriter( self.bits )
		bits.Rewind()
		
		for y in xrange( self.height ):
			bits.Seek( y * self.width )
			bits.InsertBits( width=margin )
		self.bits = bits
		self.width += margin
		
	def ConvertXOffsetToLeftMargin( self ):
		assert self.xoff >= 0
		
		if self.xoff > 0:
				self.InsertLeftMargin( self.xoff )
		self.xoff = 0

	def RowsAsList( self ):
		volume = self.GetArea()
		if volume == 0:
#			print "Glyph #", self.code, "has no data"
			return [ "" ] * self.height
			
		self.bits.Rewind()
		return [ self.bits.GetBitsAsStr( self.width )
				for pos in xrange( 0, volume, self.width )]
		
	def __str__( self ):
		return (
				( "%04x " % self.offset )
			+	( "%d %02x %s " 
					% ( self.code, self.code, repr( chr( self.code ))))
			+ ( "h:%2d " % self.height )
			+ ( "w:%2d " %  self.width )
			+ ( "a:%2d " % self.advance )
			+ ( "x:%2d " % self.xoff )
			+ ( "y:%2d " % self.yoff )
			+ ( "l:%2d  " % self.CalcNumBytes())
			+ "  data: "
			+ str( self.bits ))

	def AsBits( self ):
		self.bits.Rewind()
		blankRow = [0]
		return (
			blankRow * self.yoff
			+ [ self.bits.GetBits( self.width )
					for i in xrange( self.height )]			# - self.yoff + 1 )]
			+ blankRow * ( self.font.header.fontSize - self.height - self.yoff ))
		
	def AsBytes( self ):
		self.bits.Rewind()
		blankRow = self.blankRow()
		return (
			blankRow * self.yoff
			+ [ self.bits.GetBitsAsBytes( self.width )
					for i in xrange( self.height )]			# - self.yoff + 1 )]
			+ blankRow * ( self.font.header.fontSize - self.height - self.yoff ))

	def blankRow( self ):
		return [[0] * min( 1, ( self.GetWidth() - 1 ) / 8 + 1 )]

	def AsPTVGlyph1( self, threshold=1 ): return self
		
PTVGlyph = PTVGlyph1

class PTVGlyph4( PTVGlyph1 ):

	def GetBitDepth( self ): return 4

	def CalcNumBytes( self ):
		return int(( self.width * self.height ) / 2 ) + 1
	
	def RowsAsList( self ):
		volume = self.GetArea()
		if volume == 0:
			print "Glyph #", self.code, "has no data"
			return [ "" ] * self.height
			
		self.bits.Rewind()
		return [ self.bits.GetNibblesAsStr( self.width )
				for pos in xrange( 0, volume, self.width )]


	def AsPTVGlyph1( self, threshold=8 ):
		""" convert an AA font to a monochrome one, using the indicated threshold for black vs. white """
		bits = BitWriter()
		data = ByteWriter()
		volume = self.GetArea()

		# write out glyph header
		data.PutI16( self.code )
		data.PutI16( self.yoff  )
		data.PutI16( self.width )
		data.PutI16( self.height )
		data.PutI16( self.xoff )
		data.PutI16( self.advance )
			
		# convert 4-bit nibbles to 1-bit bits
		if volume > 0:
			for rowindex in xrange( 0, volume, self.width ):
				nibbles = self.bits.GetNibblesAsBytes( self.width )
				for nibble in nibbles:
					bits.PutBit( int( nibble >= threshold ))

		return PTVGlyph1( self.font, data.PutBytes( bits.AsBytes()))



class PTVFontFile( object ):
	""" represent a font file (as we know it) including all glyphs """
	
	BAD_OFFSET = -1	# these offsets have no corresponding glyph

	def __init__( self, filename=None ):
		self.filename = filename
		self.SHOW_ADVANCE_AS_WIDTH = False
		self.MONOCHROME_CONVERSION_THRESHOLD = 0
		self.ENSURE_MINIMUM_RIGHT_MARGIN = 0
		self.SHOW_ADVANCE_AS_WIDTH = False
		self.SHOW_XOFFSET_AS_WIDTH = False

		if filename:
			self.Load( filename )

	def Load( self, filename ):
		""" load data from a ptv font file """
		
		self.filename = filename
		data = self.data = ByteReaderFromFile( filename )
		self.header = PTVFontFileHeader( self, data )

		self.offsets = {}
		for i in xrange( self.header.count ):
			addr = data.GetI32()
			if addr != self.BAD_OFFSET:
				self.offsets[ i ] = addr

		self.GlyphClass = self.header.GetGlyphClass()

		self.glyph = {}
		for key in self.offsets.keys():
			self.glyph[ key ] = self.GlyphClass( self, data, self.offsets[ key ])

	def GetFontSize( self ): return self.header.fontSize
	def GetBaseline( self ): return self.header.baseline
	def GetBitDepth( self ): return self.header.GetBitDepth()
	def SetBitDepth( self, n ): return self.header.SetBitDepth( n )

	def ConvertToMonochrome( self, threshold=8 ):
		if self.GetBitDepth() > 1:		
			for key, value in self.glyph.items():
				self.glyph[ key ] = value.AsPTVGlyph1( threshold )
				
			self.SetBitDepth( 1 )
			
	def ConvertXOffsetToLeftMargin( self ):
		for glyph in self.glyph.values():
			glyph.ConvertXOffsetToLeftMargin()
		
	def EnsureMinimumRightMargin( self, margin=1 ):
		for glyph in self.glyph.values():
			glyph.EnsureMinimumRightMargin( margin )

	def __str__( self ):
		return  self.filename + ": " + str( self.header )

 
class PTVFontFileHeader( object ):
	""" font file header """
	
	# map reserved1 codes to appropriate glyph type:	
	NewGlyphCodeMap = {
		4:	PTVGlyph4,		# 4-bit AA fonts
		1:	PTVGlyph1,		# 1-bit, monochrome
		0:	PTVGlyph1,		# 1-bit, monochrome
	}

	NewGlyphCodeNames = {
		4:	"4-bit Anti-Aliased",
		1:	"1-bit mono (converted from 4-Bit AA)",
		0:	"1-bit, monochrome",
	}

	def __init__( self, parent, data ):
		self.parent = parent
		data.Rewind()
		self.magic = data.read( 4 )
		self.version = data.GetI32()
		self.bitDepth = data.GetI32( )	# 0=>1 bit; 4=>4bit/AA
		self.count = data.GetI16()
		self.reserved2 = data.GetI16()	# widthOf( ' ' )??
		self.fontSize = data.GetI16()
		self.baseline = data.GetI16()

	def GetGlyphClass( self ):
		try:
			return self.NewGlyphCodeMap[ self.bitDepth ]
		except KeyError:
			raise "Don't know how to handle header.reserved1==%d " 	\
				% self.bitDepth
		
	def GetFontClass( self ):
		try:
			return self.NewGlyphCodeNames[ self.bitDepth ]
		except KeyError:
			return "Unknown (%d)" % self.bitDepth

	def SetBitDepth( self, n ): self.bitDepth = n

	def GetBitDepth( self ):
		try:
			return {
				0: 1,
				1: 1,
				4: 4,
			}[ self.bitDepth ]
		except KeyError:
			raise "Unknown bit depth: %d" % self.bitDepth
			
	def __str__( self ):
		return ( self.magic 
			+ ( " %s Font" % self.GetFontClass())
			+ ( " ver: %d" % self.version )
			+ ( " max: %3d" % self.count )
			+ ( " size: %2d" % self.fontSize )
			+ ( " base: %2d" % self.baseline )
			+ ( " res: %d" % self.reserved2 ))


#######################################
# misc utilities

def NumBytes( width ):
	# return width // 8 + int( 0 != ( width % 8 ))	# jb's sol'n
	return 1 + ( width - 1 ) // 8		# Joe's better one


def hexify(l):
	try:
		return "%02x" % l
	except TypeError:
		return ", ".join([ hexify(item) for item in l ])

def AsHex( str ):
	return " ".join([ "%02x" % ord( ch ) for ch in str ])


#######################################


if __name__ == "__main__":
	for name in sys.argv[1:]:
		ff = PTVFontFile( name )
		print ff.prGlyphs()
		print
		
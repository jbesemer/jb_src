
import PTVFontFile

#######################################

FG_CHAR = "#"
BG_CHAR = " "

MONOCHROME_CONVERSION_THRESHOLD = 0
ENSURE_MINIMUM_RIGHT_MARGIN = 0
SHOW_ADVANCE_AS_WIDTH = False
SHOW_XOFFSET_AS_WIDTH = False
CONVERT_XOFFSET_TO_LEFT_MARGIN = False

class PTVFontDumper( PTVFontFile.PTVFontFile ):

	def __init__( self, filename=None ):
		PTVFontFile.PTVFontFile.__init__( self, filename )

		if MONOCHROME_CONVERSION_THRESHOLD:
			self.ConvertToMonochrome( MONOCHROME_CONVERSION_THRESHOLD )

		if ENSURE_MINIMUM_RIGHT_MARGIN > 0:
			self.EnsureMinimumRightMargin( ENSURE_MINIMUM_RIGHT_MARGIN )

		if CONVERT_XOFFSET_TO_LEFT_MARGIN:
			self.ConvertXOffsetToLeftMargin()
			
		self.SHOW_ADVANCE_AS_WIDTH = SHOW_ADVANCE_AS_WIDTH
		self.SHOW_XOFFSET_AS_WIDTH = SHOW_XOFFSET_AS_WIDTH
		

		
	def DumpGlyphs( self ):
		offset = 0
		for key in sorted( self.glyph.keys()):
			g = PTVGlyphDumper( self.glyph[ key ])
			g.offset = offset
			offset += g.length + 3
			g.Dump()


class PTVGlyphDumper( PTVFontFile.PTVGlyph ):
	def __init__( self, glyph ):
		
		# inherit all of glyph's existing properties (which must NOT override our own)
		self.__dict__.update( glyph.__dict__ )
		self.glyph = glyph

	#  but methods are not inherited, so we have to vector to them.
	def GetBitDepth( self ):	return self.glyph.GetBitDepth()
	def CalcNumBytes( self ):	return self.glyph.CalcNumBytes()
	def RowsAsList( self ):	return self.glyph.RowsAsList()
	def AsPTVGlyph1( self ):	return self.glyph.AsPTVGlyph1()

	def Dump( self ):
		print self.GetHeading()
		print self
		print "\t" + "\n\t".join( self.RowListWithBoxAndNums())

	def RowListWithBox( self ):
		width = max( self.advance, self.width)
		
		cap = [ " " * self.LEFT_INDENT + "+" + "-" * self.GetOverallWidth() + "+" ]
		blank = [ "|" + BG_CHAR * self.GetOverallWidth() + "|" ]
		rows = self.RowsAsList()
		
		return ( cap
			+ blank * self.yoff
			+ [ "|" + row + ( BG_CHAR * ( self.width  - len( row ))) 
				+ ( BG_CHAR * ( self.GetOverallWidth() - self.width ))
				+ "|" 
						for row in rows ]
			+ blank * ( self.font.GetFontSize() - self.yoff - self.height ) 
			# TODO: use .Yfill
			+ cap )

	LEFT_INDENT = 7	# number of extra chars pre-pended to each row, in the for loop, below...
	
	def RowListWithBoxAndNums( self ):
		box = self.RowListWithBox()
		rows = box[ 1 : -1 ]
		
		a = Naturals()		# offset from top into glyph on output device
		b = Naturals( -self.yoff - 1 )	# offset from first row of actual data
		newRows = []
		bitWidth = self.width * self.GetBitDepth()
		
		self.bits.Rewind()
		for row in rows:
			B = b.next()
			newRow = " %2d %s " % ( a.next(), BlankIfNegative( B )) + row
			if 0 < bitWidth and 0 <= B < self.height:
				bytes = self.bits.GetBitsAsBytes( bitWidth )
				newRow += "  = " + " ".join([ "%02x" % byte for byte in bytes ])
			newRows.append( newRow )

		newRows.insert( 
			self.font.GetBaseline(), 
			" " * self.LEFT_INDENT 
				+ "-" * ( self.advance + 1 )
				+ "+" 
				+  "-" * ( self.width - self.advance ))
		
		box[ 1 : -1 ] = newRows
		return box
		
	def GetHeading( self ): 
		return "\nAddr --Code---  h  w  a  x  y ow lm rm Len Data..."
		
	def __str__( self ):
		return (
				( "%04x " % self.offset )
			+	( "%d %02x %s " 
					% ( self.code, self.code, repr( chr( self.code ))))
			+ ( "%2d " % self.height )
			+ ( "%2d " %  self.width )
			+ ( "%2d " % self.advance )
			+ ( "%2d " % self.xoff )
			+ ( "%2d " % self.yoff )
			+ ( "%2d " % self.GetOverallWidth())
			+ ( "%2d " % self.GetLeftMargin())
			+ ( "%2d " % self.GetRightMargin())
			+ ( "%4d  " % self.CalcNumBytes())
			+ " "
			+ str( self.bits ))

class Naturals( object ):
	""" generate a stream of natural numbers """
	def __init__( self, offset=-1 ):	self.num = offset
	def __iter__( self ): 	return self
	def next( self ):
		self.num += 1
		return self.num

def BlankIfNegative( B ):
	if B < 0:	return "  "
	else:		return "%2d" % B

if __name__ == "__main__":
	import sys, re
	
	def Match( pattern, name ):
		global match
		match = re.match( pattern, name )
		return match

	for name in sys.argv[1:]:
		if Match( "-xa", name ):
			SHOW_ADVANCE_AS_WIDTH = True
			continue

		elif Match( "-aw", name ):
			SHOW_XOFFSET_AS_WIDTH = True
			continue

		elif Match( "-m=(\d+)", name ):
			MONOCHROME_CONVERSION_THRESHOLD = int( match.group(1))
			continue

		elif Match( "-rm=(\d+)", name ):
			ENSURE_MINIMUM_RIGHT_MARGIN = int( match.group(1))
			continue

		elif Match( "-lm=(\d+)", name ):
			ENSURE_MINIMUM_LEFT_MARGIN = int( match.group(1))
			continue

		elif Match( "-xm", name ):
			CONVERT_XOFFSET_TO_LEFT_MARGIN = True
			continue

		elif name[0] == '-':
			print >>sys.stderr, "Unrecognizable option:", name
			exit(1)

		try:
			font = PTVFontDumper( name )	
			print font
		
			if 0:
				g = PTVGlyphDumper( font.glyph[ 33 ])
#				g.ConvertXOffsetToLeftMargin()
				g.Dump()
			else:
				font.DumpGlyphs()
				print
		except:
			import TraceBackVars
			TraceBackVars.TraceBackVars()
			sys.exit(1)

	sys.exit(0)

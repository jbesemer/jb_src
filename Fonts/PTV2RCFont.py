
import os, os.path, time
import string
import sys

import PTVFontFile
PTVFont = PTVFontFile.PTVFontFile

VERSION = "1.1"

# pixel level to use to discriminate black (>=this) from white 
MONOCHROME_CONVERSION_THRESHOLD = 8

# widen fonts, if necessary, to ensure this many columns of zeros on the right
MINIMUM_RIGHT_MARGIN = 1			# 0 => no conversion

SHOW_ADVANCE_AS_WIDTH = True

class PTV2RCFontConverter( PTVFontFile.PTVFontFile ):
	def __init__( self, filename = None ):
		
		PTVFontFile.PTVFontFile.__init__( self, filename )
		
		if self.GetBitDepth() != 1:
			print >>sys.stdout, "Converting AA font to monochrome"
			self.ConvertToMonochrome( MONOCHROME_CONVERSION_THRESHOLD )
			
		if MINIMUM_RIGHT_MARGIN:
			self.EnsureMinimumRightMargin( MINIMUM_RIGHT_MARGIN )
			
		self.SHOW_ADVANCE_AS_WIDTH = SHOW_ADVANCE_AS_WIDTH 
		
		self.basename, ext = os.path.splitext( filename )
		path, self.fontname = os.path.split( self.basename )
		self.newname = self.basename + ".rc"
		self.offsets = []
		self.offset = 0

		self.leading		= 1
		
		self.fontHeight		= self.header.fontSize
		self.fontAscent		= self.header.baseline
		self.fontDescent	= self.header.fontSize - self.header.baseline

		self.fontWidth		= \
		self.lastCode		= \
		self.charsp			= 0
		
		self.firstCode		= 1e99

	def recordOffset( self, offset=0 ):
		self.offsets.append( self.offset )
		self.offset += offset
	
	def SaveGlyphs( self, stream ):
		for key in sorted( self.glyph.keys()):
			g = self.glyph[ key ]
			g.rc_offset = self.header.baseline - g.yoff
			
			if self.fontWidth < g.width:
				self.fontWidth = g.width
			if self.fontHeight< g.height:
				self.fontHeight = g.height
				
			if self.firstCode > key:
				self.firstCode = key
			if self.lastCode < key:
				self.lastCode = key

			char = chr( key )
			if char not in string.printable:
				char = "??"
				
			overallWidth = g.GetOverallWidth()

			print >>stream, "/* 0x%x, %d, '%s' at %d */" % ( key, key, char, self.offset ),
			
			if g.width == 0 or g.height == 0:
				print >>stream, " %d,%d,%d," % ( g.advance, 1, 0 )
				print >>stream, "\t0,"
				nBytes = 4
			else:
				print >>stream, " %d,%d,%d," 	% ( overallWidth, g.height, g.rc_offset )
				nBytes = 3
	
				if overallWidth <= g.width:
					print >>stream, "\t/********************>>>>>> overall width <= width */"
#					print "\t>>>>>> advance <= width:", overallWidth, g.width
				elif g.advance > overallWidth + 1:
					print >>stream, "\t/********************>>>>>> advance > overall width + 1 */"

				# see if advance requires extra data bytes...  
				extra = NumBytes( overallWidth ) - NumBytes( g.width )
				if extra > 0:
					print >>stream, "\t/********************>>>>>> adding %d data bytes */" % extra

				g.bits.Rewind()
				
				for i in xrange( g.height ):
					row = g.bits.GetBitsAsBytes( g.width * g.GetBitDepth())

					# if advance requires extra data bytes, we add them in here (to each row)...
					row.extend( [0] * extra )

					print >>stream, "\t%s," % ", ".join([ "%3d" % byte for byte in row ]),
					print >>stream, "\t/* %4d:" % ( self.offset + nBytes ),
					print >>stream, " %s */" % ", ".join([ "%02x" % byte for byte in row ])
					nBytes += len( row )
			print >>stream
			self.recordOffset( nBytes )

	def SaveOffsts( self, stream ):
		print >>stream, "\n/* final offset = %4d */\n"  % self.offset
		print >>stream, "\nstatic unsigned short font_offsets_%s[] = {"  % self.fontname
		m = 0
		for offset in self.offsets:
			print >>stream, "%4d," % offset,
			m += 1
			if m % 10 == 0:
				print >>stream 
		if m % 10 != 0:
			print >>stream 
		print >>stream, "};"
	
	def SaveBoilerplate( self, stream ):
		print >>stream, """
o_font_info_desc font_info_%s = {
	"%s",  			/* font name */
	"PowerTV",  		/* Char set authority */
	LATIN,  			/* Char sets */
	LATIN_1_SUP,  		/* Additional Char set info */
	%3d,  				/* Total number of Characters */
	ISO_8859_1_LATIN,  	/* Character Encoding */
	BMP_FONT_TYPE,  	/* Font type */
	BOLD + SERIF, 		/* Rendering */
	%d,  				/* Version */
	L_TO_R_TEXT,  		/* Text Direction */
	%d, %d,  			/* Width, Height */
	%d, %d, %d, %d,		/* Ascent, Descent, linesp, charsp */
	%d 					/* Point Size */ 
};
""" 		% (	self.fontname,
					self.fontname,
					self.lastCode - self.firstCode + 1,
					self.header.version,
					self.fontWidth,
					self.fontHeight,
					self.fontAscent,
					self.fontDescent,
					self.leading,
					self.charsp,
					self.header.fontSize,
				)


		print >>stream, """
RES(o_font_bitmap_info, HelvNeueCondB24) = {
	FONT_TYPE_BITMAP_INFO, 	/* type (1 bit per pixel) */
	font_data_%s,  		/* pointer to data */
	font_offsets_%s,  	/* pointer to offsets*/
	%d,  					/* Font ascent */
	%d,  					/* Font descent */
	%d,  					/* first character */
	%d,					/* last character */
	&font_info_%s 		/* pointer to info */
};
""" 		% (	self.fontname,
					self.fontname,
					self.fontAscent,
					self.fontDescent,
					self.firstCode,
					self.lastCode,
					self.fontname,
				)


	def Save( self, filename=None ):
		if filename:
			self.newname = filename
		else:
			filename = self.newname

		stream = file( filename, "w" )
		print >>stream, """
/*-----------------------------------------------------------------------|
 | OpenTV Font Resource (RC) file: %s
 | Created on: %s
 | By PowerTV Font Tool, PTV2RCFont.py Version %s
 | From: %s, %s
 |-----------------------------------------------------------------------|
 | FONT NAME    : %s
 | FONT TYPE    : BMAP (Bitmap font, 1 bit per pixel)
 | FONT BITS    : 8 bits
 | RESOURCE NAME: %s
 |------------------------------------------------------------------------
 | FONT OPTIONS: 
 | Scaling Values: X -> 1.0, Y -> 1.0
 | Blank Pixels : Default Values
 |------------------------------------------------------------------------
 */

static unsigned char font_data_%s[] = {
""" 		% ( self.newname,
				time.asctime(),
				VERSION,
				self.filename,
				time.ctime( os.path.getmtime( self.filename )),
				self.fontname, 
				self.fontname, 
				self.fontname, 
			)

		self.SaveGlyphs( stream )
		
		print >>stream, """};"""

		self.SaveOffsts( stream )
		self.SaveBoilerplate( stream )

def NumBytes( width ):
	""" calculate the number of bytes needed to contain width bits """
	# return width // 8 + int( 0 != ( width % 8 ))	# jb's sol'n
	return 1 + ( width - 1 ) // 8		# The "DiMartino Algorithm"


if __name__ == "__main__":
	import os.path, sys
	
	try:
		for name in sys.argv[1:]:
			font = PTV2RCFontConverter( name )
			print name, "->", 
			print font.newname + ":"
			font.Save()
	except:
		import TraceBackVars
		TraceBackVars.TraceBackVars()
			
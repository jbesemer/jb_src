
# refine PTVFontFile.PTVFontFilepy to format output into HTML


import PTVFontFile

ATSIGN = "&#064;"
LILDOT = "&#183;"
BULLET = "&#149;"
SPACE = "&nbsp;"

FG_CHAR = ATSIGN
BG_CHAR = LILDOT

class PTVFontFileHtml( PTVFontFile.PTVFontFile ):
	""" report various statistics about a PTF font file in HTML """
	
	def __init__( self, filename ):
		PTVFontFile.PTVFontFile.__init__( self, filename )
		PTVFontFile.FG_CHAR = FG_CHAR 
		PTVFontFile.BG_CHAR = BG_CHAR 
	
	def ReportHeading( self ):
		def b( item ):
			return ( "<font size=+2>"
					+ str( item )
					+ "<font size=-2>")
		print "<h1>PTV Font Decoding</h1>"
		print "<h2>Font Header</h2>"
		print "<table rules=all frame=box cellpadding=5>"
		print TableHead([
				"Filename",
				"Version",
				"Num Glyphs",
				"Font Size",
				"Font Height",
				"Unk1",
				"Unk2",
				])
		print TableRow([
					b( self.filename ),
					b( self.header.magic ) + "-" +  b( self.header.version ),
					b( self.header.count ),
					b( self.header.fontSize ),
					b( self.header.baseline ),
					b( self.header.reserved1 ),
					b( self.header.reserved2 ),
					],
				rowattr={ "align": "center" })
		print "</table>"
		
	def ReportTables( self ):
		print "<h2>Font Properties</h2>"
		print "<table border=box rules=all>"
		print PTVGlyphHtml.AsTableHeader()
		for key in sorted( self.glyph.keys()):
			print PTVGlyphHtml( self.glyph[ key ]).AsTableRow()
		print "</table>"
		
	def ReportGlyphs( self ):
		print "<h2>Font Glyphs</h2>"
		print "<table>"
		print "<tr>"
		count = 0
		for key in sorted( self.glyph.keys()):
			print PTVGlyphHtml( self.glyph[ key ]).AsTableCell()
			count += 1
			if count % 5 == 0:
				print "</tr><tr>"
		print "</tr>"
		print "</table>"



class PTVGlyphHtml( PTVFontFile.PTVGlyph ):
	""" report various statistics about a PTF font Glyph in HTML """
	
	def __init__( self, glyph ):
		self.font = glyph.font 
		self.offset = glyph.offset 
		self.code = glyph.code 
		self.yoff = glyph.yoff 
		self.advance = glyph.advance 
		self.height = glyph.height 
		self.xoff = glyph.xoff 
		self.width = glyph.width 
		self.length = glyph.length 
		self.bits = glyph.bits 
	
	@classmethod
	def AsTableHeader( cls ):
		return (
			"<tr><th colspan=2>Code</th>"
			+ "<th colspan=5>Properties</th>"
			+ "<th colspan=2>Raw Data</th></tr>\n"
			+ TableHead([ 
				"Dec/Hex",
				"Ascii", 
				"Height",
				"Width",
				"Adv.",
				"Xoff",
				"Yoff",
				"Offset",
				"Data Bytes",
				]))
			
	def AsTableRow( self ):
		return TableRow([
					(( "%3d" % self.code )
					+ " / " + ( "%02x" % self.code )),
					( "%c" % self.code ),
					( "%2d" % self.height ),
					( "%2d" %  self.width ),
					( "%2d" % self.advance ),
					( "%2d" % self.xoff ),
					( "%2d" % self.yoff ),
					( "%04x" % self.offset ),
		#			( "%3d  " % self.calcNumBytes()),
					str( self.bits )])

	def RowList( self ):
		return [ row.replace( " ", SPACE ) 
				for row in self.RowListWithBoxAndNums()]

	def AsTableCell( self ):
		""" the cell itself being a table """
		return ("<td><table>"
			+ TableHead([ "%3d %02x %c" % ( self.code, self.code, self.code )])
			+ "<tr><td><tt>"
			+ "</tt></td></tr><tr><td><tt>".join( self.RowList())
			+ "</tt></td></tr>"
			+ "</table></td>" )
	


###########################
# misc utils

def begin( tag, attr ):
	return ( "<" 
		+ tag 
		+ " "
		+ "".join([ " %s=%s" % ( key, repr( val )) for key, val in attr.items()])
		+ ">" )
	
def TableRow( list, rowattr={}, cellattr={}):
	TD = begin( "td", cellattr )
	return ( begin( "tr", rowattr )
			+ TD
			+ ( "</td>" + TD ).join( list )
			+ "</td></tr>" )

def TableHead( list, rowattr={}, cellattr={}):
	TH = begin( "th", cellattr )
	return ( begin( "tr", rowattr )
			+ TH 
			+ ( "</td>" + TH ).join( list )
			+ "</th></tr>" )

def Table( headRows, bodyRows ):
	return "<table>" + headRows + bodyRows + "</table>"
		

###########################
# main program / unit test

if __name__ == "__main__":
	import sys
	
	for name in sys.argv[1:]:
		ff = PTVFontFileHtml( name )
		ff.ReportHeading()
		ff.ReportGlyphs()
		ff.ReportTables()
		
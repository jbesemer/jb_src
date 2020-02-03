
import os, sys
import re
import StringIO


class RCFontFile( object ):
	""" represent an RC font file (as we know it) including all glyphs """
	
	def __init__( self, filename=None ):
		self.filename = filename
		self.res = None
		self.info = None
		self.tables = {}
		if filename:
			self.Load( filename )

	def Load( self, filename ):
		self.filename = filename
		skipping = False
		input = FilteredFile( self.filename )

		while True:
			line = input.peekline()
			if line == None:
				break

			if not line:
				input.getline()
				continue

			if re.match( "\\s*RES\\s*\\(", line ):
				self.res = RCFontFileRES( input )

			elif re.match( "\\s*o_font_info_desc", line ):
				self.info = RCFontInfoDesc( input )
				
			elif re.search( "short|char|\\[\\s*\\]", line ):
				tab = RCFontTable( input )
				self.tables[ tab.name ] = tab

			else:
				raise "Unknown syntax: " + input.getline()

	def __str__( self ):
		return ( "RCFontFile{ "
			+ "\n\t" + str( self.res )
			+ "\n\t" + str( self.info )
			+ "\n\t"
			+ "\n\t".join([ name + ": " + str( tab ) 
							for name, tab in self.tables.items() ])
			+ "\n\t}" )

class RCFontFileHeader( object ): pass
	
class RCFontFileGlyph( object ):
	def __init__( self ):
		self.x 
		self.y
		self.z
		self.data=[]
			
# above and below we assume that the headers are all on one line
# we also assume there's no data on the header lines

class RCFontTable( object ):
	def __init__( self, input=None ):
		self.input = input
		if input:
			self.Load( input )
			
	def Load( self, input ):
		header = input.getline()
		header = re.sub("\\[\\s*\\]\\s*=\\s*{\\s*$", "", header )
		fields = header.split()
		self.name = fields[-1]
		
		if "short" in fields:
			self.type = "short"
		elif "char" in fields:
			self.type = "byte"
		else:
			self.type = "int"
		
		self.data = []
		
		more = True
		while more:
			
			line = input.getline()
			if line == None:
				return
				
			if "}" in line:
				line = re.sub( "}.*", "", line )
				more = False

			line = line.strip()
			if not line:
				continue

			nums = line.split( "," )
			for num in nums:
				num = num.strip()
				if num:
					self.data.append( int( num ))
					
	def __str__( self ):
		if self.type == "byte":
			fmt = I3
		else:
			fmt = I5
			
		return ( "RCFontTable{"
			+ "\n\t\tName:    " + self.name
			+ "\n\t\tType:    " + self.type
			+ "\n\t\tData:" 
			+ "\n\t\t\t"
			+ " ".join([ fmt( i ) for i in self.data[ : 8 ]])
			+ "\n\t\t\t...\n\t\t\t"
			+ " ".join([ fmt( i ) for i in self.data[ -8 : ]])
			+ "\n\t\t}"
			)
			
		

class RCFontInfoDesc( object ):
	CNAME = "RCFontInfoDesc"
	
	def __init__( self, input=None ):
		self.input = input
		if input:
			self.Load( input )
			
	def Load( self, input ):
		header = input.getline()
		fields = header.split()
		self.name = fields[ 1 ]
		self.type = "o_font_info_desc"
		
		self.LoadData( input )
		
		self.fontName = stripNoise( self.data[ 0 ])
		self.authority = stripNoise( self.data[ 1 ])
		self.charSets = self.data[ 2 ]
		self.additionalInfo = self.data[ 3 ]
		self.numChars = int( self.data[ 4 ])
		self.encoding = self.data[ 5 ]
		self.fontType = self.data[ 6 ]
		self.rendering = self.data[ 7 ]
		self.version = self.data[ 8 ]
		self.direction = self.data[ 9 ]
		self.Width = int( self.data[ 10 ])
		self.Height = int( self.data[ 11 ])
		self.Ascent = int( self.data[ 12 ])
		self.Descent = int( self.data[ 13 ])
		self.vspacing = int( self.data[ 14 ])
		self.hspacing = int( self.data[ 15 ])
		self.PointSize = int( self.data[ 16 ])
		
		self.items = [
			( "Name" 			, self.name ),
			( "Type" 			, self.type ),
			( "FontName" 		, self.fontName ),
			( "Authority" 		, self.authority ),
			( "CharSets" 		, self.charSets ),
			( "AdditionalInfo"	, self.additionalInfo ),
			( "NumChars" 		, self.numChars ),
			( "Encoding" 		, self.encoding ),
			( "FontType" 		, self.fontType ),
			( "Rendering" 		, self.rendering ),
			( "Version" 		, self.version ),
			( "Direction" 		, self.direction ),
			( "Width" 			, self.Width ),
			( "Height" 			, self.Height ),
			( "Ascent" 			, self.Ascent ),
			( "Descent" 		, self.Descent ),
			( "VSpacing" 		, self.vspacing ),
			( "HSpacing" 		, self.hspacing ),
			( "PointSize" 		, self.PointSize ),
			]
	
	def LoadData( self, input ):	
		more = True
		text = ""
		while more:
			line = input.getline()
			if line == None:
				break
			
			if "}" in line:
				line = re.sub( "}.*", "", line )
				more = False
				
			text += line
			
		self.data = [ item.strip() for item in text.split(",")]
			
	def __str__( self ):
		return ( self.CNAME + " {"
			+ "\n\t\t"
			+ "\n\t\t".join([ ( name + ":" ).ljust( 18 ) + str( val )
						for name, val in self.items ])
			+ "\n\t\t}" )
			
			

class RCFontFileRES( RCFontInfoDesc ):
	CNAME = "RCFontFileRES"

	def Load( self, input ):
		header = input.getline()
		
		header = re.sub( ".*\\(", "", header )
		self.name = re.sub( "\\).*", "", header )
		fields = header.split( "," )
		self.name = stripNoise( fields[0])
		self.type = fields[1].strip()
		
		self.LoadData( input )
		
		self.type = self.data[0]
		self.glyphData = self.data[1]
		self.indexData = self.data[2]
		self.ascent = int( self.data[3])
		self.descent = int( self.data[4])
		self.firstCode = int( self.data[5])
		self.lastCode = int( self.data[6])
		if len( self.data ) > 7:
			self.infoStruct  = stripNoise( self.data[7])
		else:
			self.infoStruct = ""
			
		self.items = [
			( "Name", 			self.name ),
			( "Type", 			self.type ),
			( "Glyphs", 		self.glyphData ),
			( "Index", 			self.indexData ),
			( "AscentTab", 		self.ascent ),
			( "DescentTab",		self.descent ),
			( "FirstCode", 		self.firstCode ),
			( "LastCode", 		self.lastCode ),
			( "InfoStruct", 	self.infoStruct ),
			]


class FilteredFile( file ):
	def __init__( self, filename ):
		""" read-only file with C-style comments removed """
		file.__init__( self, filename )
		self.skipping = False
		self.havePeeked = False
		self.pendingLine = None
		
	def getline( self ):
		""" get next line """
		self.peekline()
		self.havePeeked = False
		return self.pendingLine	

	def peekline( self ):
		""" one line look-ahead """
		if not self.havePeeked:
			self.pendingLine = self.getNextLine()
		self.havePeeked = True
		return self.pendingLine
			
	def getNextLine( self ):
		""" readline with comments removed and whitespace stripped """
		# this expressly allows empty strings returned for a line
		# an explicit None indicates eof.
		line = file.readline( self )
		if not line:
			return None	# none expressly
			
		line = re.sub( "//.*", "", line )
		line = re.sub( "/\\*.*\\*/", "", line )
		
		if not self.skipping and re.search( "/\\*", line ):
			self.skipping = True
			line = re.sub( "/\\*.*", "", line ).strip()
			if line:
				return line
				
		while self.skipping:
			line = file.readline( self )
			if not line:
				return None
			
			if re.search( "\\*/", line ):
				self.skipping = False
				line = re.sub( ".*\\*/", "", line )
				
		return line.strip()


def stripNoise( s ):
	return re.sub( '[&",]', '', s ).strip()
	
def Hex( n ):	return "%02x" % n
def I3( n ):	return "%3d" % n
def I5( n ):	return "%5d" % n
	
	
#######################################


if __name__ == "__main__":
	for name in sys.argv[ 1 : ]:
		ff = RCFontFile( name )
		print ff
		
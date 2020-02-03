import sys
import HTMLParser

class MyParser( HTMLParser.HTMLParser ):
	
	""" split atmel lo/hi fields """
	
	def __init__( self, data=None ):
		HTMLParser.HTMLParser.__init__( self )
		self.col_num = 0
		self.in_td = 0
		self.td_data = ""
		if data:
			self.feed( data )
			self.close()

	# output primitives:

	def write( self, *data ):
		for datum in data:
			sys.stdout.write( datum )
			
	def writeln( self, *data ):
		if data:
			self.write( *data )
		self.write( "\n" )

	def format_tag( self, tag, attrs ):
		return ( "<" 
			+ tag
			+ "".join(
				[ " " + key + "=" + repr( value )
					for key, value in dict(attrs).items() ])
			+ ">" )

	def write_tag( self, tag, attrs ):
		self.write( self.format_tag( tag, attrs ))
	
	# HTML handlers:
	
	SELECTED_LO = [ 28, 30 ]
	SELECTED_HI = [ 29, 31 ]
	SELECTED = SELECTED_LO + SELECTED_HI

	def output_range( self ):
		if "-" not in self.td_data:
			self.write( self.td_data.strip())
			return
			
		lo, hi = self.td_data.split( "-" )
		if self.col_num in self.SELECTED_LO:
			self.write( lo.strip())
		elif self.col_num in self.SELECTED_HI:
			self.write( hi.strip())
		else:
			raise "IB UNK"

	def handle_starttag( self, tag, attrs ):
		if tag == "tr":
			self.col_num = 0
			self.in_td = 0
		elif tag == "td":
			attrs = dict( attrs )
			try:
				self.col_num += int( attrs[ "colspan" ])
			except KeyError:
				self.col_num += 1
			self.in_td = 1
			self.td_data = ""
			
			if "x:str" in attrs:		# fucking MicSoft
				del attrs[ "x:str" ]
				self.write_tag( tag, attrs )
				return
				
		self.write( self.get_starttag_text())
		
	def handle_startendtag( self, tag, attrs ):
		self.write( self.get_starttag_text())
		
	def handle_endtag( self, tag ):
		if tag == "tr":
			self.col_num = 0
			self.in_td = 0
		elif tag == "td":
			if self.col_num in self.SELECTED:
				self.output_range()
			self.in_td = 0
		self.write( "</", tag, ">" )

	def handle_data( self, data ):
		if self.in_td and self.col_num in self.SELECTED:
			self.td_data += data
		else:
			self.write( data )
		
	def handle_charref( self, name ):
		self.write( "&#",  name, ";" )
		
	def handle_entityref( self, name ):
		self.write( "&",  name, ";" )
		
	def handle_comment( self, text ):
		self.write( "<!--", text, "-->" )
		
	def handle_decl( self, decl ):
		self.write( "<!", decl, ">" )
		
	def handle_pi( self, data ):		
		self.write( "<?", data, ">" )

# unit test

if __name__ == "__main__":
	for name in sys.argv[1:]:
		MyParser( file( name ).read())
		
		
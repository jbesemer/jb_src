import sys
import HTMLParser

class MyParser( HTMLParser.HTMLParser ):
	
	""" strip <img> tags """
	
	def __init__( self, data=None ):
		HTMLParser.HTMLParser.__init__( self )
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

	# HTML handlers:
	
	def handle_starttag( self, tag, attrs ):
		if tag != "img":
			self.write( self.get_starttag_text())
		
	def handle_startendtag( self, tag, attrs ):
		if tag != "img":
			self.write( self.get_starttag_text())
		
	def handle_endtag( self, tag ):
		if tag != "img":
			self.write( "</", tag, ">" )

	def handle_data( self, data ):
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
		
		
import re

def quote( str ):
	def quotesub( match ):
		return "^" + chr( ord( match.group(1)) + 0100 )
		
	return re.sub( "([\0-\37])", quotesub, str )

if __name__ == "__main__":
	print quote( "AB\3\4EF\7\8IJK\0" )

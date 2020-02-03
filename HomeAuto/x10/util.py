#################################
# misc utilities

import re

def quote( str ):
	def quotesub( match ):
		return "^" + chr( ord( match.group(1)) + 0100 )
	return re.sub( "([\0-\37])", quotesub, str )

def valid_address( addr ):
	return re.match( "[A-Pa-p]((0?[1-9])|(1[0-6]))$", addr )

def numeric( str ):
	return re.match( "[0-9]+$", str )

def norm_addr( addr ):
	if valid_address( addr ):
		return addr[0].upper() + ( "%02d" % int( addr[1:] ))
	else:
		raise SyntaxError
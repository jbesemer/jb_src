
import string, re
import util

# return a list of pins, 
# given an arg of one of the following forms
#	A3
#	B3-5
#	C3-C5
#	D*
#	a space-separated list of the above
#
# Raises ArgError if illegal syntax is encountered

MAXBANK = 16

def ParsePin( arg ):

	def s2pin( s ):
		return "%02d" % int( s )

	if ' ' in arg:
		r = []
		for a in arg.split():
			r.extend( ParsePin( a ))
		return r

	if len( arg ) == 2 and arg[1] == '*':
		fmt = arg[0].upper() + "%02d"
		return [ fmt%i for i in xrange( 16 )]

	if '*' in arg:
		raise ArgError

	if '-' in arg:
		return parsePinRange( arg )

	return [( arg[0].upper() + s2pin( arg[ 1: ]))]

def parsePinRange( arg ):
	#pin range is like 'A3-5' or "B3-B6"

	a, b = arg.split( '-', 1 )

	if len( a ) == 0		\
	or len( b ) == 0		\
	or '-' in a 			\
	or '-' in b 			\
	or a[0] not in string.letters:
		raise ArgError

	banka = a[ 0 ].upper()
	a = a[ 1: ]

	if b[0] in string.letters:
		bankb = b[ 0 ].upper()
		b = b[1:]
		if banka > bankb:
			raise ArgError
	else:
		bankb = banka

	if not re.match( '^\\d+$', a ) \
	or not re.match( '^\\d+$', b ):
		raise ArgError

	a = int( a )
	b = int( b )

	def bankRange( a, b ):
		return[ chr( ch )
			for ch in xrange( ord( a ), ord( b ) + 1 )]

	def pinRange( bank ):
		if bank == banka:
			l = a
		else:
			l = 0

		if bank == bankb:
			h = b
		else:
			h = MAXBANK - 1
		return xrange( l, h + 1 )

	return [ bank + ( "%02d" % pin ) 
			for bank in bankRange( banka, bankb )
				for pin in pinRange( bank )
			]


if __name__ == "__main__":
	def test( s ):
		print s
		print ParsePin( s )

	test( "a1" )
	test( "a1-3" )
	test( "b*" )
	test( "c9-d4" )
	test( "c14-c15" )
	test( "h* i* j*" )

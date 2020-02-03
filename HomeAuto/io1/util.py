########################################
# misc. utilities

import string
import re

class ArgError: pass

# convert char a-z to num 0-25

def c2b( ch ):
	if ch == '@':
		return 0
	if ch in string.letters:
		return ord( ch.upper()) - ord( '@' )
	elif ch in string.digits:
		return ord( ch ) - ord( '0' )
	else:
		outcs( "Illegal numeric char: '" + ch + "'" )

def s2w( s ):
	word = 0
	for ch in s:
		word = ( word << 4 ) | c2b( ch )
	return word

def i2s( n ):
	return "%d" % n

def i2d( n ):
	return "%02d" % n

def f2s( n ):
	return "%4.2f" % n

def setbit( value, pin, bit ):
	if bit:
		value = value | ( 1 << pin )
	else:
		value = value & ~( 1 << pin )
	return value

def i2h4( n ):
	return "%04X" % ( n % 0xFFFF )

def s2pin( n ):
	if not re.match( '^\\d+$', n ):
		raise ArgError

	return i2pin( n )

def i2pin( n ):
	return chr( ord( '@' ) + int( n ))


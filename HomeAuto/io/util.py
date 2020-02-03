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
		print "# Illegal numeric char: '" + ch + "'", "0x%02x" % ord( ch )

def c2pin( pin ):
	if len( pin ) == 2 and pin[1] == '*':
		return pin[0].upper() + pin[1]
	else:
		return pin[0].upper() + i2d( c2b( pin[1]))

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

########################################
# form a timestamp

_prev_tv = (0,0,0,0)

def ts():
	global _prev_tv
	import time

	t = time.localtime( time.time())
	next_tv = ( t[0], t[1], t[2], t[8])
	if _prev_tv != next_tv:
		_prev_tv = next_tv
		print time.asctime( t )
		t = time.localtime( time.time())
	return "%02d:%02d:%02d " % ( t[3], t[4], t[5] )



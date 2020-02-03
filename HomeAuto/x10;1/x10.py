from __future__ import nested_scopes

import os,sys,string
import UserDict
import tty
import re

####################################################
# address aliases
#

ALIAS_FILE = "x10_aliases"

class Alias( UserDict.UserDict ):
	
	def load( self, filename ):
		"initialize dictionary from file"

		file = open( filename, "r" )
		aliases = file.read()
		file.close()

		P1 = re.compile( '#.*', re.M )
		P2 = re.compile( '[ \t]+', re.M )
		P3 = re.compile( '^ +', re.M )

		aliases = P1.sub( '', aliases )
		aliases = P2.sub( ' ', aliases )
		aliases = P3.sub( '', aliases )
		aliases = aliases.split( '\n' )

		def dodef( ali ):
			a = ali.split()
			if a and a[ 1 ] == '=':
				self.__setitem__( a[ 0 ], a[ 2: ])

		aliases = map( dodef, aliases )

	def reload( self, filenames ):
		self.dict.clear()
		for filename in filenames:
			self.load( filename )
		

	def __setitem__( self, item, value ):
		"remember definition, normalizing key"

		self.data[ item.lower() ] = value

	def __getitem__( self, item ):
		"fetch definition, normalizing key and following all nested aliases"

		items = self.data[ item.lower()]
		res = []
		for item in items:
			if item in self.data.keys():
				res.extend( self.__getitem__( item ))
			else:
				res.append( item )

		return res

	def __repr__( self ):
		"represent entire dictionary as string"
		s = ''
		for k in self.data.keys():
			s += k + ' = ' + `self.data[ k ]` + '\n'
		return s



Aliases = Alias()


################################################
# serial comm to/from X10 unit
#

# tty parameters

tty = "/dev/ttyS1"

stty_flags = "2400 cs8 cstopb -echo -echoctl -ignbrk -ignpar icrnl -isig -icanon -tostop"

def normaddr( a ):
	return "%1s%02d" % ( a[0].upper(), int( a[1:]))


def normcmd( cmd, a ):
	return "%1s%2s" % ( a[0].upper(), cmd.upper() )


def send_cmd( cmd, addr ):
	print normaddr( addr )
	print normcmd( cmd, addr )
	

################################################
# command processing
#

class Command:
	"Regular Command"

	def __init__( self, code ):
		self.code = code

	def parse( self, argv ):
		for arg in argv:
			for addr in Aliases[ arg ]:
				send_cmd( self.code, addr )

class CommandRep( Command ):
	"command like Dim or Bright with optional repeat count"

	def parse( self, argv ):
		if re.match( '[0-9]+$', argv[ 0 ]):
			repeat = int( argv[ 0 ])
			print normaddr( "R" + str( repeat ))
			argv = argv[1:]
		Command.parse( self, argv )
			

Commands = {
	"on":			Command( "ON" ),
	"off":			Command( "OF" ),
	"alloff":		Command( "A0" ),
    "allon":		Command( "L1" ), 
    "lightson":     Command( "L1" ), 
    "lightsoff":    Command( "L0" ), 
	"lights1":      Command( "L1" ), 
    "lights0":      Command( "L0" ),
	"bright":		CommandRep( "BR" ),
	"dim":			CommandRep( "DI" ),
}



# main program

def main():
	Aliases.load( ALIAS_FILE )
#	print "all:", Aliases
#	print "lr:", Aliases[ 'lr' ]

	tty.Init( tty.TTY1 )

	if len( sys.argv ) > 1:
		command = Commands[ sys.argv[ 1 ].lower() ]
		command.parse( sys.argv[ 2: ])


main()


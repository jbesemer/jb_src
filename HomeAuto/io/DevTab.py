
from Listeners import *
from util import *


__all__ = [ "DevTab", "Devices" ]


class DevTab:

	DI = 0
	DO = 1
	RO = 3
	AI = 4

	def __init__( self, tab ):
		self.tab = tab

		for key in self.tab.keys():
			self.tab[ key ].bank = key

	def __len__( self ):
		return len( self.tab )

	def __getitem__( self, index ):
		return self.tab[ index.upper() ]

	def AddMonitor( self, client, pin ):
		print "AddMonitor ", c2pin( pin )
		dev = self[ pin[0]]
		p = pin[1]
		if p == '*':
			dev.add( client, dev.allPins())
		else:
			dev.add( client, 1 << c2b( p ))

	def RemMonitor( self, client, pin ):
		print "RemMonitor ", c2pin( pin )
		dev = self[ pin[0]]
		p = pin[1]
		if p == '*':
			dev.rem( client, dev.allPins())
		else:
			dev.rem( client, 1 << c2b( p ))

	def Withdraw( self, client ):
		for dev in self.tab.values():
			dev.withdraw( client )

	def Status( self ):
		print "Devices:", len( self.tab )
		for key, dev in self.tab.items():
			if len( dev.listeners ):
				print "Device[", key, "] Listeners:", len( dev.listeners )

class DevTabEntry:
	def __init__( self, type, pins, name ):
		self.type = type
		self.pins = pins
		self.name = name
		self.bank = '@'
		self.masks = 0
		self.values = 0
		self.listeners = Listeners()
#		self.State = State()

	def allPins( self ):
		return 2 ** self.pins - 1

	def change( self, pin, value ):
		msg = ( ts()
				+ "CHANGE " 
				+ self.bank + i2d( pin ) 
				+ " " 
				+ i2s( value )
				+ '\n' 
				)

#		print msg,

		self.listeners.sendMatching( 
			( 1 << pin ),
			msg )

	def changes( self, diff, value ):
		for pin in xrange( 16 ):
			if diff & 1:
				self.change( pin, value & 1 )
			value = value >> 1
			diff = diff >> 1

	def updatePin( self, pin, value ):
		self.change( pin, value )
		self.values = setbit( self.values, pin, value )

	def updateBank( self, values ):
		if self.values != values:
			diff = self.values ^ values
			self.changes( diff, values )
			self.values = values

	def add( self, client, bits ):
		self.listeners.add( client, bits )

	def rem( self, client, bits ):
		self.listeners.rem( client, bits )

	def withdraw( self, client ):
			self.listeners.withdraw( client )


DI = DevTab.DI
DO = DevTab.DO
RO = DevTab.RO
AI = DevTab.AI


ProductionDevTab = {
	'A':	DevTabEntry( DI, 16, "8100.0.A" ),
	'B':	DevTabEntry( DI, 16, "8100.0.B" ),
	'C':	DevTabEntry( DI, 16, "8100.1.A" ),
	'D':	DevTabEntry( DI, 16, "8100.1.B" ),
	'E':	DevTabEntry( DI, 16, "8100.2.B" ),
	'F':	DevTabEntry( DI, 16, "1700.0.A" ),
	'G':	DevTabEntry( DI, 16, "8100.3.B" ),

	'H':	DevTabEntry( DO, 16, "1700.0.B" ),
	'I':	DevTabEntry( DO, 16, "8100.2.A" ),
	'J':	DevTabEntry( DO, 16, "8100.3.A" ),

	'K':	DevTabEntry( RO,  6, "8300.0.A" ),
	'L':	DevTabEntry( RO,  8, "8400.2.A" ),
	'M':	DevTabEntry( RO,  8, "8400.1.A" ),

	'N':	DevTabEntry( AI, 10, "8100.0.A" ),
	'O':	DevTabEntry( AI, 10, "8100.0.A" ),
	'P':	DevTabEntry( AI, 10, "8100.0.A" ),
	'Q':	DevTabEntry( AI, 10, "8100.0.A" ),
}


DebugDevTab = {
	'A':	DevTabEntry( DI, 16, "1700.0.A" ),
	'B':	DevTabEntry( DO, 16, "1700.0.B" ),

	'C':	DevTabEntry( AI, 10, "8100.0.A" ),
	'D':	DevTabEntry( AI, 10, "8100.0.A" ),
	'E':	DevTabEntry( AI, 10, "8100.0.A" ),
	'F':	DevTabEntry( AI, 10, "8100.0.A" ),
}


# Devices = DevTab( DebugDevTab )
Devices = DevTab( ProductionDevTab )




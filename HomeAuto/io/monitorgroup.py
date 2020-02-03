# monitor group -- provide audio and visual feedback
# depending on the settings of various low-level inputs.
#
# read in group definition files.
# attach to io and monitor inputs.
# display text and/or queue sounds depending  
# on selected rising and falling signals.

import sys
import string

import ioclient
import soundclient

######################################
# important constants

NL = "\n"
HT = "\t"

######################################
# initialize and open our sound and io
# client connectors.
# No point in going any further if this fails.
#

ss = soundclient.SoundServerImmed()
ss.open()

io = ioclient.IoClient( "MonitorGroup" )
io.open()


######################################
# Action abstracts the various things that
# can be triggered when a signal occurs
#

class Action:
	pass

	def __str__( self ):
		return self.cmd + ' ' + self.text

class ActionShow( Action ):
	def __init__( self, pin, name, text ):
		self.cmd = "show"
		self.pin = pin
		self.name = name
		self.text = text

	def run( self, timestamp ):
		print timestamp, self.pin, self.name, "--", self.text

class ActionPlay( Action ):
	def __init__( self, pin, name, text ):
		self.cmd = "play"
		self.pin = pin
		self.name = name
		self.text = text

	def run( self, timestamp ):
		ss.say( self.text )

class ActionSay( Action ):
	def __init__( self, pin, name, text ):
		self.cmd = "say"
		self.pin = pin
		self.name = name
		self.text = text

	def run( self, timestamp ):
		ss.say( self.name + ' ' + self.text )

ActionMap = {
	"show": 	ActionShow,
	"say":		ActionSay,
	"play":		ActionPlay,
	}

######################################
# events track the mapping betewen
# pin transitions and corresponding actions.
#

class Event:
	def __init__( self, pin, name ):
		self.pin = pin
		self.name = name
		self.actions = [[], []]

	def addActionString( self, str ):
		rising = ( str[ 0 ] == '<' )
		cmd, arg = str[1:].split( ' ', 1 )

		arg = string.replace( arg, '$name', self.name )
		arg = string.replace( arg, '$pin', self.pin )

		if cmd in ActionMap.keys():
			self.addAction( 
				rising, 
				ActionMap[ cmd ]( self.pin, self.name, arg ))
		else:
			raise "illegal action", cmd
	
	def addAction( self, rising, action ):
		self.actions[ rising ].append( action )

	def trigger( self, timestamp, ifRising ):
		for action in self.actions[ ifRising ]:
			action.run( timestamp )

	def __str__( self ):
		res = NL + self.pin + ' = ' + self.name + NL
		for i in xrange(2):
			for act in self.actions[i]:
				res += HT + ( "><"[i]) + str( act ) + NL
		return res


######################################
# monitor tells io what pins to monitor
# and activates events according to the results.
#

class Monitor:
	def __init__( self ):
		self.name = "[Unk]"
		self.events = {}

	def open( self ):
		if not self.events.keys():
			raise "No events to monitor"

		io.monitor( string.join( self.events.keys()))

		ss.say( "/home/jb/sounds/motstart.wav" )

	def close( self ):
		pass

	def run( self ):

		while 1:
			data = io.readline()
			if not data:
				return
			# print data

			msg = data.split()

			if len( msg ) >= 4 and msg[1] == "CHANGE":
				timestamp = msg[0]
				pin = msg[2].upper()
				rising = int( msg[3])
				if pin in self.events.keys():
					self.events[ pin ].trigger( 
						timestamp,
						rising )
				else:
					print "Unknown pin:", pin
			else:
				print "Unrecognized message:", data

	def load( self, filename ):
		file = open( filename, 'rt' )
		curev = None
		while 1:
			line = file.readline()
			if not line:
				break

			# print line
			line = line.strip()
			if not line or '#' == line[0]:
				continue

			if line[:5] == 'group':
				self.name = line[5:].strip()

			elif '=' in line:
				pin, name = line.split( '=', 1 )
				pin = pin.strip()
				name = name.strip()
				curev = Event( pin, name )
				self.events[ pin ] = curev

			elif not curev:
				print "misplaced directive:", line

			elif '<' == line[ 0 ] or '>' == line[ 0 ]:
				curev.addActionString( line )

			else:
				print "unrecognized directive:", line

		file.close()

	def __str__( self ):
		res = "group " + self.name + NL
		for ev in self.events.values():
			res += NL + str( ev ) + NL
		return res

def main():

	monitor = Monitor()

	for arg in sys.argv[1:]:
		monitor.load( arg )

	monitor.open()
	try:
		monitor.run()
	finally:
		monitor.close()
		io.close()
		ss.close()


def UnitTest():
	monitor = Monitor()
	monitor.load( "testgroup.sigdef" )
	print monitor

# UnitTest()

main()

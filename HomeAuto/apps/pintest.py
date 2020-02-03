#!/usr/local/bin/python2.2

import os, sys
import string
import socket
import signal
import thread
import time

sys.path.append( "/home/jb/lib/python" )
import whereami
sys.path.append( "/home/jb/x10" )
sys.path.append( "/home/jb/io" )

from PinsEnglish import *
import soundclient

import x10client
import ioclient

import ParsePins; ParsePin=ParsePins.ParsePin

ENABLE_SOUND = 0

if whereami.HOST == "igor":
	KEY1 = "A01"	# turn current signal off or on
	KEY2 = "A02"	# go to next signal (off: next, on: prev)
	DEFAULT_ARGS = [ "H*", "I*", "J*" ]
else:
	KEY1 = "C01"	# turn current signal off or on
	KEY2 = "C02"	# go to next signal (off: next, on: prev)
	DEFAULT_ARGS = [ "B*" ]

KEYS = [ KEY1, KEY2 ]
BANKSIZE = 16

USE_PHONETIC_ALPHABET = 0	# able, baker, ... vs. A, B, ...

OnOff = {
	'0':	" off ",
	 0 :	" off ",
	'1':	' on ',
	 1 :	' on ' }


if ENABLE_SOUND:
	Sound = soundclient.SoundServerImmed()
	Sound.open()
	def say( text ): Sound.sendspeech( text )
else:
	def say( text ): pass

# extend IOClient class to monitor IOs.
# mainly we just announce what happens.

class IOC( ioclient.IoClient ):

	def monitor( self ):

		if ENABLE_SOUND:
			Sound = soundclient.SoundServerImmed()
			Sound.open()
			def say( text ): Sound.sendspeech( text )
		else:
			def say( text ): pass

		for line in self.readline:
			line = line.strip()
			if line == "#Done":
				continue
			print line

			# lines: "hh:mm:ss CHANGE unit [01]"

			frags = line.split()
			if len( frags ) >= 3 and frags[1] == "CHANGE":

				unit = frags[2]
				word = OnOff[ frags[3]]

				if USE_PHONETIC_ALPHABET:
					unit = PhoneticPin( unit )
				else:
					unit = NormalPin( unit )

				say( unit + " " + word )

			if line[:6] == "#Error":
				continue
	
	def start_monitor( self ):
		thread.start_new_thread( self.monitor, ())

# extend X10 client to monitor selected X10 signals.
# These signals are commands to drive PinTest functionality.

class XOC( x10client.X10Client ):

	def monitor( self ):
		for line in self.readline:
			line = line.strip()
			if line == "":
				continue
			print line
			field = line.split()

			if len( field ) < 3 or field[1] <> "=":
				continue

			key = field[0]
			val = int( field[2])

			if key == KEY1:
				if val:	signal.on(1)
				else:	signal.off(1)
			elif key == KEY2:
				if val:	signal.prev()
				else:	signal.next()

	def start_monitor( self ):
		thread.start_new_thread( self.monitor, ())
			
class Signal( object ):
	def __init__( self, val, state = 0 ):
		self.val = val
		self.state = state

	def __str__( self ):
		return self.val

	def off( self, verbose=0 ):
		if verbose:
			say( "off" )
		if self.state == 0:
			return
		print "turning off", self.val
		io.off( self.val )
		self.state = 0

	def on( self, verbose=0 ):
		if verbose:
			say( "on" )
		if self.state == 1:
			return
		print "turning on", self.val
		io.on( self.val )
		self.state = 1

	def next( self ):
		say( "next" )
		self.off()

		bank = self.val[0]
		num = int( self.val[1:])
		num += 1
		self.val = "%s%02d" % ( bank.upper(), num )

		self.on()

	def prev( self ):
		say( "back" )
		self.off()

		bank = self.val[0]
		num = int( self.val[1:])
		num -= 1
		self.val = "%s%02d" % ( bank.upper(), num )

		self.on()



##########################################
# Unit Test / Command Mode

if __name__ == "__main__":

	if len( sys.argv ) > 1:
		args = sys.argv[1:]
	else:
		args = DEFAULT_ARGS

	PinList  = [ ParsePin( a ) 
			for a in args 
				if a[0] <> '-' ]
	PinList = [ x for y in PinList for x in y ]
	Pins = " ".join( PinList )
	print "testing:", PinList

	# instantiate client connections for X10 and IO.
	# in this case, io is redirected to alternate server.
	# start receive monitors

	signal = Signal( PinList[ 0 ])

	if whereami.HOST == "cascade":
		io = IOC( "PinTest", server="cascade" )
	else:
		io = IOC( "PinTest" )

	xo = XOC( "PinTest" )
	xo.useropen()
	io.useropen()

	xo.add( string.join( KEYS ))
	io.add( Pins )

	signal.on()

	io.start_monitor()
	xo.monitor() 		# never returns

#	while 1:
#		signal.pause()




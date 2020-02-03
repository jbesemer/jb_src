#!/usr/local/bin/python2.2

import os, sys
import string
import socket
import signal
import thread
import time

sys.path.append( "/home/jb/lib/python" )

from GenericClient import *
from PinsEnglish import *
from x10common import *
import x10_parse
import logger
import soundclient

PHONETIC_ALPHABET = 0	# able, baker, ... vs. A, B, ...

x10_parse.log = logger.Logger()

Sound = soundclient.SoundServerImmed()
Sound.open()
def say( text ): Sound.sendspeech( text )

OnOff = {
	'0':	" off ",
	 0 :	" off ",
	'1':	' on ',
	 1 :	' on ' }



##########################################
# Command Client

class X10Client( GenericClient ):

	def __init__( self, name='X10Client', WaitFlag = 1 ):
		self.WaitFlag = WaitFlag
		self.name = name
		self.sock = None
		self.server = SERVER
		self.port = OPPORT

	def sendCommand( self, command ):
		# print "sendCommand", command
		self.send( command + "\n" )

	def sendRawCommand( self, command ):
		# print "sendRawCommand", command
		self.send( CMD_PREFIX + command + "\n" )

	def add( self, args ):
		args = x10_parse.parse_addresses( args )
		self.sendCommand( "add " + args )

	def rem( self, args ):
		args = x10_parse.parse_addresses( args )
		self.sendCommand( "add " + args )

	def get( self, args ):
		args = x10_parse.parse_addresses( args )
		self.sendCommand( "get " + args )

	def x10s( self, commands ):
		self.x10( commands.split())

	def x10( self, commands ):
		imm = x10_parse.parse( commands )
		res = x10_parse.generate( imm )
		self.sendCommand( "send " + res.join())

	def monitor( self ):
		for line in self.readline:
			line = line.strip()
			if line == "#Done":
				continue
			print line
			if '=' in line:
				unit, state = line.split( '=' )
				frags = state.split()
				word = frags[1]
				word = word[:-1]

				if PHONETIC_ALPHABET:
					unit = PhoneticPin( unit )
				else:
					unit = NormalPin( unit )

				say( unit + " " + word )

			if line[:6] == "#Error":
				continue
	
	def start_monitor( self ):
		thread.start_new_thread( self.monitor, ())
			

##########################################
# Log Client

class X10LogClient( GenericClient ):

	def __init__( self ):
		self.name = "X10Logger"
		self.sock = None
		self.server = SERVER
		self.port = LOGPORT


##########################################
# Unit Test / Command Mode

if __name__ == "__main__":

	DEFAULT = "A B C D E F G H I J K L M N O P".split()

	x10 = X10Client( "X10Watch" )
	x10.useropen()

	if len( sys.argv ) > 1:
		args = sys.argv
	else:
		args = DEFAULT

	if 1:
		def allbank( s ):
			"convert single letter to entire bank"
			if len( s ) == 1:
				return s + "*"
			else:
				return s

		args = " ".join([ allbank ( a ) for a in args ])
		
	x10.add( args )
	x10.monitor()
	x10.shutdown()

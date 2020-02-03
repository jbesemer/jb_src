#!/usr/bin/python2.1

import os, sys
from time import time, localtime, asctime
from string import *

from Analog import *
from Stat import Stat
from LogFile import *
from ErrTab import *
from DevTab import *
from util import *
import tty

########################################
# config options

########################################
# global settings

Stats = Stat()

ana = Analog( 10 )

########################################
# track input line states, transitions


def UpdateDigital( line ):
	if len( line ) < 4:
		outcs( "Bad update: " + line )
		return

	bank = line[ 0 ]
	pin = line[ 1 ]
	value = line[ 3: ]

	outes( line + "    # 0x" + i2h4( s2w( value )))

	value = s2w( value )

	if pin == '*':		# bank update
		Devices[ bank ].updateBank( value )

	else:			# pin update
		Devices[ bank ].updatePin( c2b( pin ), value )


def UpdateAnalog( line ):
	if len( line ) > 4:
		type = ord( line[ 0 ]) - ord( 'L' )
		chan = ord( line[ 1 ]) - ord( '@' )

		ana.add( type, chan, line[ 3: ])

		desi = upper( line[ 0 ]) + ( "%02d" % chan )

		outs( "Analog: " 
			+ desi
			+ line[ 3: ]
			+ "  # " 
			+ ( "%9.7f" % ana.mean( type, chan ))
			+ "  ( " 
			+ ( "%05d" % ana.count( type, chan ))
			+ " )" )


########################################
# main command cracker

def ProcessLine( line ):

	'''Process a single input line'''
	
	# processing is entirely stateless

	Stats.InLine( line )
	line = rstrip( line )

	if len( line ) == 0:
		ch = chr( 0 )	# should match no pattern
	else:
		ch = line[ 0 ]

	# lines matching this first group of patterns 
	# do NOT get echoed (or they modify before echoing)

	if ch == '~':
		return

	if ch == '{':
		Stats.BlockBegin( line )
		return

	if ch == '}':
		Stats.BlockEnd()
		return

	if len( line ) > 3 and line[2] == ':':
		UpdateAnalog( line )
		return

	if len( line ) > 3 and line[2] == '=':
		UpdateDigital( line )
		return

	if ch == '>':
		HandleSerial( line )
		return

	if ch == "?":
		outs( "Error: " + 
			ErrMessage( line[1]) + 
			" (" + line[2] + ")" )
		return

	if len( line ) == 0:
		return

	if line[:6] == "CONFIG":
		if line == "CONFIG BEGIN":
			outs( line )
		elif line == "CONFIG END":
			outs( line )
		else:
			outs( line )

	# lines matching this first group of patterns 
	# echo input

	outes( line )

	# controller restarted:

	if line == "READY":
		raise RuntimeError

	# remaining patterns follow echoed input


########################################
# initialization and startup


# init IOM

def Init():

	outcs( "IOM Initialization" )

# parse args

def Args():
	pass

########################################
# unit test / stand-alone mode

def Main():
	Args()
	Init()
	outcs( "IOM Commencement" )

	while 1:
		line = tty.ttyi.readline()
		ProcessLine( line )



if __name__ == "__main__":
	Main()


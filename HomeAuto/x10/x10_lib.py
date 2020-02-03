#!/usr/local/bin/python

##############################
# parse commands
#
#
# TODO:
#
#	Resolve overlap with L1 command and unit
#

from __future__ import nested_scopes

import os, sys, os.path
import string, re
import time

import logger
import ttyrawio
from util import *
from timetrack import TimeTracker
from TimeoutCalc import *
from flags import *

##############################
# global parameters/constants

log_file = "x10.log"
tty_name = "/dev/ttyS1"

#################################
## instantiate/initialize subordinate objects

timetracker = TimeTracker()
calc_timeout = TimeoutCalculator()
log = logger.Logger()
tty = ttyrawio.RawTtyIO( tty_name, log )

##################################
# command / response protocol

def send_x10( cmd, maxRetries=9 ):
	"send a command and retry until a proper reply is received"
	
	for retry in xrange( maxRetries ):

		if retry:
			time.sleep( 1.0 )

		res = command_response( cmd, calc_timeout( cmd ))

		if check_result( cmd, res ):
			return

	log.echo_send( "Retry count exceeded" )


def command_response( cmd, timeout ):
	"send the command and get the response, if any"

	# fake success
	if NFlag.value:
		log.echo_send( cmd )
		cmd = "!" + cmd
		log.echo_recv( cmd )
		return cmd

	# Although the PC communicates with the X10 device
	# at 2400 baud, the X10 device communicates with the
	# powerline at only 60 baud.  Assuming the X10 device
	# receives simultaneously with transmitting (it must),
	# then we are talking 16.67 msec to the device, 666.67
	# msec. to send/recv on the power line, and another 
	# 16.67 msec. back to the PC.  
	#
	# This totals 0.7 seconds round trip per command.

	# send the command
	tty.send( cmd )

	# return response
	return tty.getline( timeout=timeout )


def check_result( cmd, res ):

	"check X10's response and return 1 if command was successful"

	if res == None:
		log.echo_recv( "tty.getline() timed out" )

	elif res == ( "?" + cmd ):
		log.echo_recv( " -- ERROR returned from X10: " 
			+ quote( res ))

	elif res[0] == "?":
		log.echo_recv( " -- ERROR returned from X10: " 
			+ quote( res ))

	elif res == ">XXX":
		log.echo_recv( " -- command was garbled" )

	elif res == ( "!" + cmd ) or res == ( ">" + cmd ):
		# results.append( res )
		return 1

	elif res[0] == ">":
		# results.append( res )
		pass

	else:
		log.echo_recv( " -- unexpected result (" + quote( res ) + ")" )

	return 0


#################################
# execute codes

# execute a sequence of codes

def execute( codes ):
	for code in codes:
		send_x10( code )


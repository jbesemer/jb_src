#!/usr/local/bin/python

##############################
# Format and send X10 commands
#
# Arg Syntax: { x10_command { unit_codes } }
#
#
# TODO:
#
#	Resolve overlap with L1 command and unit
#

from __future__ import nested_scopes

import os, sys, os.path
import string, re
import select
import time

from x10_lib import *
import x10_parse

tty.echodefault = 1

import logger
x10_parse.log = log = logger.Logger()

##########################################
# mainlines


def main():

	# import pprint;	ppp=pprint.PrettyPrinter(indent=4); pp=ppp.pprint
	def pp( codes ):
		for code in codes:
			print code

	if len( sys.argv ) <= 1:
		print "For help type:", command_name, "-h"
		return

	intermediate = x10_parse.parse( sys.argv[ 1: ])

	timetracker.countCommand( len( intermediate ))

	if IFlag.value:
		print "Itermediate code:"
		pp( intermediate )
		# if not ( GFlag.value or WFlag.value ):
		# 	return

	if WFlag.value:
		print "Watching X10 line activity..."
		tty.watch()
		# never returns

	if log.errors or not intermediate:
		return

	executable = x10_parse.generate( intermediate )

	if GFlag.value:
		print "Generated codes:"
		pp( executable )

	if log.errors or not executable:
		return

	if SFlag.value:
		timetracker.time( execute, executable )
	else:
		execute( executable )


if __name__ == "__main__":
	main()



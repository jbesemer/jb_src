from __future__ import nested_scopes

import os, sys, os.path
import string, re

sys.path.append( "/home/jb/lib/python" )

from listreader import *
from util import *
from arbnum import *

valid_house_codes = "ABCDEFGHIJKLMNOP"
valid_unit_codes = range( 1, 17 )

def forw_help( *args ):	help( args ) # link for circular references
from x10_commands import *

import aliases

alias_file = "/home/jb/x10/x10_aliases"

address_aliases = aliases.Aliases( alias_file )
address_aliases.load()
address_aliases.check( all_possible_commands )


#################################
# code generation
#
# result is a list of 3 character X10 codes

# constants shared between parsing and code-gen

OP_IMM = "IMM"
OP_CMD = "CMD"
OP_REP = "REP"


def generate( syntax ):

	reader = ListReader( syntax )
	results = ListIO()

	def handle_rep( code ):
		results.append( code.op )

	def handle_addrs( code, addrs ):

		def optimize1( addr, next ):
			"return true if optimization is allowed"
			# the optimization is that the command following
			# each individual unit code may be omitted for
			# successive units that all share the same house code.
			# This does not apply to immediate operator types,
			# for which the trailing command is always omitted.
			return ( not OFlag.value
				and next
				and next[0] == addr[0]
				)
			
		reader = ListReader( addrs )		

		while 1:
			try:	addr = reader.next()
			except:	break
			results.append( addr )
			if code and not optimize1( addr, reader.peek()):
				results.append( addr[0] + code.op )

	def handle_cmd( code ):
		handle_addrs( code, code.addrs )

	def handle_imm( code ):
		results.append( code.op )
		handle_addrs( None, code.addrs )

	# table to call known op codes
	handle = { 
		OP_IMM:		handle_imm,
		OP_REP:		handle_rep,
		OP_CMD:		handle_cmd,
		}

	while 1:
		try:	
			code = reader.next()
		except IndexError:
			break

		handle[ code.type ]( code )

	return results


def setlevel( args ):
	pass

	
#################################
# argument processing

# syntax is { cmd { arg }}

class syntactic:
	"syntactic elements, shared between parser and generator"
	def __init__( self, type, op, addrs ):
		self.type = type
		self.op = op
		self.addrs = addrs

	def __str__( self ):
		return "syn( %s, %-3.3s, %s )" % ( self.type, self.op, `self.addrs` )


def parse( args ):

	args = ListReader( args )
	cmds = ListIO()

	## generate code

	def gen( code, arg, addrs=None ):
		"""generate a command"""
		if not addrs:
			addrs = []
		cmds.append( syntactic( code, arg, addrs ))

	def addaddr( addr ):
		"""append address arguments to most recently generated command"""
		if cmds:
			cmds.last().addrs.append( addr )
		else:
			log.err( "A command must preceed the first address" )

	## report syntax error
	
	def synerr( msg, args ):
		log.err( msg, args )
		raise SyntaxError

	## handle system command
	
	def do_system_cmd( arg, args ):
		if arg not in system_commands.keys():
			log.err( "Illegal command switch: %s", arg )
			return
		action = system_commands[ arg ].action
		if callable( action ):
			action( args )
		else:
			action.toggle()
				
	def is_address( arg ):
		return valid_address( arg ) or arg in address_aliases.keys()

	## parse regular command

	def parse_command( command, args ):
		cmd = command[:2].upper()
		if cmd not in x10_commands.keys():
			raise SyntaxError

		def parse_arg_none( cmd, args ):	# no arguments
			gen( OP_IMM, cmd )				# ?? house code

		def parse_arg_norm( cmd, args ):	# normal -- one or more unit codes
			gen( OP_CMD, cmd )

		def parse_arg_rep( cmd, args ):		# associated with an optional repeat code
			if numeric( args.peek()):
				gen( OP_REP, "R%02d" % int( args.next()))
			else:
				log.warn( "reusing previous repeat count with %s", command )
			gen( OP_CMD, cmd )

		def parse_arg_set( cmd, args ):		# special set macro command
			count = args.next()				# ?? house code
			if numeric( count ):
				units = []
				while args.peek() and is_address( args.peek()):
					units.append( args.next())

				# first we turn them all on
				# then we brighten them to the max
				# then we dim to the desired level.
				# address arguments are parsed once and reused twice.

				gen( OP_CMD, "ON" )
				for unit in units:
					parse_address( unit )

				gen( OP_REP, "R%02d" % 19 )
				gen( OP_CMD, "BR", cmds.last().addrs )
				
				gen( OP_REP, "R%02d" % int( count ))
				gen( OP_CMD, "DI", cmds.last().addrs )

			else:
				log.err( "missing level number for %s", command )
				return

		def parse_arg_raw( cmd, args ):
			while 1:
				arg = args.peek()
				if not arg or arg[0] == '-':
					break
				gen( OP_IMM, args.next())

		## ?? the next two X10 commands are not fully understood 
		## ?? nor is the code debugged:

		def parse_arg_pre( cmd, args ):		# special preset command/format
			count = args.next()				# ?? house code
			if numeric( count ):
				count = int( count )
				house = chr( ord( 'A' ) + ( count & 0xF ))
				gen( OP_IMM, ( house + "P%1d" ) % int( count >> 4 ))
			else:
				log.err( "missing preset number for %s", command )

		def parse_arg_arb( cmd, args ):		# arbitrary byte stream
			gen( OP_IMM, cmd )				# ?? house code
			while isarbnum( args.peek()):
				arb = arbnum( args.next())
				while arb.more():
					gen( OP_IMM, arb.next())

		parse_argop = {
			arg_none:	parse_arg_none,
			arg_norm:	parse_arg_norm,
			arg_rep:	parse_arg_rep,
			arg_set:	parse_arg_set,
			arg_arb:	parse_arg_arb,
			arg_pre:	parse_arg_pre,
			arg_raw:	parse_arg_raw,
			}

		argop = x10_commands[ cmd ].argop
		parse_argop[ argop ]( cmd, args )

	## parse unit code address

	def parse_address( addr ):

		# print "parse_address",addr

		if addr in address_aliases.keys():
			for alias in address_aliases[ addr ].split():
				parse_address( alias )
			return

		def parse_unit( unit ):
			if re.match( "^[0-9]+$", unit ):
				iunit = int( unit )
				if iunit in valid_unit_codes:
					return iunit
				else:
					log.err( "Invalid unit code in: %s", addr )
					raise SyntaxError
			else:
				raise SyntaxError

		house = addr[0].upper()
		unit = parse_unit( addr[1:])

		if house in valid_house_codes:
			addaddr( "%s%02d" % ( house, unit ))

		else:
			log.err( "Invalid house code: %s", addr )

	
	## parser main loop

	while 1:
		try:
			arg = args.next().lower()

			# this is where the code assumes that commands 
			# and address aliases are distinct:

			if is_address( arg ):				# must be address
				parse_address( arg )

			else:								# must be command
				if arg in command_synonyms.keys():
					arg = command_synonyms[ arg ]

				if arg[0] == '-':
					do_system_cmd( arg, args )
					continue

				parse_command( arg, args )
	
		except SyntaxError:
			log.err( "Not a valid command or address: %s", arg )

		except IndexError:		# StopIteration
			return cmds

#################################
# separate copy of parse_address -- allows external clients to:
#
#	(a) normalize addresses for sending to server
#	(b) share command aliases
#
# !! should be reconciled with parse.parse_address()

## parse unit code address

class ParseAddressError:
	def __init__( self, msg, *args ):
		self.msg = msg % args

def parse_address( addr ):

	# print "parse_address",addr

	if addr in address_aliases.keys():
		return parse_addresses( address_aliases[ addr ])

	if addr[1] == '*' and addr[0].upper() in valid_house_codes:
		return parse_addresses( form_bank_list( addr[0] ))

	def parse_unit( unit ):
		if re.match( "^[0-9]+$", unit ):
			iunit = int( unit )
			if iunit in valid_unit_codes:
				return iunit
		raise ParseAddressError( "Invalid unit code in: %s", addr )

	house = addr[0].upper()
	unit = parse_unit( addr[1:])

	if house in valid_house_codes:
		return "%s%02d" % ( house, unit )

	else:
		raise ParseAddressError( "Invalid house code in: %s", addr )

def parse_address_list( list ):
	return " ".join([ parse_address( addr ) for addr in list ])

def parse_addresses( addresses ):
	return parse_address_list( addresses.split())

def form_bank_list( house ):
	house = house.upper()
	return " ".join([ house + ( "%02d" % i ) 
						for i in valid_unit_codes ])

#################################
# streamlined parse and go 

def run( args ):

	log = logger.SLogger()

	intermediate = parse( sys.argv[ 1: ])

	if log.errors or not intermediate:
		return

	results = generate( intermediate )

	if log.errors or not results:
		return

	if SFlag.value:
		timetrack( execute, results )
	else:
		execute( results )


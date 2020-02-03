
import os, sys
from flags import *

ALLOW_ADVANCED = 0	# 1 iff hardware supports advanced commands

##############################
# command dictionaries
#
# command dictionaries map command names onto one or more related properties.
# one property in all cases is help text.

class defs:
	def __str__( self ):
		return "%s( %s, %s )" % ( self.name, `self.args`, self.help )

class cdef( defs ):
	def __init__( self, argop, help ):
		self.name = "cdef"
		self.argop = argop
		self.help = help

class sdef( defs ):
	def __init__( self, action, help ):
		self.name = "sdef"
		self.action = action
		self.help = help

# commands handle arguments in several different ways

arg_none = 0	# no arguments
arg_norm = 1	# normal -- one or more unit codes
arg_rep  = 2	# associated with an optional repeat code
arg_set  = 3	# special set macro command
arg_arb  = 4	# arbitrary byte stream
arg_pre  = 5	# special preset command/format
arg_raw	 = 6	# special RAW command/format

# these are the valid X10 commands

x10_commands = {
	"ON":	cdef( arg_norm, "units on" ),
	"OF":	cdef( arg_norm, "units off" ),
	"L0":	cdef( arg_none, "all lights off" ),
	"A0":	cdef( arg_none, "all units off" ),
	"L1":	cdef( arg_none, "all lights on" ),
	"DI":	cdef( arg_rep, "units dim" ),
	"BR":	cdef( arg_rep, "units brighten" ),

# special "macro" commands, unique to this implementation

	"SE":	cdef( arg_set, "Set illumination to a specific level (0-20)" ),
	"RA":	cdef( arg_raw, "Send arbitrary codes to the hardware (applies to all args following the op)." ),
	}

# advanced commands

if not ALLOW_ADVANCED:
	advanced_commands = {}
else:
	advanced_commands = {

	"HR":	cdef( arg_none, "hail REQ" ),
	"HA":	cdef( arg_none, "hail ACK *" ),
	"SR":	cdef( arg_norm, "Status REQ" ),
	"S1":	cdef( arg_none, "Status is on *" ),
	"S0":	cdef( arg_none, "Status is off *" ),
	"EC":	cdef( arg_arb, "extended code !!" ),	#any number of code bytes
	"ED":	cdef( arg_arb, "Extended Data !!" ),	#any number of data bytes
	# "P0":	cdef( arg_norm, "Preset dim #0" ),	#house code is low bits
	# "P1":	cdef( arg_norm, "Preset dim #1" ),	#house code is low bits
	"PR":	cdef( arg_pre, "Select preset level or scene (0..31)" ),
	}

# command line flags affect overall operation 

def forw_help( *args ):	help( args ) # link for circular references

system_commands = {
	"-h":	sdef( forw_help, "Print help message" ),
	"-t":	sdef( setrt, "Set reply timeout to next arg following" ),
	"-n":	sdef( NFlag, "NO action -- go through all motions but don't send commands" ),
	"-i":	sdef( IFlag, "show intermediate codes (implies -n)" ),
	"-g":	sdef( GFlag, "show Generated commands (implies -n)" ),
	"-o":	sdef( OFlag, "suppress optimizations" ),
	"-s":	sdef( SFlag, "print timing statistics" ),
	"-w":	sdef( WFlag, "monitor line and print codes" ),
	}

# we provide aliases for some of the more unusual spellings

command_synonyms =  {
	"alloff":	"A0", 
	"allon":	"L1", 
	"lightson":	"L1", 
	"lightsoff":	"L0", 
	"lon":		"L1", 
	"loff":		"L0", 
	"lights1":	"L1", 
	"lights0":	"L0",
	"BRight":	"BR",
	"OFf":		"OF",
	"DIm":		"DI",
	"SEt":		"SE",
	"setlevel":	"SE",
	"level":	"SE",
	"RAw":		"RA",
	"Preset":	"PR",
	"Scene":	"PR",
	"-help":	"-h",
	"--help":	"-h",
	"?":		"-h",
	"/?":		"-h",
	"/help":	"-h",
	"/h":		"-h",
	}

all_possible_commands = ( x10_commands.keys() 
					+ advanced_commands.keys()
					+ system_commands.keys() 
					+ command_synonyms.keys()
					)


#################################
# print help message

command_name = os.path.basename( sys.argv[0])

def help( dummy ):
	print "Command syntax is:", command_name, "{ command { unitcode }}"
	print

	def pr_cmds( title, commands, advanced=None ):
		print title
		for cmd, data in commands.items():
			if advanced == None or advanced == data.advanced:
				names = [ cmd ]
				for ali, syn in command_synonyms.items():
					if cmd == syn:
						names.append( ali )
				print "  ", ", ".join( names ), "--", data.help
		print

	pr_cmds( "Common commands:", x10_commands )
	if ALLOW_ADVANCED:
		pr_cmds( "Advanced commands:", advanced_commands )
	pr_cmds( "Internal commands:", system_commands )




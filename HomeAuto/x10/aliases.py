##################################
# maintain a list of unit code aliases

# address aliases is a flat map alias -> addresses
# the mapping may be recursive, though it is expanded
# upon reference, not here.

import re
from util import *

class Aliases:

	def __init__( self, filename=None ):
		self.filename = filename
		self.aliases = {}

	def keys( self ):
		return self.aliases.keys()

	def __len__( self ):
		return len( self.aliases )

	def __getitem__( self, key ):
		return self.aliases[ key ]

	def load( self, filename=None ):

		if filename:
			self.filename = filename

		file = open( self.filename )
		if not file:
			log.warn( "cannot open address alias file: %s", self.filename )

		for line in file.readlines():
			line = re.sub( "#.*", "", line )
			line = re.sub( "[ \t]+", " ", line )
			line = line.strip()

			if line:
				if "=" in line:
					name, alias = line.split( "=", 1 )
					name = name.strip().lower()
					alias = alias.strip().lower()
					self.aliases[ name ] = alias
					# print "alias", name, " = ", alias
					continue

				if "[" in line:
					continue	# ignore classes for now
								# ?? future: make them synonyms for all in class

				print "Syntax error in line:", line

		file.close()

	def check( self, commands ):
				
		## data integrity check: warn if aliases and commands overlap

		for alias in self.aliases.keys():
			if alias in commands:
				log.warn( "address alias conflicts with command: %s", alias )

		for addresses in self.aliases.values():
			addrs = addresses.split()
			for addr in addrs:
				if addr not in self.aliases.keys() \
				and not valid_address( addr ):
					log.warn( "address alias is undefined: %s", addr )
			


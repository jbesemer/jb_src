#!/usr/local/bin/python2.2

# tc -- figure transitive closure of python program
#
# follows includes to identify all modules involved.
#
# patterns:
#
#	sys.path.append(...)
#	import ...
#	from ... import ...
#

import os, sys, os.path
import re, string

ROOT_TAG = "[[ ROOT ]]"
INDENT = 4

SFlag = 0

RefsCache = {}	# cache of already scanned Refs(), indexed by pathname

def NewRef( pathname, mod=None ):
	if pathname not in RefsCache:
		RefsCache[ pathname ] = Refs( pathname )
	if mod:
		RefsCache[ pathname ].addMod( mod )
	return RefsCache[ pathname ]

class Refs:
	def __init__( self, pathname ):
		head, name = os.path.split( pathname )
		base, ext = os.path.splitext( name )
		if not head:
			head = "."
		self.pathname = pathname	# pathname for this module
		self.mname = base			# module name of this module
		self.names = []				# names included by this module
		self.syss = []				# system modules imported
		self.refs = {}				# non-sys modules imported 
		self.paths = [ head ]		# search paths for this module
		self.path = head			# path to this module
		self.scanned = 0			# true once file is scanned
		self.mods = []				# list of mods referencing this mod

	def basename( self ):
		return self.mname + ".py"

	def modname( self ):
		return self.mname

	def addPath( self, path ):
		if path not in self.paths:
			self.paths.append( path )

	def addSys( self, name ):
		if name not in self.syss:
			self.syss.append( name )

	def addRef( self, name, ref ):
		if name not in self.refs.keys():
			self.refs[ name ] = ref

	def addMod( self, name ):
		if name not in self.mods:
			self.mods.append( name )

	def addName( self, name ):
		if name not in self.names:
			self.names.append( name )

	def scanline( self, line ):
		line = line.strip()
		if len( line ) < 1 or line[0] == '#':
			return

		def act1( mat ):
			list = mat.group( 1 ).split( ',' )
			list = map( string.strip, list )
			for item in list:
				self.addName( item )

		def act2( mat ):
			path = mat.group( 1 )
			if len( path ) <= 2:
				return
			quote = path[0]
			assert( path[ -1 ] == quote )
			path = path[ 1 : -1 ]
			path = re.sub( quote + quote, "", path )
			self.addPath( path )

		def act3( mat ):
			self.addName( mat.group( 1 ))

		actpat = [
			[ act1,	"\s*import\s+(.*)" ],
			[ act2,	"\s*sys.path.append\(\s*(\S*)\s*\)" ],
			[ act3,	"\s*from\s+(\S+)\s+import" ],
			]

		for act, pat in actpat:
			mat = re.match( pat, line )
			if mat:
				act( mat )
				break

	def scan( self, pathname = None ):
		if self.scanned:
			return
		self.scanned = 1

		if not pathname:
			pathname = self.pathname

		src = file( pathname )
		for line in src:
			self.scanline( line )
		src.close()

		for name in self.names:
			filename = self.findPath( name )
			if filename:
				ref = NewRef( filename, self.modname())
				self.addRef( name, ref )
				ref.scan()
			else:
				self.addSys( name )

	def findPath( self, modname ):
		"find module path given mod name and present paths"
		for path in self.paths:
			prospect = os.path.join( path, modname + ".py" )
			if os.path.exists( prospect ):
				return prospect
		return None

	def report( self, expanded, indent = 0 ):
		print "%s%s in %s" % (
					" " * indent,
					self.modname(), 
					self.path )
		
		indent += INDENT

		if expanded.added( self ):

			if SFlag:
				for name in self.syss:
					print " " * indent, name, "in", "sys"

			for ref in self.refs.values():
				ref.report( expanded, indent )

	def __cmp__( self, other ):
		return cmp( self.modname(), other.modname())

	def __hash__( self ):
		return id( self )

class CheapSet( dict ):
	def added( self, value ):
		"add item to set and return true iff it WAS NOT there before hand"
		if value in self.keys():
			return 0
		self.__setitem__( value, 1 )
		return 1

def report( toplevel ):
	
	# print calling tree

	print "HIERARCHY:::\n"

	expanded = CheapSet()
	for ref in toplevel:
		ref.report( expanded )

	print "\fCLOSURE:::\n"

	# sort the names by modname

	refs = RefsCache.values()[:]
	refs.sort()
	
	# figure report field width, based on max name width, et al.

	wid = len( ROOT_TAG )
	for ref in refs:
		wid = max( wid, len( ref.modname()))
	wid += 2
	fmt = "%%-%ds" % wid
	fit = 80 / wid - 1

	# print the list

	for ref in refs:
		print fmt % ref.modname(), 
		n = 1
		if ref.mods:
			for name in ref.mods:
				if n % fit == 0:
					print "\n" + fmt % "",
				n += 1
				print fmt % name,
			print
		else:
			print fmt % ROOT_TAG

def main( names ):
	toplevel = [ NewRef( name ) for name in names ]
	for ref in toplevel:
		ref.scan()
	report( toplevel )

main( sys.argv[1:])





#####################################################
#

syspath = "/usr/local/lib/python2.2"

def isSysFile( basename ):
	def alt1( name ):	return os.path.join( syspath, name + ".py" )
	def alt2( name ):	return os.path.join( syspath, name )
	def alt3( name ):	return alt1( name ).lower()
	def alt4( name ):	return alt2( name ).lower()

	alternatives = [ alt1, alt2, alt3, alt4 ]

	for alt in alternatives:
		prospect = alt( basename )
		if os.path.exists( prospect ):
			return 1

	return 0
		


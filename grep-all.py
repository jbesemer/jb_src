#! /python24/python

import sys, os, os.path
import re

if 1:
	PATTERN = re.compile( "kPd_Descender" ) # , re.I )
else:
	if len( sys.argv ) <= 1:
		print "Syntax: grep-all pattern..."
		sys.exit(0)
	
	PATTERN = re.compile( "|".join([ re.escape( arg ) 
						for arg in sys.argv[1:]]), re.I )

if 1:		EXTENSIONS = re.compile( "\\.([cChH]|cpp)$" )
elif 0:	EXTENSIONS = re.compile( "\\.[hH]$" )
elif 0:	EXTENSIONS = re.compile( "\\.([cC]|cpp)$" )
else:		EXTENSIONS = None	# None meaning No restrictions, i.e., All files

DIRS = [ 
	"/powertv/explorer/os33/2200/target/include",
	"/Projects/Sherman/dev/Client/PowerTV/src/",
	"/Projects/Sherman/dev/Shared/Common/Include",
	"/Projects/Sherman/dev/Shared/Client",
	"/Projects/Sherman/dev/Shared/Tools",
	]

OLD_DIRS = [ 
	"/Projects/Sherman/dev",
	"/OpenTV/SDK30/include",
	"/OpenTV/SDK30/OTV_12/include",
	"/OpenTV/SDK30/OTV_EN/include",
	"/OpenTV/SDK30/OTV_EN2/include",
	"/OpenTV/SDK30/OTV_EN21/include",
	"/Projects/Sherman/dev/Client/OpenTV/src/",
	"/OpenTV/SDK30/include",
	]

def grep( path, name ):
	if ( name[ -1 ] == "~" 
	or name[ 0 ] == "." 
	or ( EXTENSIONS and not EXTENSIONS.search( name ))):
		return 0

	filename = os.path.join( path, name )
	first = lnum = matches = 0
	for line in file( filename ):
		lnum += 1
		if PATTERN.search( line ):
			if not first:
				print "+-", name, "- - "*10
				first = 1
			print ( "|  %05d:" % lnum ), line.rstrip()
			matches += 1
	return matches


def grep_all( path ):
	fileMatches = 0
	matches = 0

	for root, dirs, files in os.walk( path ):
		for file in files:
			count = grep( root, file )
			matches += count
			if count:
				fileMatches += 1
	return matches, fileMatches 

if __name__ == "__main__":
	Files = Matches = 0
	
	for DIR in DIRS:
		print "/===<", DIR
		matches, files = grep_all( DIR )
		print "\\===>", matches, "Lines,", files, "Files match in", DIR
		print
		Matches += matches
		Files += files
	
	print "### Total Matches:", Matches
	print "### Total Files:", Files
	print "\n[press Enter to exit]"

	sys.stdin.readline()	# pause the dos box

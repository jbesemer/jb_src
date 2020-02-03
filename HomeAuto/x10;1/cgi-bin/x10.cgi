#!/usr/bin/python

import sys, os, cgi
from string import *
import commands

DebugFlag = 0

X10_ROOT = "/home/jb/x10/"
X10_ALIASES = X10_ROOT + "x10_aliases"
CMD = "x10"

POST_PATH = None	# filled in at runtime

DEFAULT_CONFIG=[
	"master br 1		= d2",
	"master br 2		= d3",
	"living room overhead 	= b5",
	"living room sw 	= b4",
	"living room nw 	= b3",
	"living room se 	= b2",
	"living room 		= lr_chase lr_nw lr_se",
	"porch 			= b7",
	"hall			= b8",
	"bath1			= b9",
	"family room table	= f2",
	"family room standing	= f3",
	"family room all	= f2 f3",
	"jb_desk		= c1",
	"jb_fan			= c9",
	]

REPEATABLE=[ "Dim", "Brighten" ]	# commands which can be repeated

def print_boilerplate():
	print """Content-type: text/html\n

	<HTML>
	<HEAD>
	<H1>JB's X10 interface</H1>
	</HEAD>
	<BODY>
	Press buttons below to control X10s.
	<P>
	"""

	# <SCRIPT lang=JavaScript>
	# <!-- ... // --></SCRIPT>

def print_trailer():
	print "</BODY>"
	print "</HTML>"

def select_list( name, opts, selected ):
	res = '<SELECT name="' + name + '">\r\n'

	for opt in opts:
		if opt == selected:
			res = res + "<OPTION SELECTED>"
		else:
			res = res + "<OPTION>"
		res = res + opt + "\r\n"

	res = res + "</SELECT>\r\n"
	return res

HOUSE_OPTS = [ 
	"A", "B", "C", "D", "E", "F", "G", "H", 
	"I", "J", "K", "L", "M", "N", "O", "P" ]

CODE_OPTS = [ 
	"1", "2", "3", "4", "5", "6", "7", "8", 
	"9", "10", "11", "12", "13", "14", "15", "16" ]

def manual_selection( man_house, man_code ):
	return (
		select_list( "house", HOUSE_OPTS, man_house ) 
		+ select_list( "code", CODE_OPTS, man_code )
		)


def form_post_head( action ):
	return (
		'  <form method=POST action="' 
		+ action 
		+ '">'
		)

def input_submit( name, value ):
	return ( 
		'<input type=submit name="' 
		+ str( name ) 
		+ '" value="' 
		+ str( value ) 
		+ '">' 
		)

def input_text( name, value="1", size=4 ):
	return (
		'<input type=text name="' 
		+ str( name ) 
		+ '" value="' 
		+ str( value ) 
		+ '" size=' 
		+ str( size ) 
		+ ">"
		)

def standard_buttons( name ):
	return ( 
		"\n          "
		+ input_submit( "x10", "On" )
		+ "\n          "
		+ input_submit( "x10", "Off" )
		+ "\n          "
		+ input_submit( "x10", "Dim" )
		+ "\n          "
		+ input_submit( "x10", "Brighten" )
		+ "\n          "
		+ input_text( "repeat", value="1" )
		+ "\n      "
		)

	#	+ " times" 

def print_table( list_of_rows ):

	print "<TABLE>"		#  width=98% rules=all border=2>"

	# heading row
	for headrows in list_of_rows[0:2]:
		print "  <TR bgcolor=#e0e0e0>"
		for heading in headrows:
			print "    <TD>" + heading + "</TD>"
		print "  </TR>"

	# other rows (actually pairs of rows)
	even = 1
	for row in list_of_rows[2:]:

		print form_post_head( POST_PATH + "/" + row[0][0])

		if even:
			print "    <TR bgcolor=#D0FFD0>"
		else:
			print "    <TR>"

		for col in row[0]:
			print "      <TD>" + col + "</TD>"

		print "    </TR>"

		if even:
			print "    <TR bgcolor=#D0FFD0>"
		else:
			print "    <TR>"

		for col in row[1]:
			print "      <TD>" + col + "</TD>"

		print "    </TR>"
		print "  </form>"

		even = ( even + 1 ) % 2

	print "</TABLE>"

def build_table( filename, man_house, man_code ):
	try:
		file = open( filename, "r" )
		lines = file.readlines()
	except:
		lines = DEFAULT_CONFIG

	lines = map( strip, lines )
	table = [["Name","Definition"], [ "State", "Actions"]]

	for line in lines:

		# remove comment, if any

		comment = ""
		i = find( line, "#" )
		if i >= 0:
			comment = line[i:]
			line = line[0:i]

		# split into rhs, lhs

		i = find( line, "=" )
		if i > 0:
			(lhs, rhs) = split( line, "=", 1 )
			lhs = strip( lhs )
			rhs = strip( rhs )
			table.append(([ lhs, rhs ],
					[ "", standard_buttons( lhs )]))
	table.append(([ "Manual selection", 
				manual_selection( man_house, man_code )],
			[ "", standard_buttons( "manual" )]))

	return table

# other way: 
# <INPUT type=BUTTON value=label onClick="window.location='http://...'">

##################
# main program
##################

# print html prefix, to ensure debug and exception output will be visible

print_boilerplate()

# try the normal actions

try:
	# parse input

	Form = cgi.FieldStorage()

	POST_PATH = os.environ[ "SCRIPT_NAME" ]

	try:
		man_house = Form['house'].value 
		man_code = Form['code'].value
	except:
		man_house = 'A'
		man_code = '1'

	# display the form

	print_table( build_table( X10_ALIASES, man_house, man_code ))
	print "<P>Press any above buttons to send X10 commands"
	print_trailer()

	# process commands

	if os.environ.has_key( "PATH_INFO" ):
		target = os.environ[ "PATH_INFO" ]

		if len( target ) > 1:
			target = target[1:]
			if target == 'Manual':
				target = man_house + man_code
			cmd = Form[ 'x10' ].value
			rep = Form[ 'repeat' ].value
			if cmd in REPEATABLE:
				cmd = cmd + " " + rep

			cmd = join([ X10_ROOT + CMD, cmd, target ], " " )

			print "<hr><H3>Executing: </H3><pre>"
			print cmd, "</pre><P>"

			print "<H3>Results:</H3><PRE>"
			print commands.getoutput( cmd )
			print "</pre>"


# if something goes wrong, display the traceback

except:
	import traceback
	print "<hr><H1>Exception raised:</H1>\n<pre>\n"
	sys.stderr = sys.stdout
	traceback.print_exc()
	print "\n</pre>"

# echo cgi inputs if debug is on 

if DebugFlag:
	print "<hr><H2>Debug Output:</H2><P>"
	cgi.print_form( Form )
	cgi.print_environ( os.environ )


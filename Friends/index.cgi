#!/usr/local/bin/python

import os, os.path
import sys
import cgi
import cgitb; cgitb.enable()
import time

import Friends
import Report
import Password

##############################################
# CGI boilerplate

DEBUG = False
TITLE = """JB's SL Friends Online"""

print "Content-type: text/html; charset=iso-8859-1\n"
print """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head>
<title>%s</title>
</head>
<body bgcolor="#fffff0">
<pre>""" % TITLE

# <link type="text/css" rel="stylesheet" href=\"""" + STYLE + """">

Form = cgi.FieldStorage()

DEBUG |= ( "DEBUG" in Form ) and ( Form.getlist("DEBUG")[0] in [ "TRUE", "YES", "ON", "ENABLED",  "1" ])

##############################################
# Definitions

def LogfilePath( filename ):
	return os.path.join( Friends.LOG_FOLDER, filename )

ReportFilenames = [ name for name in os.listdir( Friends.LOG_FOLDER )
		if os.path.isfile( LogfilePath( name ))
			and "-" in name and "." not in name ]
ReportFilenames.sort()
ReportFilenames.reverse()

if "date" in Form:
	SelectedFilename = Form[ "date" ].value
	if SelectedFilename not in ReportFilenames:
		SelectedFilename = ReportFilenames[ 0 ]
else:
	SelectedFilename = ReportFilenames[ 0 ]

def FilenameAsHTML( name ):
	if name == SelectedFilename:
		name = "<b>" + name + "</b>"
	else:
		name = '<a href="index.cgi?date=%s">%s</a>' % ( name, name )
	return "<tr><td>%s</td><tr>" % name

ReportFilenamesAsHTML = """<table>
<tr><th>Other Dates</th></tr>
""" + "\n".join([ FilenameAsHTML( name ) 
			for name in ReportFilenames 
				if name != SelectedFilename ]) + """
</table>
"""



def PrintSummary( filename, friendsOnline ):
	if filename == ReportFilenames[ 0 ]:
		( Report.Summary( LogfilePath( filename ),
				friendsOnline )	
		).PrHTML()
	else:
		Report.Summary( LogfilePath( filename )) .PrHTML()

##############################################
# Mainline

try:
	from Password import PASSWORD
	password = PASSWORD

except OSError:
	print "Warning: no password file"
	
else:
	answer = Friends.GetFriends( password )

	print "</pre>"
	print "<H1>", TITLE, "</H1>"

	#print "<h2>Friends Currently Online</h2>"
	print "<h2>", time.ctime(), "</h2>"
	print answer.GetNamesAsHTML()
	print "<h2>Friends' Online History %s</h2>" % SelectedFilename

	print "<table>"
	print "<tr><td valign=top>"
	print ReportFilenamesAsHTML
	print "</td><td valign=top>"
	PrintSummary( SelectedFilename, answer.GetNames())
	print "</td></tr>"

	print "</table>"
	print "</body>"
	print "</html>"

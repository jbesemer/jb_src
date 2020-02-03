#!c:/python24/python.exe

##
##  Genie -- portal to family Genealogy database
##

import os, sys
import cgi
import cgitb; cgitb.enable()
import time

import HTML
import GenieDB

# constants

NBSP = "&nbsp;"

COLOR_BG = "#98fb98"
COLOR_HI = "#fffacd"
COLOR_A = "#fff8dc"
COLOR_B = "#f0fff0"

# conditional constants

SELF = os.environ.get( "SCRIPT_NAME", "/cgi-bin/Genie" )
STYLE = "/Genie.css"
PATH_INFO = os.environ.get( "PATH_INFO", "" )
DEBUG = os.environ.get( "DEBUG", "0" ).upper() in [ "TRUE", "YES", "ON", "ENABLED",  "1" ]
IMAGE = "/icons/"

##############################################
# CGI boilerplate

TITLE = """<b><big>Genie -- </big>A Simple Genealogy Wiki</b>"""

print "Content-type: text/html; charset=iso-8859-1\n"
print """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head>
<title>Genie -- A Simple Genealogy Wiki</title>
<link type="text/css" rel="stylesheet" href=\"""" + STYLE + """">
</head>
<body bgcolor="#fffff0">
<pre>"""

Form = cgi.FieldStorage()

DEBUG |= ( "DEBUG" in Form ) and ( Form.getlist("DEBUG")[0] in [ "TRUE", "YES", "ON", "ENABLED",  "1" ])


##############################################
# command handlers...
##############################################

def HandleSearch( name=""):
	print """
<form>
	<input type=text name="name" width="40" value="%s">
	<input type=SUBMIT name="Search" value="Search for Names">
</form>
""" % name

SEXMAP = {
	"M": "Male",
	"F": "Female",
	"?": "", 
	}

def PersonAsLink( person ):
	return '<a href="%s?id=%s">%s</a>'% ( SELF, person[ "idPerson" ], person[ "name" ])
	
def PrependIfNonNull( s, item="&nbsp;&nbsp;&nbsp;&nbsp; " ):
	if s:
		return item + s
	else:
		return ""

def EditButton( href="", title="" ):
	return """[<a href="%s" title="%s">edit</a>]""" % ( href, title )
	# return """<div class="editsection" style="float:left;margin-right:5em;">[<a href="%s" title="%s">edit</a>]</div>""" % ( href, title )

	
def HandleID( id ):
	if not id:
		return HandleSearch()
		
	people = GenieDB.GetPersonByID( id ).GetData()
	
	if len( people ) > 1:		HandlePeople( people )
	elif len( people ) == 0:	print "Cannot find individual with id=", id
	else:
		person = people[ 0 ]
		parents, unions = GenieDB.GetRelated( person[ "idPerson" ])
		print "<h2>", person[ "name" ], "</h2>"
		
		print "<b><i>Born:</i></b>", person[ "BirthDate" ], PrependIfNonNull( person[ "BirthPlace" ])
		if person[ "DeathDate" ]:
			print "<br><b><i>Died:</i></b>", person[ "DeathDate" ], PrependIfNonNull( person[ "DeathPlace" ])
		print "<p><ul>"
		print EditButton()
		print "</ul>"
		
		print "<h3>Parents</h3>"
		print "<ul>"
		for parent in parents.GetData():
			print "<li>", PersonAsLink( parent ), "</li>"
		print "<p>"	
		print EditButton()
		print "</ul>"
		
		print "<h3>Unions and Offspring</h3>"
		print "<ul>"
		for union in unions.GetData():
			if union:
				print "<li>"
				#print "Married", 
				print PersonAsLink( union )
				print PrependIfNonNull( union[ "StartDate" ])
				print PrependIfNonNull( union[ "Location" ])

				children =  GenieDB.GetOffspringByUnionID( union[ "idUnion" ]).GetData()
				if children:
					print "<p><table>"
					
					for child in children:
						print "<tr><td>&#186;&nbsp;&nbsp; ", PersonAsLink( child ), "</td><td>"
						if child[ "BirthDate" ]:
							print child[ "BirthDate" ]
						print "</td><td>"
						if child[ "BirthPlace" ]:
							print child[ "BirthPlace" ]
						print "</td></tr>"
					print "</table>"
				print "</li>"
				print "<p>", EditButton()
		print "</ul>"
		
		print "<br><br><br>"
		print "<i>Sex: %s,&nbsp;&nbsp;&nbsp;&nbsp; Database ID: %s</i>" % (
			SEXMAP[ person[ "sex" ]], person[ "idPerson" ])


	
def HandleName( name ):
	HandleSearch( name )

	print "<h2>Search Results</h2>"
	HandlePeople( GenieDB.GetPeopleByName( name ).GetData())

def HandlePeople( people ):
	if people:
		print "<ul>"
		for person in people:
			print """<li>
				<a href=%s?id=%s>%s</a>
				</li>""" % ( SELF, person[ "idPerson" ], person[ "name" ])
		print "</ul>"
	else:
		print "No matching names were found; revise the name and search again."
	

###############################################
# now see if we have specific commands or just the main page

print "</pre>" 
print """<h1>Genie -- A Simple Genaology
<a href="http://en.wikipedia.org/wiki/Wiki">Wiki</a>
Page</h1>
<hr>"""
	
if 'id' in Form:
	ids = Form[ "id" ].value
	if isinstance( ids, list ):
		for id in ids:
			HandleID( id )
	else:
		HandleID( ids )
	
elif 'name' in Form:
	names = Form[ "name" ].value
	if isinstance( names, list ):
		for name in names:
			HandleName( name )
	else:
		HandleName( names )
	
	
else:
	HandleSearch()
	

# Db.close()

#########################################
# CGI postscript / cleanup


# debug info

if 0 or DEBUG:
	cgi.print_form( Form )
	if 1:
		cgi.print_environ()
	else:
		cgi.print_environ_usage()

# Trailer boilerplate

if 1:
	print "<br>"
	print "<br>"
	print "<br>"
	print "<br>"
	print "<br>"

	print "<hr>"
	print "<i>Credits:</i>"
	print "<table><tr valign=top>"
	print "<td>"			##############################
	
	print '<a href="http://cascade-sys.com/~jb">'
	print '<table valign=top frame=border border=3 cellpadding=0 rules=none><tr valign=middle><td>'
	print '<img src="/icons/gear1">'
	print '</td></tr><tr valign=middle><td>'
	print "<small><i>JB.OnIdle()</i></small>"
	print '</td></tr></table>'
	print "</a>"

	print "</td><td>"		##############################

	print '<a href="http://www.mysql.org">'
	print '<img src="/icons/mysql5-100">'
	print "</a>"
	
	print "</td><td>"		##############################

	print '<a href="http://www.apache.org"><img src="/icons/apache_pb2_ani"></a>'
	
	print "</td><td>"		##############################
	
	print '<a href="http://www.python.org"><img src="/icons/PythonPoweredAnimSmall"></a>'
	
	print "</td>"			##############################
	print "</tr></table>"
	
	
	
	print "</body></html>"
	
def GenAlternating( a, b ):
	while True:
		yield a
		yield b


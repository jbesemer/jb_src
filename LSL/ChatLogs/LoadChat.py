#! env python

import os, os.path
import re
import MySQLdb
import SqlSelect

IM_LINE = "\\[(\\d\\d\\d\\d/\\d\\d/\\d\\d\\s\\d?\\d:\\d\\d)\\]\\s+(.*)$"
RE = re.compile( IM_LINE )

QUOTE_TEXT = "(['\"\\\\])"
QUOTE_REPL = "\\\\\\1"

class MyDb:
	"""database class for visitors"""

	# Kludge to extract date and time, given old (3.x) version of MySQL installed on cascade2

	DateKey = "date_format(`timestamp`,'%Y-%m-%d')"
	TimeKey = "date_format(`timestamp`,'%H-%i-%s')"

	def __init__( self ):
		self.Db = MySQLdb.Connect(
			db="SL CHAT LOG",
			user="jb",
			passwd="Reject0")

		self.DatesVisitors = None

		self.LoadNameCache()

	def Commit( self ):
		self.Db.commit()

	def Cursor( self ):
		return self.Db.cursor()

	def Execute( self, query ):
		cursor = self.Cursor()
		# print query
		cursor.execute( str( query ))	# convert Select objects to string (strings are unaffected)
		return cursor

	def ExecuteAndFetch( self, query ):
		return self.Execute( query ).fetchall()

	def LoadNameCache( self ):
		self.NameCache = {}
		for row in self.ExecuteAndFetch( "select name,id from names" ):
			self.NameCache[ row[ 0 ]] = int( row[ 1 ])

	MAX_NAME_LEN = 88

	def GetId( self, name ):
		if len( name ) >= self.MAX_NAME_LEN:
			print "### TOO LONG NAME:", 	name
			name = name[ :self.MAX_NAME_LEN ]

		try:
			return self.NameCache[ name ]
		except KeyError:
			cur = self.Execute( "INSERT INTO names SET Name='%s'" % self.FmtText( name ))
			self.Commit()
			# print "Adding", name, cur.lastrowid
			self.NameCache[ name ] = cur.lastrowid
			return cur.lastrowid

	def FmtDate( self, s ):
		return s.replace("/","-") + ":00"

	def FmtText( self, s ):
		return re.sub( QUOTE_TEXT, QUOTE_REPL, s )

	def FmtName( self, flags, name ):
		m = re.search( "(\s+shouts)$", name )
		if m:
			return flags|1, name[ :m.end(1)]

		m = re.search( "(\s+whispers)$", name )
		if m:
			return flags|2, name[ :m.end(1)]

		return flags, name

	def AddLine( self, table, time, text ):
		flags, speaker, text = self.ProcessSpecialForms( text )
		flags, speaker = self.FmtName( flags, speaker )

		self.Execute(
			"INSERT INTO `%s` " % table
			+ "SET Name=%d," % self.GetId( speaker )
			+ "Timestamp='%s'," % self.FmtDate( time )
			+ "Text='%s'," % self.FmtText( text )
			+ "Flags=%d" % flags )
		self.Commit()

	STRINGS = [
		"Connecting to in-world Voice Chat",
		"Connected",
		"Disconnected from in-world Voice Chat",
		"Teleport completed",
		"Insufficient permissions",
		"The system is currently unable to process your request",
		"You decline ",
		"VISTA ANIMATION SUPA VALUE FEM",
		"VISTA DIVINE GIRL AO",
		"Notecard Giver owned by",
		"Cake AO - Casual Set",
		"Abranimations - Kick Butt Animator",
		]

	def ProcessSpecialForms( self, text ):
		m = re.match( "(\\S+\\s+\\S+)\\s+(is Online|is Offline)$", text )
		if m:
			return 10, m.group(1), m.group(2)

		m = re.match( "(A group member named )?(\\S+\\s+\\S+)\\s+(gave you.*)", text )
		if m:
			return 12, m.group(2), text

		for s in self.STRINGS:
			if re.match( s, text ):
				return 13, "System", text

		m = re.match( "([^:]+):\\s+(.*)$", text )
		if m:
			return 0, m.group(1), m.group(2)

		m = re.match( "(\\S+\\s+\\S+)\\s+(.*)$", text )
		if m:
			return 0, m.group(1), m.group(2)

		return 1024, "Unknown", text


Db = MyDb()

def Main( arg ):
	path,name = os.path.split( arg )
	table,ext = os.path.splitext( name )
	print "Importing:", table

	for line in file( arg ):
		if not line.strip() or line[0] != "[":
			continue

		m = RE.match( line )
		if m:
			Db.AddLine( table, m.group(1), m.group(2))

		else:
			print "## no match:", line

if __name__ == "__main__":
	import sys

	for arg in sys.argv[ 1: ]:
		Main( arg )
#! env python

import os, os.path
import re
import MySQLdb
import SqlSelect

IM_LINE = "\\[([0-9 /-:]+)\\]\\s*([^\\s]+\\s+[^\\s:]*):?\\s*(.*)$"
RE = re.compile( IM_LINE )

QUOTE_TEXT = "(['\"])"
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

	def GetId( self, name ):
		try:
			return self.NameCache[ name ]
		except KeyError:
			cur = self.Execute( "INSERT INTO names SET Name='%s'" % name )
			self.Commit()
			print "Adding", name, cur.lastrowid
			self.NameCache[ name ] = cur.lastrowid
			return cur.lastrowid

	def FmtDate( self, s ):
		return s.replace("/","-") + ":00"

	def FmtText( self, s ):
		return re.sub( QUOTE_TEXT, QUOTE_REPL, s )

	def AddLine( self, table, time, speaker, text ):
		self.Execute(
			"INSERT INTO `%s` " % table
			+ "SET Name=%d," % self.GetId( speaker )
			+ "Timestamp='%s'," % self.FmtDate( time )
			+ "Words='%s'" % self.FmtText( text ))
		self.Commit()


Db = MyDb()

def Main( arg ):
	path,name = os.path.split( arg )
	table,ext = os.path.splitext( name )
	print "Importing:", table


	for line in file( arg ):
		m = RE.match( line )
		if m:
			Db.AddLine( table, m.group(1), m.group(2), m.group(3))

		else:
			print "## no match:", line






if __name__ == "__main__":
	import sys

	for arg in sys.argv[ 1: ]:
		Main( arg )
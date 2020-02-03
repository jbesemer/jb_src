#!/usr/bin/python2.2

import sys, os, cgi
import cgitb; cgitb.enable()
from string import *
import commands
import MySQLdb
import time

DebugFlag = 0

class Select:
	def __init__( self, table="", columns="", where="", order="", group="" ):
		self.table = table
		self.columns = columns
		self.where = where
		self.order = order
		self.group = group
		
	def __str__( self ):
		return ("SELECT "
			+	self.GetColumns()
			+	self.GetTable()
			+	self.GetWhere()
			+	self.GetGroup()
			+	self.GetOrder())

	def GetColumns( self ):
		return self.columns
		
	def GetTable( self ):
		return " FROM " + self.table
		
	def GetWhere( self ):
		if self.where:
			return " WHERE " + self.where
		else:
			return ""
			
	def GetOrder( self ):
		if self.order:
			return " ORDER BY " + self.order
		else:
			return ""
			
	def GetGroup( self ):
		if self.group:
			return " GROUP BY " + self.group
		else:
			return ""
			
	def AddWhereClause( self, where ):
		if self.where:
			self.where += " AND " + where
		else:
			self.where = where
				
class MyDb:
	"""database class for visitors"""
	
	# Kludge to extract date and time, given old (3.x) version of MySQL installed on cascade2

	DateKey = "date_format(`timestamp`,'%Y-%m-%d')"
	TimeKey = "date_format(`timestamp`,'%H-%i-%s')"

	def __init__( self ):
		self.Db = MySQLdb.Connect(
			db="avatars",
			user="WWW",
			passwd="WWW")
			
		self.DatesVisitors = None

	def Cursor( self ): 
		return self.Db.cursor()
		
	def Execute( self, query ):
		cursor = self.Cursor()
		# print query
		cursor.execute( str( query ))	# convert Select objects to string (strings are unaffected)
		return cursor
		
	def ExecuteAndFetch( self, query ):
		return self.Execute( query ).fetchall()

	def RecordEvent( self, time, event ):
		"""record an event"""

		return self.Execute( 
			"""Insert into events (timestamp,timecode,description) 
				VALUES( '%s', '%s', '%s' );"""
				% ( ParseDate( time ), time, event ))

	def RecordMemory( self, time, memory ):
		"""record a memory event"""

		return self.RecordEvent( time, "memory = %s" % memory )
				

	def RecordUpdate( self, name, online, time ):
		# name, online, time = storage.value.split(",")

		return self.Execute( 
			"""Insert into log (timestamp,timecode,name,online) 
				VALUES( '%s', '%s', '%s', %s );"""
				% ( ParseDate( time ), time, name, online))
				
	def RecordKeysUpdate( self, time, uuid, name ):

		return self.Execute( 
			"""Insert into avatars (uuid,timestamp,timecode,name) 
				VALUES( '%s', '%s', '%s', '%s' );"""
				% ( uuid, ParseDate( time ), time, name ))
				
	def ShowDatesAndVisitors( self ):
		# construct table for all possible dates
		#	(and fill in default date range for second table)

		print "<TABLE rules=all cellpadding=3 border=2>"

		print "<TR><TH>Date</TH><TH>#Visitors</TH></TR>"
		for row in self.FetchDatesAndVisitors():
			date = row[0]
			print "<TR>", 
			print "<TR><TD>", 
			print "<a href=http://cascade-sys.com/cgi-bin/visitor.cgi?date=%s>" % date
			print date, 
			print "</a>"
			print "</TD>"
			print "<TD>", row[1], "</TD></TR>"

		print "</TABLE>"
		
	def ShowSelectedDetails( self, startDate,  endDate ):
		# construct table for selected range

		print "<TABLE rules=all cellpadding=3 border=2>"
		print "<TR><TH>When</TH><TH>Sensor</TH><TH>Name</TH><TH>Action</TH><TH>Duration</TH></TR>"

		ArrivalTimes = {}
		
		for row in self.FetchRange( startDate, endDate ):
			if row[3] == "Arrival":
				ArrivalTimes[ row[2]] = row[0]
			elif row[3] == "Departure":
				try:
					delta = ComputeDuration( ArrivalTimes[ row[2]], row[0])
					row = row + ( delta, )
				except KeyError:
					pass
				
			s = "<TR>"
			for col in row:
				s += "<TD>" + str( col ) + "</TD>"
			s += "</TR>"
			print s

		print "</TABLE>"
		
	def ShowHistory( self, startDate,  endDate ):
		print "<h1>Visitor Log</h1>"		# print "<h1>Hiro's Visitors</h1>"

		# table header for joining following two tables

		print "<TABLE rules=all cellpadding=3 border=2>"
		print "<TR><TD valign=top>"
		
		self.ShowDatesAndVisitors()

		# glue for joining two tables

		print "</TD><TD valign=top>"

		self.ShowSelectedDetails( startDate,  endDate )

		# table trailer for joining above two tables

		print "</TD></TR>"
		print "</TABLE>"

	def FetchRange( self, startDate, endDate ):
		query = Select( 
			"log", 
			"timestamp,sensor,name,action", 
			order="timestamp" )
		self.AddDateRange( query, startDate,  endDate )
		# print query
		return self.ExecuteAndFetch( str( query ))
				
	def FetchDatesAndVisitors( self ):
		if not self.DatesVisitors:
			self.DatesVisitors \
				= self.ExecuteAndFetch( 
						Select( 
							table="log",
							columns =  self.DateKey + ",count(action='Arrival')",
							group=self.DateKey,
							order=self.DateKey))
			
		return self.DatesVisitors
		
	def GetLastDate( self ):
		return self.FetchDatesAndVisitors()[-1][0]
		
	def AddDateRange( self, query, startDate,  endDate ):		
		if not endDate:
			if startDate:
				query.AddWhereClause( """ %s = '%s' """ % ( self.DateKey, startDate ))
			else:
				query.AddWhereClause( """ %s = '%s'""" % ( self.DateKey, self.GetLastDate()))
		else:
			if startDate:
				query.AddWhereClause( """ `timestamp` >= '%s' """ % startDate )
			if endDate:
				query.AddWhereClause( """ `timestamp` <= '%s' """ % endDate )
		

def ParseTime( t ):
	"""convert MySQL datetime to seconds since midnight"""
	
	date,t = str( t ).split(" ")
	t,ignore = t.split(".")
	hh,mm,ss = t.split(":")
	
	return int( ss ) + 60 * int( mm ) + 3600 * int( hh )
	
def ComputeDuration( arrival, departure ):
	try:
		a = ParseTime( arrival )
		d = ParseTime( departure )
	except:
		return "?"
		
	delta = d - a

	while( delta < 0 ):
		delta += 3600 * 24

	if delta < 60:
		return str( delta ) + " sec"
	
	if delta < 3600:
		return "%4.1f min" % ( delta / 60.0 )
		
	return "%4.2f hrs" % ( delta / 3600.0 )
	
	
def ParseDate( timestamp ):
	timestamp = str( timestamp )

	if "." in timestamp:
		timestamp, ms = timestamp.split( "." )
		
	if not timestamp:
		return ""

	if "T" in timestamp:
		date, time = timestamp.split( "T" )
	elif " " in timestamp:
		date, time = timestamp.split( " " )
	else:
		return timestamp

	return date + " " + time


class MyFieldStorage( cgi.FieldStorage ):
	""" Extend Field Storage"""
	
	def __init__( self ):
		cgi.FieldStorage.__init__( self )
		
	def IsEventQuery( self ):
		return self.has_key( 'event' )
			
	def IsUpdateQuery( self ):
		return self.has_key( 'u' )
			
	def IsUpdateKeysQuery( self ):
		return self.has_key( 'k' )
			
	def IsMemoryQuery( self ):
		return self.has_key( 'memory' )
			
	def IsDebugMode( self ): 
		return self.has_key( "debug" ) and self[ 'debug' ].value
			

if __name__ == "__main__":
	
	RollCredits = 0
	
	# print html prefix, to ensure debug and exception output will be visible

	print """Content-type: text/html\n

	<HTML>
	<HEAD>
	</HEAD>
	<BODY>
	"""

	try:
		Db = MyDb()
		Form = MyFieldStorage()

		if Form.IsMemoryQuery():
			# Db.RecordMemory( Form["time"].value, Form["memory"].value )
			print "OK"
			
		if Form.IsEventQuery():
			Db.RecordEvent( Form["time"].value, Form["event"].value )
			print "OK"

		elif Form.IsUpdateQuery():
			u = Form[ "u" ]
			if isinstance( u, list ):
				for uu in u:
					name, online, time = uu.value.split(",")
					Db.RecordUpdate( name, online, time )
			else:
				name, online, time = u.value.split(",")
				Db.RecordUpdate( name, online, time )
			print "OK"
			
		elif Form.IsUpdateKeysQuery():
			ts = Form["time"].value
			k = Form[ "k" ]
			if isinstance( k, list ):
				for kk in k:
					name,uuid = kk.value.split(",")
					Db.RecordKeysUpdate( ts, uuid, name )
			else:
					name,uuid = k.value.split(",")
					Db.RecordKeysUpdate( ts, uuid, name )
			print "OK"

		else:
			# Db.ShowHistory( Form.GetStart(), Form.GetEnd())
			RollCredits = 1

	# if something goes wrong, display the traceback

	except:
		import traceback
		#print "<hr><H1>Exception raised:</H1>\n<pre>\n"
		sys.stderr = sys.stdout
		traceback.print_exc()
		print "\n</pre>"

	# echo cgi inputs if debug is on 

	if DebugFlag or Form.IsDebugMode():
		print "<hr><H2>Debug Output:</H2><P>"
		cgi.print_form( Form )
		cgi.print_environ( os.environ )

	# Roll Credits

	if RollCredits:
		print "<br>"
		print "<br>"
		print "<br>"
		
		print "<hr>"
		print "<i>", time.ctime(), "</i>"
		print "<table><tr valign=top>"
		print "<td>"			##############################
		
		print '<a href="http://cascade-sys.com/~jb">'
		print '<table valign=top frame=border border=3 cellpadding=0 rules=none><tr valign=middle><td>'
		print '<img src="/icons/gear1.gif">'
		print '</td></tr><tr valign=middle><td>'
		print "<small><i>JB.OnIdle()</i></small>"
		print '</td></tr></table>'
		print "</a>"


		if 1 :
			print "</td><td>"		##############################
			print '<a href="http://www.mysql.org">'
			print '<img src="/icons/mysql5-100.gif">'
			print "</a>"
			

		if 1 :
			print "</td><td>"		##############################
			print '<a href="http://www.apache.org"><img src="/icons/apache_pb2_ani.gif"></a>'
		
		if 1 :
			print "</td><td>"		##############################
			
			print '<a href="http://www.python.org"><img src="/icons/PythonPoweredAnimSmall.gif"></a>'
		
		print "</td>"			##############################
		print "</tr></table>"

	# Trailer

	print "</body></html>"


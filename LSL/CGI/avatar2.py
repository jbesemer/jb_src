#!/usr/bin/python2.2

import sys, os, cgi
import cgitb; cgitb.enable()
from string import *
import commands
import MySQLdb
import time

DebugFlag = 0

URL = "http://cascade-sys.com/cgi-bin/avatar.cgi"

COLOR_SELECTED = "#FAFAD2"
COLOR_UNSELECTED = "#FFFFFF"

def SelectedColor( q1, q2 ):
	if int( q1 ) == int( q2 ):
		return COLOR_SELECTED
	else:
		return COLOR_UNSELECTED
	
MONTH_NAME = {
	1:	"January",
	2:	"February",
	3:	"March",
	4:	"April",
	5:	"May",
	6:	"June",
	7:	"July",
	8:	"August",
	9:	"September",
	10:	"October",
	11:	"November",
	12:	"December",
	}

class Select:
	def __init__( self, columns="", table="", where="", order="", group="", on="" ):
		self.columns = columns
		self.table = table
		self.where = where
		self.order = order
		self.group = group
		self.on = on

	def __str__( self ):
		return ("SELECT "
			+	self.GetColumns()
			+	self.GetFrom()
			+	self.GetOn()
			+	self.GetWhere()
			+	self.GetGroup()
			+	self.GetOrder())

	def GetColumns( self ):
		if not self.columns:
			return " * "
		else:
			return JoinIfList( self.columns )
		
	def GetFrom( self ):
		return " FROM " + self.JoinIfList( self.table )
		
	def GetWhere( self ):
		if self.where:
			return " WHERE " + self.JoinIfList( self.where, " AND " )
		else:
			return ""
			
	def GetOn( self ):
		if self.on:
			return " ON " + self.JoinIfList( self.on, " AND " )
		else:
			return ""
			
	def GetOrder( self ):
		if self.order:
			return " ORDER BY " + self.JoinIfList( self.order )
		else:
			return ""
			
	def GetGroup( self ):
		if self.group:
			return " GROUP BY " + self.JoinIfList( self.group )
		else:
			return ""
			
	def AddWhereClause( self, where ):
		if self.where:
			if isinstance( item, list ):
				self.where += [ where ]
			else:
				self.where += " AND " + where
		else:
			self.where = where
				
	def JoinIfList( self, item, sep="," ):
		if isinstance( item, list ):
			return sep.join( item )
		else:
			return item

class MyDb:
	"""database class for visitors"""

	# Kludge to extract date and time, given old (3.x) version of MySQL installed on cascade2

	TIMEZONE_OFFSET = -8
	TimestampKey = "date_add( log.timestamp, interval %d hour )" % TIMEZONE_OFFSET
	TimestampKeyL = "date_add( l.`timestamp`, interval %d hour )" % TIMEZONE_OFFSET
	TimestampKeyR = "date_add( r.`timestamp`, interval %d hour )" % TIMEZONE_OFFSET

	DateKey = "date_format( %s,'%%Y-%%m-%%d')" % TimestampKey
	DateKeyL = "date_format( %s,'%%Y-%%m-%%d')" % TimestampKeyL
	TimeKey = "date_format( %s,'%%H:%%i:%%s')" % TimestampKey
	TimeKeyL = "date_format( %s,'%%H:%%i:%%s')" % TimestampKeyL

	YearKey = "date_format( %s,'%%Y')" % TimestampKey
	MonthKeyLo = "date_format( %s,'%%Y-%%m-00')" % TimestampKey
	MonthKeyHi = "date_format( %s,'%%Y-%%m-31')" % TimestampKey
	MonthNameKey = "MONTHNAME( %s )" % TimestampKey
	MonthKey = "MONTH( %s )" % TimestampKey
	DayKey = "DAYOFMONTH( %s )" % TimestampKey
	DayNameKey = "DAYNAME( %s )" % TimestampKey

	def __init__( self ):
		self.Db = MySQLdb.Connect(
			db="visitors",
			user="WWW",
			passwd="WWW")
			
		self.DatesVisitors = None
		self.YY = self.MM = self.DD = ""

	def SetDate( self, date ):
		self.Date = date
		if date:
			self.YY, self.MM, self.DD = date.split( "-" )
	
	def GetDate( self ):
		return "%04d-%02d-%02d" % ( int( self.GetYear()), int( self.GetMonth()), int( self.GetDay()))

	def GetPrettyDate( self ):
		return "%d %s %s" % ( int( self.GetDay()), MONTH_NAME[ int( self.GetMonth())], str(self.GetYear()) )

	def GetYear( self ):
		if self.YY and int( self.YY ):
			return self.YY
		else:
			return self.LastYear

	def GetMonth( self ):
		if self.MM and int( self.MM ):
			return self.MM
		else:
			return self.LastMonth

	def GetDay( self ):
		if self.DD and int( self.DD ):
			return self.DD
		else:
			return self.LastDay

	def Cursor( self ): 
		return self.Db.cursor()
		
	def Execute( self, query ):
		cursor = self.Cursor()
		# print query
		cursor.execute( str( query ))	# convert Select objects to string (strings are unaffected)
		return cursor
		
	def ExecuteAndFetch( self, query, trace=False ):
		if trace:
			print query
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
				

	def FetchDetails3( self ):
		
		self.Execute( "drop table if exists arrivals;" );

		self.Execute( """create temporary table IF NOT EXISTS arrivals ( 
			id integer unsigned not null primary key ,
			`timestamp` datetime not null ) """ )
		
		# self.Execute( """delete from arrivals""" )
		
		self.Execute ("""
			insert into arrivals ( id, timestamp )
				select l.id, max( r.timestamp )
					from log as l, log as r 
					where	l.name = r.name 
						and l.sensor = r.sensor 
						and r.timestamp < l.timestamp 
						and l.action = 'Departure' 
						and r.action = 'Arrival'
					group by l.id
			""")
		
		return self.ExecuteAndFetch( 
			Select( self.TimeKey + ", sensor, name, action, log.timestamp, arrivals.timestamp",
				table="log LEFT OUTER JOIN arrivals", 
				on = "log.id = arrivals.id",
				where = self.DateKey + "='%s'" % self.GetDate(),
				order="log.timestamp"))

	def FetchDetails2( self ):
		return self.ExecuteAndFetch( 
			Select( 
				self.TimeKeyL + ", l.sensor, l.name, l.action, l.timestamp, max(r.timestamp)", 
				table="log AS l LEFT OUTER JOIN log AS r", 
				on = [
#					self.DateKeyL + "='%s'" % self.GetDate(),
					"l.name = r.name",
					"l.sensor = r.sensor",
					"r.timestamp < l.timestamp",
					"l.action = 'departure'",
					"r.action = 'arrival'",
					],
				group="l.id",
				order="l.timestamp"))

	def FetchDetails1( self ):
		return self.ExecuteAndFetch( 
			Select( 
				self.TimeKey + ",sensor,name,action", 
				"log", 
				order="timestamp",
				where = self.DateKey + "='%s'" % self.GetDate()))

	def FetchYears( self ):
		self.Years = \
			self.ExecuteAndFetch( 
				Select( table = "log",
					columns =  self.YearKey,
					group = self.YearKey,
					order = self.YearKey))

		self.LastYear = self.Years[-1][0]
		return self.Years


	def FetchMonths( self, year ):
		self.CurrentYear = year

		self.Months =  \
			self.ExecuteAndFetch( 
				Select( table="log",
					columns =  [
						self.DateKey,  
						self.MonthKey,
						self.MonthNameKey,
						],
					group = self.MonthKey,
					order = self.MonthKey,
					where = self.YearKey + " = " + str( year )))

		self.LastMonth = self.Months[ -1 ][ 1 ]
		return self.Months

	def FetchDaysAndArrivals( self, year, month ):
		self.CurrentMonth = month

		self.DaysAndArrivals = \
			self.ExecuteAndFetch( 
				Select( 
					table="log",
					columns =  [
						self.DateKey,  
						self.DayKey,
						self.DayNameKey,
						"count(action='Arrival')",
						],
					group=self.DateKey,
					order=self.DateKey,
					where = self.YearKey + " = " + str( year )
						+ " and "
						+ self.MonthKey + " = " + str( month )))

		self.LastDay = self.DaysAndArrivals[ -1 ][ 1 ]
		return self.DaysAndArrivals

	def ShowDaysAndArrivals( self ):
		year, month = self.GetYear(), self.GetMonth()
		print "<table><tr>"
		print "<th colspan=2>Date</th>"
		print "<th>#Visitors</th>"
		print "</tr>"
		for row in self.FetchDaysAndArrivals( year, month ):
			print "<tr>"
			print "<td bgcolor=%s><font size=+1>" % SelectedColor( row[1], self.GetDay()),
			print self.HrefToDate( row[1], year, month, row[1]), 
			print "</font></td>"
			print "<td bgcolor=%s><font size=+1>" % SelectedColor( row[1], self.GetDay()),
			print self.HrefToDate( row[2], year, month, row[1]), 
			print "<td align=center bgcolor=%s><font size=+1>" % SelectedColor( row[1], self.GetDay()),
			print row[3], "</td>"
			print "<tr>"
		print "</table>"

	def ShowMonths( self ):
		year = self.GetYear()
		print "<table><tr>"
		print "<th>Month</th>"
		print "</tr>"
		for row in self.FetchMonths( year ):
			print "<tr><td bgcolor=%s><font size=+2>" % SelectedColor( row[1], self.GetMonth()),
			print self.HrefToDate( row[2], year, row[1]), 
			print "</font></td><tr>"
		print "</table>"

	def ShowYears( self ):
		print "<table><tr>"
		print "<th>Year</th>"
		print "</tr>"
		for row in self.FetchYears():
			print "<tr><td bgcolor=%s><font size=+3>" % SelectedColor( row[0], self.GetYear()),
			print self.HrefToDate( row[0], row[0]), 
			print "</font></td><tr>"
		print "</table>"

	def URLToDate( self, year, month=None, day=None ):
		if not month:
			month = "00"	# missing month means last month in year
		if not day:
			day = "00"	# mising day means last day in month

		date = str( year ) + "-" + str( month ) + "-" + str( day )

		return URL + "?date=" + date

	def HrefToDate( self, item, year, month=None, day=None ):
		return '<a href="%s">' % self.URLToDate( year, month, day ) + str( item ) + "</a>"

	def ShowDatesAndArrivals( self ):
		# construct table for all possible dates
		#	(and fill in default date range for second table)

		print "<center><b><i><font size=+2>"
		print "Select Report"
		print "</font></i></b></center>"

		print "<TABLE rules=all cellpadding=3 border=2>"

		print "<TR valign=top><TD valign=top>"
		self.ShowYears()
		print "</TD><TD valign=top>"
		self.ShowMonths()
		print "</TD><TD valign=top>"
		self.ShowDaysAndArrivals()
		print "</TD></TR>"

		print "</TABLE>"
		
	def ShowSelectedDetails( self ):
		# construct table for selected range

		print "<center><b><i><font size=+2>"
		print self.GetPrettyDate()
		print "</font></i></b></center>"

		print "<TABLE rules=all cellpadding=3 border=2 bgcolor=%s>" % COLOR_SELECTED
		print "<TR><TH>When</TH><TH>Where</TH><TH>Who</TH><TH>What</TH><TH>Duration</TH></TR>"

		for row in self.FetchDetails():
			print "<TR>"
			for col in row[0:4]:
				print "<TD>" + str( col ) + "</TD>"
				
			if row[3] == "Departure":
				try:
					delta = self.ComputeDuration( row[5], row[4])
					print "<TD>" + str( delta ) + "</TD>"
				except KeyError:
					print "<TD>?</TD>"
					
			print "</TR>"

		print "</TABLE>"
		
	def ShowHistory( self, date ):
		self.SetDate( date )

		print "<h1>Visitor Log</h1>"		# print "<h1>Hiro's Visitors</h1>"

		# table header for joining following two tables

		print "<TABLE rules=all cellpadding=3 border=2>"
		print "<TR><TD valign=top>"
		
		self.ShowDatesAndArrivals()

		# glue for joining two tables

		print "</TD><TD valign=top bgcolor=%s>" % COLOR_SELECTED

		self.ShowSelectedDetails()

		# table trailer for joining above two tables

		print "</TD></TR>"
		print "</TABLE>"

	def Time2Seconds( self, t ):
		"""convert MySQL datetime to seconds since epoch"""
		
		t = str( t )
		
		if " " in t:
			date,t = str( t ).split(" ")
			yy,mo,dd = date.split("-")
		else:
			yy=2000
			mo=dd= 1
			
		if "." in t:
			t,ignore = t.split(".")
		hh,mm,ss = t.split(":")
		
		return time.mktime(( int( yy ), int( mo ), int( dd ), int( hh ), int( mm ), int( ss ), 0, 1, -1 ))

		
	def ComputeDuration( self, arrival, departure ):
		try:
			a = self.ParseTime( arrival )
			d = self.ParseTime( departure )
		except:
			return "?"
			
		delta = d - a

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
	<BODY bgcolor=%s>
	""" % COLOR_UNSELECTED

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
		print "<hr><H1>Exception raised:</H1>\n<pre>\n"
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
		print "<table><tr valign=top>"
		print "<td>"				##############################
		
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
		
		if 1 :
			print "</td><td>"		##############################
			print "<i>", time.ctime(), "</i>"
		print "</td>"				##############################
		print "</tr></table>"

	# Trailer

	print "</body></html>"


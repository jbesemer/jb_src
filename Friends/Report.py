#!/usr/local/bin/python

import os, os.path
import sys

FRIENDS_FILENAME = "Friends.txt"

REPORT_INTERVAL = 30 	# minutes, 60, 30, 20, 15, 10 are common values

class Time( object ):
	EndingTime = None
	First = None
	Last = None

	def __init__( self, hh=0, mm=0, ss=0, s=None ):
		self.hour = hh
		self.minute = mm
		self.second = ss
		if s:
			self.FromString( s )

		if not Time.First:
			Time.First = self

		if not Time.Last or Time.Last < self:
			Time.Last = self

	def FromString( self, hhmmss ):
		hh, mm, ss = [ int(x) for x in hhmmss.strip()[:8].split(":")]
		self.__init__( hh, mm, ss )

	def AsMinutes( self ):
		return self.hour * 60 + self.minute # + self.second / 60.0

	@classmethod
	def MarkEndingTime( self ): self.EndingTime = self.Last
	@classmethod
	def GetEndingTime( self ): return self.EndingTime

	def RoundedUp( self, interval=REPORT_INTERVAL ):
		mm = interval * int(( self.minute + interval - 1 ) / interval )
		return Time( self.hour + int( mm / 60 ), mm % 60, self.second )

	def RoundedDown( self, interval=REPORT_INTERVAL ):
#		mm = interval * int(( self.minute + interval - 1 ) / interval )
#		return Time( self.hour + int( mm / 60 ), mm % 60, self.second )
		pass

	def __add__( self, minutes ):
		""" create a new time some minutes in the future from this one """
		hh, mm, ss = self.hour, self.minute, self.second
		mm += int( minutes )

		return Time( hh + mm/60, mm % 60, ss )

	def __sub__( self, other ):
		""" subtract 2 times, resulting in minutes """
		return self.AsMinutes() - other.AsMinutes()

	def __iadd__( self, minutes ):
		""" add minutes to this time """
		mm = self.minute + minutes
		self.minute = mm % 60
		self.hour += mm / 60
		return self
	
	def __cmp__( self, other ):
		return cmp( self.AsMinutes(), other.AsMinutes())

	def __str__( self ):
		return "%02d:%02d" % ( self.hour, self.minute )
#		return "%02d:%02d:%02d" % ( self.hour, self.minute, self.second )


class Interval( object ):
	def __init__( self, start, stop=None ):
		self.start = Time( s=start )
		if stop:
			self.stop = Time( s=stop )
		else:
			self.stop = self.start

	def __contains__( self, time ):
		return self.start <= time and time < self.stop

	def __len__( self ):
		""" return duration in minutes """
		return self.stop - self.start

	def __iadd__( self, stop ):
		self.stop = Time( s=stop )
		return self

People = []
Names = {}

class Person( object ):
	def __init__( self, name, time=None, tz=None ):
		self.name = name.strip()
		self.intervals = []
		self.intervalCache = None
		self.tz = tz
		self.onlineNow = False

		if time:
			self.intervals.append( Interval( time ))
			self.online = True
		else:
			self.online = False

		# auto cross-ref
		global People, Names
		People.append( self )
		Names[ self.name ] = self
#		print "Adding:", name

	def GetTotal( self ): 
		return reduce( lambda x,y: x+len(y), self.intervals, 0 )

	def SetOnline( self, time ):
		if self.online:
			self.intervals[ -1 ] += time
		else:
			self.intervals.append( Interval( time ))
			self.online = True

	def SetOffline( self, time ):
		self.online = False

	def SetOnlineNow( self, online=True ):
#		print "SetOnlineNow(", self.name, ")"
		self.onlineNow = online	

	def __contains__( self, time ):
		if self.intervalCache and time in self.intervalCache:
			return True
		for interval in self.intervals:
			if time in interval:
				self.intervalCache = interval
				return True
		return False

	def GetStart( self, time ):
		if time in self.intervalCache:
			return self.intervalCache.start
		else:
			for interval in self.intervals:
				if time in interval:
					return interval.start

	def GetStop( self, time ):
		if time in self.intervalCache:
			return self.intervalCache.stop
		else:
			for interval in self.intervals:
				if time in interval:
					return interval.stop

	def ReportStatus( self, time, delta ):
		if self.OnDuring( time, delta ):
			return " " # mustn't be False
#			return GRN( "////" )
#			return GRN( delta )
#			return str( delta )

		# else we have to enumerate transitions within the interval
		r = ""
		wasOnline = time in self
		for m in xrange( delta + 1 ):
			t0 = time + m
			isOnline = t0 in self
			if isOnline != wasOnline:
				r += " "
				if wasOnline:
					t1 = self.GetStop( t0 + -1 )
					if t1 != Time.GetEndingTime():
						r += RED( t1 )
				else:
					t1 = self.GetStart( t0 )
					if t1 != Time.First:
						r += GRN( t1 )
			wasOnline = isOnline
	
		return r

	def OnDuring( self, time, delta ):
		a = b = None
		if time in self: a = self.intervalCache
		if time+delta in self: b = self.intervalCache

		return a and b and a==b

	def OnSince( self ):
		if not self.online:
			return "N/A"
		else:
			return str( self.intervals[-1].start )

	def GetNameAsHtmlTD( self ):
		name = B( self.name )

		if self.GetTotal():
			if self.onlineNow:
				return '<td align=center bgcolor="#ccffcc">%s</td>' % name
			else:
				return "<td align=center>%s</td>" % name
		else:
			return '<td align=center bgcolor="#FFCCFF">%s</td>' % name


def B( text ): return "<b>%s</b>" % str( text )
def RED( text ): return FONT( B( text ), color="#800000" )
def GRN( text ): return FONT( B( text ), color="#008000" )

def FONT( text, color=None, face=None, size=None ):
	return ( "<font%s%s%s>%s</font>" % (
		OptProp( "color", color ),
		OptProp( "face", face ),
		OptProp( "size", size ),
		str( text )))

def OptProp( name, value ):
	if value:
		return ' %s="%s"' % ( name, str( value ))
	else:
		return ""

class Summary( object ):

	def __init__( self, filename, friendsOnline=[] ):
		self.friendsOnline = friendsOnline
		self.Load( filename )

	def Load( self, filename ):
		self.filename = filename
		input = file( filename )
		for line in input:
			Offline = set( People )
			fields = line.strip().split( None, 1 )
			if not fields:
				continue
			t = fields[0]
			if len( fields ) >= 2 and fields[1].strip() != ",":
				names = fields[1].split( "," )
				for name in names:
					try:
						person = Names[ name ]
						person.SetOnline( t )
						Offline.remove( person )
					except KeyError:
						person = Person( name, t )
						
			for person in Offline:
				person.SetOffline( t )

		Time.MarkEndingTime()

		for name in self.friendsOnline:
			try:
				Names[ name ].SetOnlineNow()
			except KeyError:
				pass

	def PrHTML( self ):
		print "<table frame=box rules=all>"
		
		print "<tr>"
		print "<td align=center><b>Time</b></td>"
		for person in People:
			print person.GetNameAsHtmlTD()
#			print "<td align=center>%s since %s</td>" \
#				% ( person.name, person.OnSince())
		print "</tr>"
		
		time = Time( 00, 00 )
		EndingTime = Time.GetEndingTime()
		while time <= EndingTime:
			print "<tr>"
			print "<td align=center>%s</td>" % B( str( time ))
			for person in People:
				s = person.ReportStatus( time, REPORT_INTERVAL )
				if s:
					print '<td align=center bgcolor="#ccffcc">%s</td>' % s 
				else:
					if person.GetTotal():
						print "<td align=center></td>"
					else:
						print '<td align=center bgcolor="#FFCCFF"></td>'
			print "</tr>"
			time += REPORT_INTERVAL

		print "<tr>"
		print "<td align=center>%s</td>" % "Total"
		for person in People:
			print "<td align=center>%d</td>" % person.GetTotal()
		print "</tr>"

		print "<table>"

# seed the people list
for line in file( FRIENDS_FILENAME ):
	line = line.strip()
	if not line:
		break
	if '[' in line:
		continue
	if '/' in line:
		name, tz = line.split('/', 1 )
		Person( name.strip(), tz=tz.strip())
	else:
		Person( line )


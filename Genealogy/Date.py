
# date encoding/decoding ##############################################

import datetime

MONTH_NAMES = [ "???", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ]		

DATE_SEP = "-"
DATE_SEP_ALT = "/"

class Date( object ):
	""" represent dates to varying degrees of precision """
	# in particular need to represent dates with missing days or months
	# and dates that are expressly "approximate".
	# The database encoding is yyyy-mm-dd 
	#	with an optional "?" for approximate dates
	#	-- 10 or 11 chars

	def __init__( self, yy=0, mm=0, dd=0, ca=False ):
		self.yy = yy
		self.mm = mm
		self.dd = dd
		self.ca = ca

	# component access:
	def SetYear( self, yy ):	
		assert 1000 <= int( yy ) <= 9999
		self.yy = int( yy )
		
	def SetMonth( self, mm ):
		assert 0 <= int( mm ) <= 12
		self.mm = int( mm )
		
	def SetDay( self, dd ):
		assert 0 <= int( dd ) <= 31
		self.dd = int( dd )
		
	def SetApprox( self, ca=True ):	
		self.ca = ca
		
	def SetYYMMDD( self, yy=0, mm=0, dd=0 ):
		self.yy = yy
		self.mm = mm
		self.dd = dd

	def SetYYMMDDCA( self, yy=0, mm=0, dd=0, ca=False ):
		self.SetYYMMDD( yy, mm, dd )
		self.ca = ca

	def GetYear( self ):	return self.yy
	def GetMonth( self ):	return self.mm
	def GetDay( self ):		return self.dd
	def GetApprox( self ):	return self.ca

	def ParseNormal( self, date ):
		""" parse repr() form used in MySQL """
		
		self.SetApprox( "?" in date )
		parts = date.replace( "?", "" )
		
		if DATE_SEP in date:
			parts = date.split( DATE_SEP )
		elif DATE_SEP_ALT in date:
			parts = date.split( DATE_SEP_ALT )
		else:
			raise ValueError, "Bad date: '%s'" % date

		if   len( parts ) == 1:		self.SetYYMMDD( parts[ 0 ])
		elif len( parts ) == 2:		self.SetYYMMDD( parts[ 0 ], parts[ 1 ])
		elif len( parts ) == 3:		self.SetYYMMDD( parts[ 0 ], parts[ 1 ], parts[ 2 ])
		else:
			raise ValueError, "Bad date: '%s'" % date

	def FromDate( self, date, ca=False ):
		self.SetYYMMDD( date.year, date.month, date.day )
		self.SetApprox( ca )
		
	def AsDate( self ):
		return datetime.date( self.yy, max( 1, self.mm ), max( 1, self.dd ))

	# formatting for DB and for humans

	def IfCa( self ):
		if self.ca:	return "?"
		else:		return ""

	def OptMonth( self ):
		if self.mm: return DATE_SEP + MONTH_NAMES[ self.mm ]
		else:		return ""

	def OptDay( self ):
		if self.dd: return DATE_SEP + "%02d" % self.dd
		else:		return ""

	def __repr__( self ):
		""" format for storage in MySQL """
		return ( "%04d" % self.yy
			+	self.OptMonth()
			+	self.OptDay()
			+	self.IfCa())

	def __str__( self ):
		""" format for external display """
		return ( "%04d" % self.yy
			+	self.OptMonth()
			+	self.OptDay()
			+	self.IfCa())

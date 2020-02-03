#!/usr/local/bin/python

import os, os.path
import urllib, urllib2
from HTMLParser import HTMLParser

FIRSTNAME = "Hiroshi"
LASTNAME = "Sakai"
PASSWORD = ""

LOG_FOLDER = "@Logs"

MAIN = "http://secondlife.com/"
FRIENDS = "http://secondlife.com/community/friends-inner.php"

URL = "https://secure-web4.secondlife.com"
LOGIN = "/account/login.php?type=second-life-member&nextpage=/account/index.php"
LOGIN = "/account/login.php?type=second-life-member&nextpage=/community/friends-inner.php"
LOGIN = "/account/login.php"

HEADERS = {
	"ACCEPT":
		 "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
	"ACCEPT-CHARSET":
		 "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
	"ACCEPT-ENCODING":
		 "text/html,text/plain",
	"ACCEPT-LANGUAGE":
		 "en-us,en;q=0.5",
#	"CONNECTION":
#		 "keep-alive",
#	"KEEP-ALIVE":
#		 "300",
	"USER-AGENT":
		"Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.0.11) Gecko/20070312 Firefox/1.5.0.11",
	}

Example = """
<form action="login.php" method="post">
<input type="hidden" name="form[type]" value="second-life-member" />
<input type="hidden" name="form[nextpage]" value="/account/index.php" />
<input type="hidden" name="form[persistent]" value="Y" />
<td><input type="text" name="form[username]" value="" size="20" maxlength="31" />
<input type="text" name="form[lastname]" value="" size="20" maxlength="50" />
<input type="password" name="form[password]" value="" size="20" maxlength="16" />
<input type="image" src="/_img/buttons/b_submit.gif" name="submit" value="Submit" />
</form>
"""

def GetParams( password, username=FIRSTNAME, lastname=LASTNAME ):
	return urllib.urlencode({
		"form[type]":			"second-life-member",
		"form[nextpage]":		"/community/friends-inner.php",	# "/account/index.php",
		"form[persistent]":		"Y",
		"form[username]":		username,
		"form[lastname]":		lastname,
		"form[password]":		password,
		"submit":				"Submit",
	})

class MyHtmlParserException( Exception ): pass

class ParseFriends( HTMLParser ):
	
	TRACE_DATA = True
	
	def __init__( self, text="" ):
		HTMLParser.__init__( self )

		self.text = text

		self.inTable = self.inTd = False
		self.data = ""
		self.names = []

		if text:
			try: 
				self.feed( text )
				self.close()
			except MyHtmlParserException:
				pass

	def handle_starttag( self, tag, attrs ):
		if tag == "table":
			self.inTable = True
		elif tag == "td":
			self.inTd = True

	def handle_endtag( self, tag ):
		if self.inTable and tag == "table":
			self.inTable = False
			raise MyHtmlParserException()
		elif self.inTd and tag == "td":
			self.inTd = False
			self.names.append( self.data.strip())
			self.data = ""

	def handle_data( self, data ):
		if self.inTable and self.inTd:
			self.data += data

	def __str__( self ): return "\n".join( self.names )
		
	def GetNames( self ): return self.names

	def GetNamesAsHTML( self ):
		return ( "<ul>\n"
			+ "\n".join([ "<li>%s" % name for name in self.names ])
			+ "\n</ul>\n" )

def GetFriends( password ):
	urllib2.install_opener( 
		urllib2.build_opener( 
			urllib2.HTTPCookieProcessor()))

	req = urllib2.Request( URL + LOGIN, GetParams( password ), HEADERS )
	f = urllib2.urlopen( req )
	page = f.read()
	if os.path.isdir( LOG_FOLDER):
		file( os.path.join( LOG_FOLDER, "PrevPage.html" ), "wt" ).write( page )
	return ParseFriends( page )

def GetFriendsNames( password ):
	return GetFriends( password ).GetNames()

if __name__ == "__main__":
	import sys
	
	def Main( args ):
		if len( args ) >= 1:
			password = args[0]

			if password == "-default":
				try:
					from Password import PASSWORD
				except OSError:
					print "Warning: no password file"
					PASSWORD = ""
				else:
					password = PASSWORD
			
			print "\n".join(GetFriends( password ))
		else:
			print "Must specify password."
		


	Main( sys.argv[ 1: ])

#!/usr/local/bin/python

####################################
# command line and API utility for
# sending email via arbitrary SMTP server
#

import sys, string, os.path, StringIO
import smtplib, base64
from MimeWriter import MimeWriter

from time import localtime, asctime, time
from getpass import getuser
import socket
import copy
import types

######################################
# global constants
#

Default_SMTP_Host = 'cascade'
DefaultSender = "<MIME-Bot>"
SENDMAILUSER = 'SENDMAILUSER'

# multi-part mime prolog and epilog text

prolog = "This is a multipart message in MIME format\n\n"
epilog = "\nEnd of multipart message in MIME format\n"

# mime header substrings

MimeTextType = "text/plain; charset=us-ascii"
MimeBinaryType = "application/octet-stream"
MimeMultiTypeMixed = "mixed"

# list of message headers, header field names & default values

HeaderFrom = "From"
HeaderTo = "To"
HeaderCc = "Cc"
HeaderBcc = "Bcc"
HeaderDate = "Date"
HeaderSu = "Subject"

# more or less constant/standard/default header entries 

DefaultHeader = {
#	"ReplyTo": "[cannot reply to robot-generated message]",
	"X-Mailer": "Python SMTP Robot",
	"X-Remote-Host": "None",
	"MIME-Version": "1.0"
	};

##################################################
# global variables
#

# option flags

DebugFlag = 0		# flag to control debug output from SMTP
VerifyFlag = 0		# flag to control name verification pass
SendFlag = 1		# flag to control actual sending of message
VerboseFlag = 1		# flag to enable progress messages
KeepFlag = 0		# flag to control saving of message encoding

##################################################
# file type mapping functions
#

if os.name == "nt":
	def getContentType( ext ):

		""" Return the Mime type/subtype from the Win Registry 
			per a file extension"""

		# THIS PART IS WIN32-SPECIFIC
		#
		# TODO: add a switch to substitute the unix version 
		# from the runtime lib

		from win32api import RegOpenKeyEx
		from win32api import RegQueryValueEx
		from win32api import RegCloseKey
		from win32con import HKEY_CLASSES_ROOT

		result = MimeBinaryType
		try:
			key = RegOpenKeyEx( HKEY_CLASSES_ROOT, ext, 0 )
			try:
				assoc = RegQueryValueEx( key, "Content Type" )
				result = assoc[ 0 ]
			except: 
				pass
			
			RegCloseKey( key )
		except: pass

		return result

elif os.name == "posix":

	def getContentType( ext ):
		import mimetypes
		mimetypes.init()
		result = MimeBinaryType
		try:
			res = mimetypes.guess_type( ext )
			print "ext:", ext, "mimetype:", res
			if res and res[0]:
				result = res[0]
		except: 
			pass
		return result

def getFileContentType( filename ):

	"Return the Mime type/subtype for a particular filename"

	path, ext = os.path.splitext( os.path.basename( filename ))
	ext = string.lower( ext )
	tysub = getContentType( ext )
	return tysub

def isBinaryContentType( tysub ):
	
	"return true iff the Mime type/subtype deserves a binary encoding"

	( type, subtype ) = string.split( tysub, "/" )
	return type != "text" and type != "message"

		

##################################################
# several different kinds of attachments
#

class Attachment( object ):			# abstract class
	def getContentType( self ):
		return self.type

	def addEncodingHeader( self, part ):
		pass

	def getBasename( self ):
		return os.path.basename( self.name )

class TextFileAttachment( Attachment ):

	def __init__( self, name, type ):
		self.name = name
		self.type = type

	def getBody( self ):
		file = open( self.name, "r" )
		data = file.read()
		file.close()

		self.size = `len( data )` + " bytes"

		return data
		
	def getSize( self ):
		return self.size	# not valid until after getBody()

class BinaryFileAttachment( Attachment ):

	def __init__( self, name, type ):
		self.name = name
		self.type = type

	def getBody( self ):
		file = open( self.name, "rb" )
		data = file.read()
		file.close()

		self.size = `len( data )`

		data = base64.encodestring( data )

		self.size = self.size + " ( expanded to " + `len( data )` + " ) bytes"

		return data
		
	def addEncodingHeader( self, part ):
		part.addheader( "Content-transfer-encoding", "base64" )

	def getSize( self ):
		return self.size	# not valid until after getBody()

def FileAttachment( filename ):
	"helper to create a binary or text file attachment, depending on file type"

	type = getFileContentType( filename )

	if isBinaryContentType( type ):
		return BinaryFileAttachment( filename, type )
	else:
		return TextFileAttachment( filename, type )	

class TextAttachment( Attachment ):

	Count = 0

	def __init__( self, body = "", name=None ):
		self.Count = self.Count + 1
		if name:
			self.name = name
		else:
			self.name = "Text-Literal-" + ( "%03d" % self.Count )
		self.body = body
		self.type = MimeTextType
		self.isBinary = 0

	def getBody( self ):
		return self.body

	def getSize( self ):
		return `len( self.getBody())` + " bytes"

# companion to TextAttachment

def getLiteralText():

	"prompt for and assemble a block of text and return it as a string"

	text = ""
	print "Enter message text:"
	while 1:
		line = sys.stdin.readline()
		if line == "" or line == ".\n": 
			break
		text = text + line
	
	print ""
	return text

##########################################
# Misc utilities
#

def makeList( value ):
	if type( value ) == types.ListType:
		return value

	elif type( value ) == types.StringType:
		return [ value ]

	elif type( value ) == types.TupleType:
		return list( value )

	else:
		return [ value ]

#	elif type( value ) == type( Attachment ):
#		return [ value ]
#
#	else:
#		raise "missing string or list type"

# normalize header key

def normalize( key ):

	# this normalizes keys like "x-remote-host" to "X-Remote-Host"
	# it does NOT lower non-leading letters that are capitalized.
	# this means it does the right thing for cases like "MIME-Version"
	# but it means that it won't prevent

	def cap1( word ):
		l = len( word )
		if   l >= 2:	return word[0].upper() + word[1:]
		elif l == 1:	return word[0].upper()
		else:			return ""

	return "-".join([ cap1( word ) for word in key.split( "-" )])
		

##########################################
# message class
#
# This represents an email message, including
# provisions for normal header fields plus
# multi-part mime attachments.
#
# The paradigm is that you create and add to
# the message until you ultimately convert it
# to text before sending.

class Message( object ):

	def __init__( 	self,
		body=[],	# one or more of the following:
					# 	FileAttachment( file )
					# 	TextAttachment( text )

		to=[],		#  recipients
		cc=[], 
		bcc=[], 
		fr=None, 	# sender;  None => lookup user id
		subject="", su="", re="",
		**custom	# custom header fields via extra field=value args
		):

		self.body = makeList( body )
		self.fr = fr
		self.to_list = makeList( to )
		self.cc_list = makeList( cc )
		self.bcc_list = makeList( bcc )
		self.subject = subject + su + re

		self.Header = copy.copy( DefaultHeader )

		# merge in custom fields, if any

		for key, value in custom.items():
			self.Header[ normalize( key )] = value

		self.rep = None
		self.encoded = 0


	def addBody( self, attachment ):
		self.body += makeList( attachment )

	def __iadd__( self, attachment ):
		self.addBody( attachment )
		return self

	def setFrom( self, fr ):
		self.fr = fr

	def getFrom( self ):
		return self.fr

	def setSubject( self, su ):
		self.subject = su

	def addTo( self, to ):
		self.to += makeList( to )

	def addCc( self, cc ):
		self.cc += makeList( cc )

	def addBcc( self, bcc ):
		self.bcc += makeList( bcc )

	def addOptHead( self, key, value ):
		if value:
			self.Header[ key ] = value

	def addOptHeadList( self, key, value ):
		if value:
			self.Header[ key ] = ", ".join( value )

	# encoding the message

	def _encode_header( self ):

		"""	encode sendmail recipient list and header field/value 
			pairs from input data"""

		self.recipients = ( self.to_list 
						+ self.cc_list 
						+ self.bcc_list )

		if len( self.recipients ) <= 0:
			raise "Nobody to send to"

		self.addOptHead( HeaderSu, self.subject )
		self.addOptHeadList( HeaderTo, self.to_list )
		self.addOptHeadList( HeaderCc, self.cc_list )

		# from may come from "fr=" arg or custom From= arg.
		# failing that, we try getuser()@getfqdn().
		# failing that we try environment var SENDMAILUSER
		# failing that we use DefaultSender

		if not self.Header.has_key( HeaderFrom ):
			if not self.fr:
				try:
					self.fr = ( getuser() 
								+ '@' 
								+ socket.getfqdn())
				except:
					if os.environ.has_key( SENDMAILUSER ):
						self.fr = os.environ[ SENDMAILUSER]
					else:
						self.fr = DefaultSender

			self.Header[ HeaderFrom ] = self.fr 

		if not self.Header.has_key( HeaderDate ):
			self.Header[ HeaderDate ] = asctime( localtime(time()))

		if VerboseFlag:
			print "From:", self.Header[ HeaderFrom ]
			print "Date:", self.Header[ HeaderDate ]

	def _encode_body( self ):

		"""	Encode the various header and attachment lists into 
			a single MIME-encoded 'message'"""

		if VerboseFlag:
			print "MIME Encoding... "

		self.msg = StringIO.StringIO()
		self.mime = MimeWriter( self.msg )

		for key in self.Header.keys():
			self.mime.addheader( key, self.Header[ key ])

		self.fd1 = self.mime.startmultipartbody( MimeMultiTypeMixed )
		self.fd1.write( prolog )

		for attachment in self.body:
			part = self.mime.nextpart()

			baseName = attachment.getBasename()

			if VerboseFlag: 
				print baseName + ": ",

			mimeType = attachment.getContentType()
			if VerboseFlag: 
				print "(" + mimeType + ")",

			attachment.addEncodingHeader( part )

			fd = part.startbody( mimeType, [[ "name", baseName ]])

			data = attachment.getBody()

			if VerboseFlag: 
				print attachment.getSize(),

			fd.write( data )

			if VerboseFlag: 
				print ""

		self.mime.lastpart()

		self.fd1.write( epilog )

	def encode( self ):
		self._encode_header()
		self._encode_body()
		self.encoded = 1

	def __str__( self ):
		if not self.encoded:
			self.encode()

		if not self.rep:
			self.rep = self.msg.getvalue()
		return self.rep

	def __len__( self ):
		return len( str( self ))

	def send( self ):
		self.encode()
		send( 
			self.Header[ HeaderFrom ],
			self.recipients,
			str( self ))


##################################################
## send a formatted message to recipients


def send( sender, recipients, message, SMTP_Host=Default_SMTP_Host ):

	"""	Send a properly formatted message to a list of recipients 
		via a given SMTP host."""

	server = smtplib.SMTP( SMTP_Host )
	server.set_debuglevel( DebugFlag )

	errs = {}

	if VerifyFlag :
		for user in recipients:
			print user + ":",
			print server.verify( user )

	try:
		if SendFlag:
			if VerboseFlag:
				print "Sending... "

			errs = server.sendmail( 
					sender,
					recipients, 
					message )

		if KeepFlag:
			if VerboseFlag:
				print "Saving... "

			file = open( "send.txt", "w" )
			file.write( message )
			file.close()	

	except smtplib.SMTPRecipientsRefused, who:
		print "All Recipients Refused:"
		errs = who.recipients

	except smtplib.SMTPSenderRefused, who:
		print who.args

	except smtplib.SMTPServerDisconnected:
		print "Server Disconnected"

	except smtplib.SMTPDataError:
		print "SMTP Data Error"

	except smtplib.SMTPConnectError:
		print "SMTP Connect Error"

	except smtplib.SMTPHeloError:
		print "SMTP HELO Error"

	server.quit()

	if errs:
		print "Error sending to the following recipients:"
		for recipient in errs.keys():
			print "\t", recipient, errs[ recipient ]


##################################################
# API
##################################################


def sendmail( 	
		body=[],	# one or more of the following:
					# 	FileAttachment( file )
					# 	TextAttachment( text )

		fr=None, 	# sender
		to=[],		#  recipients
		cc=[], 
		bcc=[], 
		subject="", su="", re="",
		):

	msg = Message( 
				body, 
				fr=fr, 
				to=to, 
				cc=cc, 
				bcc=bcc,
				subject=subject,
				su=su,
				re=re )

	msg.send()


##################################################
# default main program
##################################################


if __name__ == '__main__':

	"Main entry point"

	def print_help():

		"print help message"

		print ""
		print "Syntax: send [options] recipients [options]"
		print ""
		print "Options:"
		print ""
		print "	-to | to:	# subsequent args added to normal recipient list [default]"
		print "	-cc | cc:	# subsequent args added to cc recipient list"
		print "	-bcc | bcc:	# subsequent args added to bcc recipient list"
		print "	-from | from:	# next arg is originator name"
		print "	-a		# next arg is a file to be attached"
		print "	-h		# next arg is delivery hostname"
		print "	-s		# next arg is subject line"
		print "	-v		# toggle Verbose flag"
		print "	-vu		# toggle Verify Users flag"
		print "	-ns		# toggle NoSend flag"
		print "	-d		# toggle Debug flag"
		print "	-test		# run test code"
		print ""

	argc = len( sys.argv )

	if argc <= 1 or string.lower( sys.argv[ 1 ]) == '-help' :
		print_help()
		sys.exit( 0 )

	# parse arguments

	i=1
	msg = Message()
	nameList = msg.to_list # initial unqualified args added to this list


	while i < argc:

		def getArg():	## local function to fetch next arg
			global i
			i = i + 1
			return sys.argv[ i - 1 ]

		arg = string.lower( getArg()) 	# current arg

		if arg == "-to" or arg == "to:":	## normal recipient list
			nameList = msg.to_list

		elif arg == "-cc" or arg == "cc:":	## cc recipient list
			nameList = msg.cc_list

		elif arg == "-bcc" or arg == "bcc:":	## bcc recipient list
			nameList = msg.bcc_list


		elif arg == "-from" or arg == "from:":	## originator
			msg.setFrom( getArg())

		elif arg == "-a":			## attach a file
			msg += FileAttachment( getArg())

		elif arg == '-':			## prompt for and attach literal text
			msg += TextAttachment( getLiteralText())

		elif arg == '-h':			## set delivery hostname
			SMTP_Host = getArg()

		elif arg == '-s':			## set subject line
			msg.setSubject( getArg())


		elif arg == '-vu':			## toggle Verify flag
			VerifyFlag = not VerifyFlag	
			
		elif arg == '-ns':			## toggle NoSend flag
			SendFlag = not SendFlag

		elif arg == '-v':			## toggle Verbose flag
			VerboseFlag = not VerboseFlag	
			
		elif arg == '-d':			## toggle Debug flag
			DebugFlag = not DebugFlag

		elif arg == "-test":			## run test code
			test()
			exit( 0 )

		elif arg == "-keep":			## toggle Keep Flag
			KeepFlag = not KeepFlag

		elif arg == "-help":			## run test code
			print_help()
			exit( 0 )

		else:					## add to recipient list
			nameList.append( arg )

	# encode message and maybe send it

	msg.encode()

	if VerboseFlag:
		print "ENTIRE MESSAGE: (multi-part/mixed)", len( msg ), "bytes"

	if VerboseFlag:
		print "Sending... "

	msg.send()


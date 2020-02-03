
import sys, string, os.path, StringIO
import smtplib, base64
from MimeWriter import MimeWriter

from time import localtime, asctime, time
from getpass import getuser
import socket

# name of host to vector through

SMTP_Host = 'cascade'

# default user for testing

defaultUser = "jb@cascade-sys.com"
# defaultUser = "james_besemer@vcd.hp.com"
# defaultUser = "james_besemer@ex.vcd.hp.com"
# defaultUser = "james_besemer@non.hp.com"

# multi-part mime prolog and epilog text

prolog = "This is a multipart message in MIME format\n\n"
epilog = "\nEnd of multipart message in MIME format\n"

# mime header substrings

MimeTextType = "text/plain; charset=us-ascii"
MimeBinaryType = "application/octet-stream"
MimeMultiTypeMixed = "mixed"

# list of attachments (of type class Attachment, see below)

attachments = []

# option flags

DebugFlag = 0		# flag to control debug output from SMTP
VerifyFlag = 0		# flag to control name verification pass
SendFlag = 1		# flag to control actual sending of message
VerboseFlag = 1		# flag to enable progress messages

# list of message headers, header field names & default values

HeaderFrom = "From"
HeaderFromDefault = "<MIME-Bot>"
HeaderTo = "To"
HeaderCc = "Cc"
HeaderBcc = "Bcc"
HeaderDate = "Date"

# more or less constant/standard/default header entries 

DefaultHeader = {
#	"ReplyTo": "[cannot reply to robot-generated message]",
	"X-Mailer": "Python SMTP Robot",
	"X-Remote-Host": "None",
	"MIME-Version": "1.0"
	};

##################################################
# file type mappings

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
# there are different kinds of attachments


class Attachment:			# abstract class
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
		if not name:
			self.name = "Text-Literal-" + ( "%03d" % self.Count )
		else:
			self.name = name
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
# message class
#

class Message:

	def __init__( 	self,
		body=[],	# one or more of the following:
					# 	FileAttachment( file )
					# 	TextAttachment( text )

		fr=None, 	# sender
		to=[],		#  recipients
		cc=[], 
		bcc=[], 
		subject="", su="", re="",
		VfFlag=VerifyFlag,
		SFlag=SendFlag,
		VbFlag=VerboseFlag,
		DFlag=DebugFlag,
		):
		
		self.to_list = to
		self.cc_list = cc
		self.bcc_list = bcc

		self.Verbose = VbFlag
		self.SendFlag = SFlag
		self.Verify = VfFlag
		self.DebugFlag = DFlag

		self.Header = DefaultHeader[:]
		self.subject = subject + su + re
		if self.subject:
			Header[ "Subject" ] = self.subject

		if fr:
			Header[ "From" ] = fr


	def addBody( self, attachment ):
		body.append( attachment )

	def addTo( self, to ):
		self.to.append( to )

	def addCc( self, cc ):
		self.cc.append( cc )

	def addBcc( self, bcc ):
		self.bcc.append( bcc )


	# encoding the message

	def encode_header( self ):

		"""	encode sendmail recipient list and header field/value 
			pairs from input data"""

		self.recipients = ( self.to_list 
						+ self.cc_list 
						+ self.bcc_list )

		if len( recipients ) <= 0:
			raise "Nobody to send to"

		if len( self.to_list ) > 0: 
			self.Header[ HeaderTo ] = ", ".join( self.to_list )
		if len( self.cc_list ) > 0: 
			self.Header[ HeaderCc ] = ", ".join( self.cc_list )
	#	if len( self.bcc_list ) > 0: 
	#		self.Header[ HeaderBcc ] = ", ".join( self.bcc_list )  # duh

		if not self.Header.has_key( HeaderFrom ):
			if os.environ.has_key( 'SENDMAILUSER' ):
				self.Header[ HeaderFrom ] = os.environ[ 'SENDMAILUSER']
			else:
				self.Header[ HeaderFrom ] = ( getuser() 
									+ '@' 
									+ socket.getfqdn())
			if self.Verbose:
				print "From:", self.Header[ HeaderFrom ]

		self.Header[ self.HeaderDate ] = asctime( localtime(time()))
		if self.Verbose:
			print "Date:", self.Header[ self.HeaderDate ]

	def mimeEncode( self ):

		"""	Encode the various header and attachment lists into 
			a single MIME-encoded 'message'"""

		self.msg = StringIO.StringIO()
		self.mime = MimeWriter( self.msg )

		self.encode_header()

		for key in self.Header.keys():
			self.mime.addheader( key, self.Header[ key ])

		self.fd1 = self.mime.startmultipartbody( MimeMultiTypeMixed )
		self.fd1.write( prolog )

		for attachment in self.body:
			part = self.mime.nextpart()

			baseName = attachment.getBasename()

			if self.Verbose: 
				print baseName + ": ",

			mimeType = attachment.getContentType()
			if self.Verbose: 
				print "(" + mimeType + ")",

			attachment.addEncodingHeader( part )

			fd = part.startbody( mimeType, [[ "name", baseName ]])

			data = attachment.getBody()

			if self.Verbose: 
				print attachment.getSize(),

			fd.write( data )

			if self.Verbose: 
				print ""

		self.mime.lastpart()

		self.fd1.write( epilog )

		self.body = self.msg.getvalue()


##################################################
## send a formatted message to recipients


def send( message ):

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
			errs = server.sendmail( 
					Header[ "From" ],  
					recipients, 
					message )

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

	if len( errs.keys()) > 0 :
		print "Error sending to the following recipients:"
		for recipient in errs.keys():
			print "\t", recipient, errs[ recipient ]


##################################################
# API
##################################################


def sendmail( 	body=[],	# one or more of the following:
				# 	FileAttachment( file )
				# 	TextAttachment( text )

		fr=None, 	# sender
		to=[],		#  recipients
		cc=[], 
		bcc=[], 
		subject="", su="", re="",
		VfFlag=VerifyFlag,
		SFlag=SendFlag,
		VbFlag=VerboseFlag,
		DFlag=DebugFlag,
		):

	global VerifyFlag, SendFlag, VerboseFlag, DebugFlag

	VerifyFlag = VfFlag
	SendFlag = SFlag
	VerboseFlag = VbFlag
	DebugFlag = DFlag

	global to_list, cc_list, bcc_list

	to_list = to
	cc_list = cc
	bcc_list = bcc

	su = subject + su + re
	if su:
		Header[ "Subject" ] = su

	if fr:
		Header[ "From" ] = fr

	global attachments
	if body:
		attachments = body

	msg = mimeEncode( VerboseFlag )

	send( msg )


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

	nameList = to_list # unqualified args added to this list

	i=1

	while i < argc:

		def getArg():	## local function to fetch next arg
			global i
			i = i + 1
			return sys.argv[ i - 1 ]

		arg = string.lower( getArg()) 	# current arg

		if arg == "-to" or arg == "to:":	## normal recipient list
			nameList = to_list

		elif arg == "-cc" or arg == "cc:":	## cc recipient list
			nameList = cc_list

		elif arg == "-bcc" or arg == "bcc:":	## bcc recipient list
			nameList = bcc_list


		elif arg == "-from" or arg == "from:":	## originator
			Header[ "From" ] = getArg()

		elif arg == "-a":			## attach a file
			attachments.append( 
				FileAttachment( 
					getArg()))

		elif arg == '-':			## prompt for and attach literal text
			attachments.append( 
				TextAttachment( 
					getLiteralText()))

		elif arg == '-h':			## set delivery hostname
			SMTP_Host = getArg()

		elif arg == '-s':			## set subject line
			Header[ "Subject" ] = getArg()


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

		elif arg == "-help":			## run test code
			print_help()
			exit( 0 )

		else:					## add to recipient list
			nameList.append( arg )

	# encode message and maybe send it

	if VerboseFlag:
		print "MIME Encoding... "

	msg = mimeEncode( VerboseFlag )

	if VerboseFlag:
		print "ENTIRE MESSAGE: (multi-part/mixed)", len( msg ), "bytes"

	if VerboseFlag:
		print "Sending... "

	send( msg )

	if VerboseFlag:
		print "Saving... "

	file = open( "send.txt", "w" )
	file.write( msg )
	file.close()	

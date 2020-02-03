##############################
## flags to control operation

class Flag:
	def __init__( self, init=0 ):
		self.value = init
	def toggle( self ):
		self.value = not self.value
	def set( self, value ):
		self.value = value
	def __rep__( self ):
		return "Flag( %s )" % self.value

NFlag = Flag()	# go through motions but don't send anything
GFlag = Flag()	# just show generated commands
IFlag = Flag()	# just show intermediate code
OFlag = Flag()	# suppress optimizations
SFlag = Flag()	# print timing info
WFlag = Flag()	# simply watch traffic

def setrt( args ):
	"set min reply timeout (-t system command)"
	try:
		arg = args.next()
		calc_timeout.setMin( string.atof( arg ))
	except IndexError:
		log.err( "missing timeout argument for -t flag" )
	except ValueError:
		log.err( "argument for -t flag is not a float: %s", arg )



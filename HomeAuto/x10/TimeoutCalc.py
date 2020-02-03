
import string, re

class TimeoutCalculator:
	
	"calculate timeouts, including repeat code state"

	def __init__( self, count=0 ):	# ?? would 20 be safer?
		self.count = count

		self.baseline = 0.75	# minimum
		self.increment = 0.2	# per "repeat" cycle
		self.minimum = self.baseline	# user override

	def setMin( self, minimum ):
		self.minimum = minimum

	def is_repeat_cmd( self, code ):
		"command is repeat count command"
		return re.match( "R\d\d", code )

	def is_repeatABLE_cmd( self, code ):
		"command is a repeatABLE command"
		return re.match( ".BR|.DI", code )

	def __call__( self, code ):

		"calculate timeout based on command history to date"

		timeout = self.baseline

		if self.is_repeat_cmd( code ):
			self.count = string.atoi( code[1:] )
			
		elif self.is_repeatABLE_cmd( code ):
			timeout += self.count * self.increment

		return max( timeout, self.minimum )


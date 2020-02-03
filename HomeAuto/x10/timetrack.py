## track/report timing statistics

import time

class TimeTracker:
	def __init__( self ):
		self.commandCount = 0

	def countCommand( self, count=1 ):
		self.commandCount += count

	def time( self, function, args ):
		"run a command and track total elapsed time"

		startTime = time.time()
		
		function( args )

		total = time.time() - startTime
		
		print "total runtime:", "%6.3f" % total,

		if self.commandCount:
			print "%6.3f" % ( total / self.commandCount ), 
			print "per", self.commandCount, "command(s)"
		else:
			print


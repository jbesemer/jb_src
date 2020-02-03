## TODO:
#
#	consolidate Tracker and Listener
#
#	reconstruct state from portion of logfile
#

import thread
from LockedList import *
from util import *

def onoff( state ):
	if state:	return "ON"
	else:		return "OFF"

class Unit:
	def __init__( self, addr ):
		self.addr = norm_addr( addr )
		self.state = None
		self.watchers = LockedList()
		self.min = 0
		self.max = 20
		self.dim = 20

	def __repr__( self ):
		return "%s=( %s, %d )" % ( self.addr, onoff( self.state ), self.dim )

	def add( self, watcher ):
#		print "add watcher", self.addr
		self.watchers.add( watcher )

	def rem( self, watcher ):
		while watcher in self.watchers:
#			print "rem watcher", self.addr
			self.watchers.rem( watcher )

	def put( self ):
		print "sending to", len( self.watchers ), "watchers"
		self.watchers.put( `self` + '\n' )

	def command( self, cmd, count ):

		if cmd == "ON":
			self.state = 1
			self.put()

		elif cmd == "OF":
			self.state = 0
			self.put()

		elif cmd == "DI":
			self.dim -= count
			if self.dim < self.min:
				self.dim = self.min
			self.put()

		elif cmd == "BR":
			self.dim += count
			if self.dim > self.max:
				self.dim = self.max
			self.put()

		else:
			print "# unrecognized code (%s) for unit %s" % ( cmd, self.addr )

class Tracker:
	def __init__( self ):
		self.lock = thread.allocate_lock()
		self.units = {}
		self.pending = []
		self.count = 0

	def addunit( self, unit ):
		self.units[ unit.addr ] = unit

	def __getitem__( self, addr ):
		return self.units[ norm_addr( addr )]

	def remall( self, watcher ):
		self.lock.acquire()
		for unit in self.units.values():
			unit.rem( watcher )
		self.lock.release()

	def put( self, code ):
		if not code:
			return

		if len( code ) >= 4 and ( code[0] == '!' or code[0] == '>' ):
			code = code.upper()
			addr = code[1:]

			if addr[0] == 'R':
				self.count = int( unit )

			elif addr[1] in ['0', '1']:
				self.lock.acquire()
				self.pending.append( addr )
				self.lock.release()

			else:
				self.lock.acquire()
				try:
					cmd = addr[1:]

					for pend in self.pending:
						if addr[0] == pend[0]:
							unit = self.units[ pend ]
							unit.command( cmd, self.count )

					if cmd in [ "ON", "OF" ]:
						self.pending = []
					else:
						for pend in self.pending[:]:
							if pend[0] <> addr[0]:
								self.pending.remove( pend )

				finally:
					self.lock.release()
		else:
			print "# Unrecognizable code: %s" % code

	def send( self, code ):
		self.put( code )



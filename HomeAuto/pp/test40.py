import os, sys, string
import socket, thread, time
import select

N = 40

class GuardedCounter:
	def __init__( self, init = 0 ):
		self.lock = thread.allocate_lock()
		self.count = init
	
	def get( self ):
		self.lock.acquire()
		val = self.count
		self.lock.release()
		return val
	
	def inc( self ):
		self.lock.acquire()
		self.count += 1
		val = self.count
		self.lock.release()
		return val
		
def delay( sec ):
	select.select( [], [], [], sec )
	

started = GuardedCounter()
stopped = GuardedCounter()
prlock = thread.allocate_lock()

def pr( args ):
	prlock.acquire()
	print args
	prlock.release()

def test( pid ):
	global started, stopped

	started.inc()
	pr(( "starting", pid, started.get()))

	while started.get() < N - 1:
		delay( 0.1 )

	stopped.inc()
	pr(( "stopping", pid, stopped.get()))
	thread.exit()



for pid in xrange( N ):
	thread.start_new_thread( test, ( pid, ))

while stopped.get() < N - 1:
	time.sleep( 0.1 )
	prlock.acquire()
	print "waiting", started.get(), stopped.get()
	sys.stdout.flush()
	prlock.release()

pr(( "exiting..." ))

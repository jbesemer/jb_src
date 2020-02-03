import thread
import time

print "imported tracethread"

ActiveLocks = {}

class allocate_lock:
	def __init__( self ):
		self.lock = thread.allocate_lock()
		ActiveLocks[ self ] = 1
		self.acquired = 0

	def __del__( self ):
		del ActiveLocks[ self ]

	def acquire( self ):
		self.lock.acquire()
		self.acquired = time.time()

	def release( self ):
		self.acquired = 0
		self.lock.release()


def trace_start_new_thread( func, args ):
	print "Starting thread"
	try:
		func( *args )
	finally:
		print "Thread exits"

def start_new_thread( func, args ):
	thread.start_new_thread( trace_start_new_thread, ( func, args ))


def trace( mod, state="" ):
	print "%s[%d] %s\n" % ( mod, thread.get_ident(), state ),


def LockWatcher():
	while 1:
		time.sleep( 1 )
		for lock in ActiveLocks.keys():
			if lock.acquired and time.time() - lock.acquired > 3:
				print "lock frozen"

def StartLockWatcher():
	start_new_thread( LockWatcher, ())

StartLockWatcher()





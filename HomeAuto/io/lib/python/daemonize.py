
import os, sys

DEBUG = 0

####################################################
# perform checklist of items to make process a daemon
#
# there is a "DEBUG" mode, where many steps are skipped
####################################################

def Daemonize( name=None ):

	"""perform checklist of items to make process a daemon"""

	# detach the current process

	if not DEBUG: 
		if os.fork(): 
			os._exit(0)

	# close connection to current console

	if not DEBUG: 
		os.close( sys.__stdin__.fileno())
		os.close( sys.__stdout__.fileno())
		os.close( sys.__stderr__.fileno())

	# reroute stdin to dev_null

	dev_null = open( "/dev/null" )

	sys.stdin = dev_null

	# create new os session

	if not DEBUG: 
		os.setsid()

	# fork again to ensure Init is parent

	if not DEBUG: 
		if os.fork(): 
			os._exit(0)

	register( name )

####################################################
# register the current proc's PID in a common location
####################################################

import os, sys

ROOT="/home/jb/bin/pids"

def register( appname=None ):

	if not appname:
		appname = sys.argv[0].lower()
		if appname[-3:] == ".py":
			appname = appname[:-3]

	filename = os.path.join( ROOT, appname )

	pidfile = open( filename, "w" )
	pidfile.write( str( os.getpid()) + "\n" )
	pidfile.close()


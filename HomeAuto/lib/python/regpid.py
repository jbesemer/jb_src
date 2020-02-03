
###############################################
# register the current proc's PID in a common location
###############################################

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


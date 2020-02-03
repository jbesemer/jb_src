#! env python

import os, os.path, time
import sys

import Friends
import Password

LOG_FOLDER = "@Logs"

def Main( args ):
	t = time.localtime()
	fn = ( "%04d-%02d-%02d"
		% ( t.tm_year, t.tm_mon, t.tm_mday ))
	ts = ( "%02d:%02d:%02d" 
		% ( t.tm_hour, t.tm_min, t.tm_sec ))

	friends = Friends.Main([ Password.PASSWORD ])

	out = open( os.path.join( LOG_FOLDER, fn ), "at" )
	print >>out, ts, ",".join( friends.GetNames()) 
	out.close()

if __name__ == "__main__":	
	Main( sys.argv[ 1: ])

#! env python

import os, os.path, time
import sys

import Friends
import Password

REPEAT_INTERVAL = 3.0 * 60		# repeat every 3 minutes (20 times per hour)

def UpdateFriends( password ):
	t = time.localtime()
	fn = ( "%04d-%02d-%02d"
		% ( t.tm_year, t.tm_mon, t.tm_mday ))
	ts = ( "%02d:%02d:%02d" 
		% ( t.tm_hour, t.tm_min, t.tm_sec ))

	out = open( os.path.join( Friends.LOG_FOLDER, fn ), "at" )
	print >>out, ts, ",".join( Friends.GetFriendsNames( password )) 
	out.close()

def Main( args ):
	try:
		from Password import PASSWORD
		password = PASSWORD
	except OSError:
		print "Error: missing password file"
		return

	if len(args) >= 1 and args[0] == "-once":
			UpdateFriends(password)
	else:
		while True:
			UpdateFriends(password)
			time.sleep( REPEAT_INTERVAL )

if __name__ == "__main__":	
	Main( sys.argv[ 1: ])

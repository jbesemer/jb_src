#! env python

import os, os.path
import time

import Friends
import Play

SPECIAL_FRIENDS = [ 			# case sensitive
	"December Jewell", 
	"Natalina DeVinna",
	"Ulver Voight",
	"Aisha Yao",
	]
	
SPECIAL_ONLINE = "Windows XP Balloon.wav"
SPECIAL_OFFLINE = "Windows Feed Discovered.wav"
REPEAT_INTERVAL = 5.0 # seconds

def WatchFriends( password, special=[]):
	previous = []
	onSince = {}
	offSince = {}
	
	while True:
		online = Friends.GetFriendsNames( password )
		playArrival = playDeparture = False
		
		for friend in online:
			if friend not in previous:
				onSince[ friend ] = Timestamp()
				print friend, "came online", onSince[ friend ]
				if friend in special:
					playArrival = ( previous )
				
		for friend in online:
			if friend in previous:
				print friend, "on since", onSince[ friend ]

		for friend in previous:
			if friend not in online:
				offSince[ friend ] = Timestamp()
				print friend, "went offline", offSince[ friend ]
				if friend in special:
					playDeparture = True
				
		if playArrival:
			Play.Play( SPECIAL_ONLINE )
		if playDeparture:
			Play.Play( SPECIAL_OFFLINE )
			
		previous = online
		time.sleep( REPEAT_INTERVAL )
		print

def Timestamp():
		return "%02d:%02d:%02d" % time.localtime()[3:6]
	
def Main( args ):
	password = ""
	names = []
	
	for arg in args:
		if arg.startswith("-p"):
			password = arg[2:]

		elif arg in ["-default", "-file"]:
			try:
				from Password import PASSWORD
			except OSError:
				print "Error: missing password file"
				return
			else:
				password = PASSWORD
		
		else:
			names.append( arg )
			
	if not password:
		print "Must specify password."
		return
		
	if not names:
		names = SPECIAL_FRIENDS 
		
	WatchFriends( password, names )

if __name__ == "__main__":
	import sys
	
	Main( sys.argv[ 1: ])

import os, sys
sys.path.append( "/home/jb/lib/python" )

import send
import popen2

HOME="/home/jb"
JB = "jb@cascade-sys.com"
send.SaveFlag = 1

Logs = [( 30,	"apps/sund.log" ),
	( 100,	"actd/actd.log" ),
	( 60,	"io/io.log" ),
	( 20,	"sound/soundserver.log" ),
	( 100,	"x10/x10.log" ),
	]

msg = send.Message(
	send.TextAttachment( 
		"Summary of recent Igor daemon logs." ),
	to=JB,
	su="Daily Logs" )

for lines, log in Logs:
	path = os.path.join( HOME, log )

	co, ci = popen2.popen2( "tail -" + `lines` + " " + path )
	data = co.read()
	co.close()
	ci.close()

	# msg.addBody( send.TextAttachment( data, name=log ))
	msg += send.TextAttachment( data, name=log )

msg.send()

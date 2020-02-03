
# serial I/O device

import popen2
import whereami

# constants

TTY0 = "/dev/ttyS0"
TTY1 = "/dev/ttyS1"
ttyi = 0
ttyo = 0

# default TTY depends on host

if whereami.HOST == "cascade":
	TTY = TTY1
else:
	TTY = TTY0

# send break to tty

def SendBreak():
	ioctl( ttyo.fileno(), IOCTL.TCSBRK, 0 )

# write to tty

def send( cmd ):
	ttyo.write( "\n" + cmd + "\n" )
#	print "CMD:", cmd

def normPin( pin ):
	return pin[0] + chr( ord('@') + int( pin[1:]))

def set( pin, value ):
	send( "A" + normPin( pin ) + `value` )

# init TTY

INIT_COMMAND = "init_tty"

def Init( tty = TTY ):

	print "# using", tty

	global ttyi, ttyo
	ttyi = open( tty, "rb" )
	ttyo = open( tty, "wb" )

	print "# TTY Initialization"
	
	init = popen2.Popen4( INIT_COMMAND )
	init.wait()
	print init.fromchild.read()
	
	print "# END TTY Initialization"

	# rc = os.system( INIT_COMMAND )
	# if rc:
	# 	print "# system() return", rc 


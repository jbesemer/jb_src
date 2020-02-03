
# serial I/O device

import os
from LogFile import outcs

TTY0 = "/dev/ttyS0"
TTY1 = "/dev/ttyS1"
ttyi = 0
ttyo = 0

def SendBreak():
	ioctl( ttyo.fileno(), IOCTL.TCSBRK, 0 )

def send( cmd ):
	ttyo.write( "\n" + cmd + "\n" )
#	print "CMD:", cmd

def normPin( pin ):
	return pin[0] + chr( ord('@') + int( pin[1:]))

def set( pin, value ):
	send( "A" + normPin( pin ) + `value` )

# init TTY

def Init( tty = TTY1 ):
	
	global ttyi, ttyo
	ttyi = open( tty, "rb" )
	ttyo = open( tty, "wb" )

	outcs( "TTY Initialization" )
	rc = os.system( "init_tty" )
	if rc:
		print "# system() return", rc 


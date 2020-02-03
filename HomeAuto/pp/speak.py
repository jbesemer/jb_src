import os
import string

__all__ = [ "speak", "speakfile" ]

SPEAKFILE = "/home/jb/bin/cmdlinespeakfile"

os.environ[ "ECIINI" ] = "/usr/lib/ViaVoiceTTS/eci.ini"  
			# speech app needs this

def speak( data ):
	o, i = os.popen2([ SPEAKFILE, "-" ])
	o.write( data )
	o.close()
	res = i.read()
	i.close()
	return res

def speakfile( filename ):
	o, i = os.popen2([ SPEAKFILE, filename ])
	o.write( "" )
	o.close()
	res = i.read()
	i.close()
	return res

def say_ipaddr( addr ):
	return string.replace( 
		string.join( addr, " " ), 
		".", 
		" dot " )

if __name__ == "__main__":
	print speak( "this is only a test" )


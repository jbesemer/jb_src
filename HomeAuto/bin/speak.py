import os

__all__ = [ "speak" ]

SPEAK = "/home/jb/bin/cmdlinespeakfile -"

def speak( data ):
	o, i = os.popen2( SPEAK )
	o.write( data )
	o.close()
	res = i.read()
	i.close()
	return res

if __name__ == "__main__":
	print speak( "this is only a test" )

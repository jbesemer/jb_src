import os, time
import types

__all__ = [ "playsounds", "playsoundfile" ]

PLAY = "/usr/bin/play"
SOUNDROOT = "/home/jb/sounds/"

def playsoundfile( soundfile ):
	return os.system( PLAY + " " + soundfile )

def playsounds( sounds ):
	if type( sounds ) is types.StringType:
		return playsoundfile( sounds )

	elif type( sounds ) is types.ListType:
		# make sure files are cached before playing them
		for sound in sounds:
			file = open( sound, 'r' )
			file.read()
			file.close()
		for sound in sounds:
			stat = playsoundfile( sound )
			if stat != 0:
				return stat
		return 0

if __name__ == "__main__":
	# playsounds([ SOUNDROOT + "thundernlightning.wav" ])
	playsounds([ SOUNDROOT + "ringout.wav" ])
	playsounds( SOUNDROOT + "ringin.wav" )

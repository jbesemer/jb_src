#!/python24/python.exe

import os
import sys
import time
import winsound

# optional flags

ASYNC = winsound.SND_ASYNC
NOWAIT = winsound.SND_NOWAIT
NOSTOP = winsound.SND_NOSTOP
PURGE = winsound.SND_PURGE
LOOP = winsound.SND_LOOP
NODEFAULT = winsound.SND_LOOP

# prohibited flags
BAD_FLAGS = ( winsound.SND_ALIAS 
		| winsound.SND_FILENAME 
		| winsound.SND_MEMORY 
		)

#default flags
FLAGS = 0

# there's an optional search path for sound files
SOUNDPATH_KEY = "SOUNDPATH"
DEFAULT_SOUNDPATH = "e:/windows/media;e:/windows/media/Sounds"

try:
	SOUNDPATH = os.environ[ SOUNDPATH_KEY ].split( ";" )
except KeyError:
	SOUNDPATH = DEFAULT_SOUNDPATH.split( ";" )


# command line synonyms for sounds
SYNONYM = {
	"*": 		"@SystemAsterisk",
	"!": 		"@SystemExclamation",
	"?":		"@SystemQuestion",
	"&":	 	"@SystemExit",
	"-exit": 	"@SystemExit",
	"-quit": 	"@SystemExit",
	"-hand":	"@SystemHand",
	"-stop":	"@SystemHand",
	"-quest":	"@SystemQuestion",
	"-question": "@SystemQuestion",
	}
	
#command line keys for flags
FLAG_MAP = {
	"+async":		ASYNC,
	"+nowait":		NOWAIT,
	"+nostop":		NOSTOP,
	"+purge":		PURGE,
	"+loop":		LOOP,
	"+nodefault":	NODEFAULT,
	}

class PlayException( Exception ):
	""" certain exceptions are raised by this module """
	def __init__( self, *largs, **dargs ):
		self.largs = largs
		self.dargs = dargs
	
	def __str__( self ):
		return ( "PlayException: "
			+ " ".join( self.largs )
			+ ", ".join([ "%s='%s'" % ( key, val ) for key,val in self.dargs.items()])
			)
			
			
def Play( sound, flags=FLAGS ):
	
	if sound == "-unittest":
		play( "*" )
		play( "-stop" )
	
	if sound in SYNONYM:
		sound = SYNONYM[ sound ]
		
	flags &= ~BAD_FLAGS 
	if sound[0] == "@":
		flags |= winsound.SND_ALIAS 
		sound = sound[1:]
	else:
		flags |= winsound.SND_FILENAME
		sound = findSoundFile( sound )
		
	winsound.PlaySound( sound, flags)


def findSoundFile( basename ):
	
	if os.path.isfile( basename ):
		return basename
		
	for path in SOUNDPATH:
		filename = os.path.join( path, basename )
		if os.path.isfile( filename ):
			return filename

	if basename.startswith('"') and basename.endswith('"'):
		return findSoundFile( basename[1:-1])
			
	if basename[-4:].lower() != ".wav":
		return findSoundFile( basename + ".wav" )
		
	raise PlayException( "Cannot find sound file", filename=basename )
	
	
if __name__ == "__main__":
	if len( sys.argv ) > 1:
		flags = 0
		for sound in sys.argv[1:]:
			if sound in FLAG_MAP:
				flags |= FLAG_MAP[ sound ]
			else:
				Play( sound, flags )
				if flags:
					time.sleep( 0.2 )
				
		if flags & ASYNC:
			time.sleep( 3 )
	else:
		print "Syntax: play soundName..."
		Play( "-stop" )

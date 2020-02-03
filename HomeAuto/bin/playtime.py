import os, time, types
import playsounds 

__all__ = [ "playtime" ]

CLOCK = playsounds.SOUNDROOT + "CalcCardsNClock/"

TA_AM = "taam.wav"
TA_PM = "tapm.wav"
TA_OC = "taoclock.wav"
TA_WAV = "ta%d.wav" 
TA_HEAD = "theader.wav"

PLAY_HEADING = 0

def playtime0( hr, mi, pm = 0 ):
	if hr < 12:
		ampm = TA_AM
	else:
		ampm = TA_PM
	hr = hr % 12
	if hr == 0:
		hr = 12

	mit = ( mi / 10 ) * 10
	miu = mi % 10

	# print hr,":",mi

	if PLAY_HEADING:
		sounds = [ CLOCK + TA_HEAD, CLOCK + ( TA_WAV % hr )]
	else:
		sounds = [ CLOCK + ( TA_WAV % hr )]

	if mi == 0:
		sounds.append( CLOCK + TA_OC )

	elif mi < 10:
		sounds.append( CLOCK + ( TA_WAV % 0 ))
		sounds.append( CLOCK + ( TA_WAV % mi ))

	elif mi <= 20:
		sounds.append( CLOCK + ( TA_WAV % mi ))

	else:
		sounds.append( CLOCK + ( TA_WAV % mit ))
		if miu != 0:
			sounds.append( CLOCK + ( TA_WAV % miu ))

	sounds.append( CLOCK + ampm )
	playsounds.playsounds( sounds )

def playtime( timetuple = None ):

	if type( timetuple ) is types.FloatType:
		timetuple = time.localtime( timetuple )

	if not timetuple:
		timetuple = time.localtime()

	if len( timetuple ) < 3:
		playtime0( timetuple[ 0 ], timetuple[ 1 ])
	else:
		playtime0( timetuple[ 3 ], timetuple[ 4 ])


def unittest():
	playtime( time.time())

	playtime(( 0, 46 ))
	playtime(( 0, 40 ))
	playtime(( 0, 00 ))
	playtime(( 0, 01 ))
	playtime(( 0, 13 ))
	playtime(( 0, 20 ))
	playtime(( 0, 21 ))
	playtime(( 3, 41 ))


if __name__ == "__main__":
	playtime( None )


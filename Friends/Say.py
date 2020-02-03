#! env python

import sys
import win32com.client

SERVICE = "SAPI.SpVoice"
SpVoice = win32com.client.Dispatch( SERVICE )

def Say( *words ):
	try:
		SpVoice.Speak( " ".join( words ))
	except:
		import traceback
		traceback.print_exc()
		print "[CONTINUING...]"

def SetVolume(level):		SpVoice.SetVolume(level)
def GetVolume(): 			SpVoice.GetVolume()
def GetVoiceNames():		SpVoice.GetVoiceNames()
def GetVoice():				SpVoice.GetVoice()
def SetVoiceByName(name):	SpVoice.SetVoiceByName(name)
def GetRate():				SpVoice.GetRate()
def SetRate(rate):			SpVoice.SetRate(rate)

if __name__ == "__main__":
	if len( sys.argv ) > 1:
		Say( *sys.argv[1:])
	else:
		print "Syntax: say text..."
		Say( "specify text to be spoken as command arguments" )
	

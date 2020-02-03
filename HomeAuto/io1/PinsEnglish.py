Phonetic = [
	"Alfa",
	"Bravo",
	"Charlie",
	"Delta",
	"Echo",
	"Foxtrot",
	"Golf",
	"Hotel",
	"India",
	"Juliet",
	"Kilo",
	"Lima",
	"Mike",
	"November",
	"Oscar",
	"Papa",
	"Quebec",
	"Romeo",
	"Sierra",
	"Tango",
	"Uniform",
	"Victor",
	"Whiskey",
	"X-Ray",
	"Yankee",
	"Zulu",
	]

def NormalPin( pin ):
	"remove leading zero on 2 digit pin name"
	if pin[1] == '0':
		pin = pin[0] + ( "%d" % int( pin[1:]))
	return pin

def PhoneticBank( bank ):
	return Phonetic[ ord( bank.lower()) - ord( 'a' )] 

def PhoneticPin( pin ):
	"convert bank letter to phonetic name"
	pin = NormalPin( pin )
	return ( 
		PhoneticBank( pin[0].lower())
		+ " "
		+ pin[1:]
		)

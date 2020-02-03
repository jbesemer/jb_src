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

Ordinary = [
	"Ae",
	"Bee",
	"Cee",
	"Dee",
	"Eee",
	"Ef",
	"Gee",
	"aitch",
	"eye",
	"Jay",
	"Kay",
	"Ell",
	"em",
	"en",
	"oh",
	"Pee",
	"Queue",
	"Are",
	"ess",
	"tee",
	"you",
	"vee",
	"double ewe",
	"ex",
	"why",
	"zee",
	]

def NormalPin( pin ):
	"remove leading zero, if any, on 2 digit pin name"
	if pin[1] == '0':
		pin = pin[0] + pin[2:]
	return pin

def PhoneticBank( bank ):
	return Phonetic[ ord( bank.lower()) - ord( 'a' )] 

def OrdinaryBank( bank ):
	return Ordinary[ ord( bank.lower()) - ord( 'a' )] 

def PhoneticPin( pin ):
	"convert bank letter to phonetic name"
	pin = NormalPin( pin )
	return ( 
		PhoneticBank( pin[0].lower())
		+ " "
		+ pin[1:])

def OrdinaryPin( pin ):
	"convert bank letter to letter + number"
	pin = NormalPin( pin )
	return ( 
		OrdinaryBank( pin[0].lower())
		+ " "
		+ pin[1:])


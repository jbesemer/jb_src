
# sex encoding/decoding ###############################################

import sys

SEX_NAME_FILENAME = "FirstNames.txt"	# file containing name->sex hints

# report unions of same-sex partners
REPORT_SAME_SEX_UNIONS = True		
			# Note: this is NOT Homophobia, but an integrity check,
			# to help debug the sex inference algorithm & database.

# report inferences from title
REPORT_INFERENCE_FROM_TITLE = True

# report inferences from union
REPORT_INFERENCE_FROM_UNION = True

# There are only 3 immutable instances of these classes, shared by all

class SexObject( object ):
	""" represent the sex of a person, when the sex is unknown """
	
	def __nonzero__( self ): 	return False	# sex is unknown
	def Opposite( self ):		return self		# opposite of unk is still unk
	def GetTitle( self ):		return "Spouse"
	def __str__( self ):		return "?"
		
class MaleSexObject( SexObject ):
	def __nonzero__( self ):	return True # yes, sex is known
	def Opposite( self ):		return Female
	def GetTitle( self ):		return "Husband"
	def __str__( self ):		return "M"

class FemaleSexObject( MaleSexObject ):
	def Opposite( self ):		return Male
	def GetTitle( self ):		return "Wife"
	def __str__( self ):		return "F"


# Sex Literals ########################################################

# since these are singletons and the only possibilities,
# then == works as expected

Unk = SexObject()
Male = MaleSexObject()
Female = FemaleSexObject()


LetterMap = {
	"m":	Male,
	"f":	Female,
	}

# Table to lookup sex from names ######################################

class SexByNameMap( dict ):
	""" Dictionary mapping names -> sex """
	
	def __init__( self, filename=None ):
		dict.__init__( self )
		if filename:
			self.Load( filename )
	
	def Load( self, filename ):
		global Unk, Female, Male
		
		for line in open( filename ):
			if line.strip():		# ignore blanks
				if line[0] == "\t":
					if line[1] == "\t":
						sex = Unk
					else:
						sex = Female
				else:
					sex = Male
				self[ line.strip().lower()] = sex

	def ListDifferences( self, inputfilename ):
		FindDifferences( self, inputfilename, sys.stdout, prefix="# New: " )
			
	def SaveDifferences( self, inputfilename, outputfilename ):
		output = file( outputfilename, "wt" )
		FindDifferences( self, inputfilename, output )
		
	def FindDifferences( self, inputfilename, output, prefix="" ):
		newNames = {}
		for line in file( inputfilename ):
			name = line.strip().lower() 
			if name and name not in self and name not in newNames:
				if prefix:
					out.write( prefix )
				print >>out, name
				newNames[ name ] = 1

	def __getitem__( self, name ):
		try:
			return dict.__getitem__( self, name.strip().lower())
		except ( KeyError, AttributeError ):
			pass
		return Unk

# Singleton instance of name-sex dictionary

InferSexFromName = SexByNameMap( SEX_NAME_FILENAME )

# Sex Objects #########################################################

# Sex Inference Functions #############################################

def InferSexFromNames( firstName, secondName ):
	return (	
			InferSexFromName[ firstName ]
		or	InferSexFromName[ secondName ]
		or	Unk )

def InferSexFromUnion( union ):
	""" If sex of just one of the partners is indeterminate, 
		then we may presume (!) to infer his or her sex 
		from that of the other partner.
	"""
	if union.a.sex and union.b.sex:
		# both have sex, nothing to infer
		if union.a.sex == union.b.sex and REPORT_SAME_SEX_UNIONS:
			print ("# Warning: possible homosexual partnership:", union.a, "AND", union.b)
		return
		
	if union.a.sex and not union.b.sex:
		union.b.sex = union.a.sex.Opposite()
		
	if not union.a.sex and union.b.sex:
		union.a.sex = union.b.sex.Opposite()
		
	# else: neither has sex, no inference can be made,
	# nothing to be done
		
def InferSexFromTitle( person, title ):
	""" Infer sex from title if any """
	# this is a pretty strong clue, so it overrides names

	if Male.GetTitle().lower() in title.lower():
		person.sex = Male
		if REPORT_INFERENCE_FROM_TITLE:
			print ("Infer Male for", person)

	elif Female.GetTitle().lower() in title.lower():
		person.sex = Female
		if REPORT_INFERENCE_FROM_TITLE:
			print ("Infer Male for", person)

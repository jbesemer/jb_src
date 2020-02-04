#!/usr/bin/env python

import sys

import Sex
import GenieDB
import Date

# Configuration Control ###############################################
if 1: # for folding
	# These settings affect how the program operates.  Some are for 
	# debugging.  Others are optional, but produce important results.
	
	# Disambiguate successors/predecessors who have the exact same names 
	# by adding a roman number suffix.  Oldest relative has no suffix, 
	# first scion is called "II", etc.
	DISAMBIGUATE_SCIONS = True	
	
	# report each scion relationship detected, whether resolved or not
	REPORT_SCIONS = False		
					
	# Disambiguate non-scions who happen to have the exact same names 
	# by adding an arabic number suffix. First relative entered with 
	# the name has no suffix, first namesake gets "(2)", etc.
	DISAMBIGUATE_NAMESAKES = True	
	
	# report each namesake relationship detected, whether resolved or not
	REPORT_NAMESAKES = False	
	
	# try to infer sex of individual from first and middle names
	INFER_SEX_FROM_NAME = True	
	
	# try to infer sex of individual, if indeterminate, from partner
	INFER_SEX_FROM_UNION = True	
	
	# try to infer sex of individual, if indeterminate, from other hints
	INFER_SEX_FROM_TITLE = False
	
	# report each person who's sex cannot be determined
	REPORT_UNK_SEXES = True		
	
	# report names that do not appear in our sex-name database
	REPORT_NEW_NAMES = False	
	
	# report all first and middle names in the entire family
	REPORT_ALL_NAMES = False
	
	# include person's sex when printing 
	INCLUDE_SEX_IN_PERSON_STR = False
	
	# include person's ID when printing 
	INCLUDE_INDEX_IN_PERSON_STR = True
	
	# trace DB inserts
	TRACE_DB_INSERTS = True
	
	# trace Date extraction
	TRACE_DATE_EXTRACTION = False
	
	# trace data import
	TRACE_TEXT_IMPORT = False

# Constants ###########################################################

import Sex

# quick and dirty conversions to roman numerals and ordinal names;
# good enuf for gov't work. the 0th case "cannot" happen, and the
# 1st cases also are never used as a matter of policy.

ROMAN = [ "[ZERO]", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X" ]

# quick and dirty lookup of ordinal names:

def ORDINAL( n ):
	assert n > 1
	try:				return [ "ZED", "1st", "2nd", "3rd" ][ n ]
	except IndexError:	return "%dth" % ( n )


# Globals #############################################################

People = []			# list of all people, indexed by idPerson
Unions = []			# list of all marriages, indexed by idUnion

PeopleStack = {}	# recent descendants, indexed by level
UnionsStack = {}	# recent unions, indexed by level
Level = 0			# most recent level


# Object to represent Unions ##########################################

class Union( object ):
	""" represent the union of two people """

	def __init__( self, a, b ):
		self.a = a
		self.b = b
		b.level = a.level
		a.marriage = b.marriage = self
		self.children = []

		if INFER_SEX_FROM_UNION:
			Sex.InferSexFromUnion( self )

		self.Date, self.Place = ExtractDateAndPlace( 
						b.attr.get( "m", 
							a.attr.get( "m", "" )))

		self.EndDate, _unused_ = ExtractDateAndPlace( 
						b.attr.get( "x", 
							a.attr.get( "x", "" )))

		Unions.append( self )
		self.idUnion = len( Unions )

	def GetDate( self ):		return self.Date
	def GetPlace( self ):		return self.Place
	def GetEndDate( self ):		return self.EndDate
		
	def AddOffspring( self, child ):
		self.children.append( child )

	def Export( self, index, out=sys.stdout ):
		if index > 1:
			print >>out, "+", ORDINAL( index ), self.b.sex.Title(), "OF", self.a
		print >>out, self
		for child in self.children:
			child.Export( out )

	def InsertDb( self ):
		if TRACE_DB_INSERTS:
			print ("... Inserting Union:", self.idUnion)

		GenieDB.DbExecute( 
			GenieDB.Unions({
				"idUnion":			self.idUnion,
				"idPerson_A":		self.a.idPerson,
				"idPerson_B":		self.b.idPerson,
				"StartDate":		str( self.GetDate()),
				"EndDate":			str( self.GetEndDate()),
				"Location":			self.GetPlace(),
			}).AsSQLInsert())	\
				.Commit()
				
		for child in self.children:
			if TRACE_DB_INSERTS:
				print ("... Inserting Child:", self.idUnion, child.idPerson)
			GenieDB.DbExecute( 
				GenieDB.Offspring({
					"Parents": 		self.idUnion,
					"Offspring": 	child.idPerson,
				}).AsSQLInsert())	\
					.Commit()
			

	def __str__( self ):
		return "Union #%d: %s  %s  %s" % ( self.idUnion, str( self.b ), self.title, str( self.a ))

# Object to represent individual People ###############################

class Person( object ):
	def __init__( self, lexeme, parents=None, title=None  ):
		self.name = lexeme.name
		self.attr = lexeme.attr
		self.line = lexeme.line
		self.fields = lexeme.fields
		self.level = lexeme.level
		
		self.parents = None
		
		self.idPerson = len( People ) + 1
		self.qualifier = 1
		self.scion = 1

		if title:	self.title = title + " OF"
		else:		self.title = "AND"

		try:
			self.sex = Sex.LetterMap[ self.attr[ "s" ].lower()]
		except KeyError:
			self.sex = Sex.Unk
			
		if INFER_SEX_FROM_TITLE:
			Sex.InferSexFromTitle( self, title )

		if INFER_SEX_FROM_NAME and not self.sex:
			self.sex = Sex.InferSexFromNames( 
							self.GetFirstName(), 
							self.GetMiddleName())

		self.BirthDate, self.BirthPlace = ExtractDateAndPlace( self.attr.get( "b", "" ))	
		self.DeathDate, self.DeathPlace = ExtractDateAndPlace( self.attr.get( "d", "" ))
		
		self.AddParents( parents )
		self.DisambiguateName()
		People.append( self )

	def AddParents( self, parents ):
		if parents:
			assert self.parents == None
			self.parents = parents
			parents.AddOffspring( self )
			self.DisambiguateSuccessors( parents )

	def DisambiguateSuccessors( self, parents ):
		""" if a person is named after any direct predecessor, 
			then we qualify the successors' names with roman numerals 
		"""
		# this takes precedence over disambiguating other name matches.
		
		# check parents
		if self.name == parents.a.name:
			self.scion = parents.a.scion + 1
			if REPORT_SCIONS:
				print ("## Scion:", self, "TO", parents.a)
		elif self.name == parents.b.name:
			self.scion = parents.b.scion + 1
			if REPORT_SCIONS:
				print ("## Scion:", self, "TO", parents.b)
			
		# Recursively check all other predecessors.
		# Since at this point, all prior scions have been detected,
		# we can stop after the first match.

		if parents.a.parents:
			self.DisambiguateSuccessors( parents.a.parents )
		if parents.b.parents:
			self.DisambiguateSuccessors( parents.b.parents )
	
	def DisambiguateName( self ):
		""" if two relataives on different branches share the same name, 
			we distinguish them with numeric suffixes.  
			This is done after any Roman numerals have been added.
		"""
		namesake = FindPersonOnList( self.GetName())
		if namesake:
			self.qualifier = namesake.qualifier + 1
			if REPORT_NAMESAKES:
				print ("## Namesake:", self, "AND", namesake)
		
	def GetFirstName( self ):
		fields = self.name.split()
		if len( fields ) > 1:	return fields[ 0 ]
		else:					return None

	def GetMiddleName( self ):
		fields = self.name.split()
		if len( fields ) > 2:	return fields[ 1 ]
		else:					return None
			
	def GetName( self ):
		""" display name with optional roman numerals, if any """
		# first realtive with name gets no qualifier
		if self.scion > 1:	return "%s (%s)" % ( self.name, ROMAN[ self.scion ])
		else:				return self.name

	def GetQualifiedName( self ):
		""" return name with optional qualifier suffix, if any """
		# first realtive with name gets no qualifier
		if self.qualifier > 1:	return "%s (%d)" % ( self.GetName(), self.qualifier )
		else:					return self.GetName()
			
	def GetBirthDate( self ):	return self.BirthDate
	def GetBirthPlace( self ):	return self.BirthPlace
	def GetDeathDate( self ):	return self.DeathDate
	def GetDeathPlace( self ):	return self.DeathPlace

	def Export( self, out=sys.stdout ):
		""" print out self, and any unions """

		print (self, file=out)
		for union, index in FindUnions( self ):
			union.Export( index, out )
			
	def InsertDb( self ):
		row = GenieDB.People({
				"Name": 		self.GetQualifiedName(),
				"idPerson": 	self.idPerson,
				"Scion":		self.scion,
				"Qualifier":	self.qualifier,
				"Sex":			str( self.sex ),
				"BirthDate":	str( self.GetBirthDate()),
				"BirthPlace":	self.GetBirthPlace(),
				"DeathDate":	str( self.GetDeathDate()),
				"DeathPlace":	self.GetDeathPlace(),
				"idParents":	self.parents and self.parents.idUnion,
			})

		if TRACE_DB_INSERTS:
			print ("... Inserting Person:", self.idPerson, self)
			# print row

		GenieDB.DbExecute( row.AsSQLInsert())	\
			.Commit()

	def __getattr__( self, attr ):
		return 

	def __repr__( self ):			return "Person( %s )" % self.name
		
	def __str__( self ):
		name = self.GetQualifiedName()
		if INCLUDE_SEX_IN_PERSON_STR:	name += " " + str( self.sex )
		if INCLUDE_INDEX_IN_PERSON_STR:	name += " #%d" % self.idPerson 
		return name


# Descendant Input File Decoding ######################################

class ParsedLine( object ):
	""" parse a line in the given format """
	
	def __init__( self, line ):
		self.token = line[0]
		self.level = Level
		self.attr = {}

		if self.token in "0123456789":		# a new offspring
			level, line = line.split( None, 1 )
			self.level = int( level )
			self.token = "0"

		elif self.token == "+":				# marriage
			line = line[1:].strip()

		elif self.token == "*":				 # nth spouse or "friend"
			line = line[1:-1].strip()
			assert " of " in line
			self.title, self.name = line.split( " of " )
			self.name = self.name.replace( ":", "" )
			self.attr = { "name": self.name }
			return

		else:								# not recognizeable
			assert 0

		# now parse the remainder: a name, followed by zero or more attributes

		self.line = line
		self.attr = {}
		self.fields = line.split()
		self.attr[ "name" ] = curVals = []
		
		for field in self.fields:
			if field[-1] == ":":
				self.attr[ field[ : -1 ]] = curVals = []
			else:
				curVals.append( field )

		nattr = {}
		for key, val in self.attr.items():
			nattr[ key ] = " ".join( val )

		self.attr = nattr
		self.name = self.attr[ "name" ]

	def __getitem__( self, key ):
		return self.attr[ key ]

	def __str__( self ):
		return (
				"%d \t" % ( self.level )
			+	"\n\t".join([ "%s: %s" % ( key, val ) 
							for key, val in self.attr.items()]))

def Reader( filename ):
	"""	yield non-empty, stripped lines in a file, 
		after skipping a premble of non-blank lines 
	"""
	src = file( filename )
	for line in src:
		if not line.strip():
			break
	for line in src:
		line = line.strip()
		if line:
			yield ParsedLine( line )

def Import( filename ):
	""" read a file in the format provided, 
		creating all people and relationships 
	"""
	
	global Level
	
	title = None
	
	for lexeme in Reader( filename ):
		if lexeme.token == "0":						# regular person
			Level = lexeme.level
			PeopleStack[ Level ] 	\
				= person 			\
				= Person( lexeme, parents=MostRecentUnionIfAny())
			if TRACE_TEXT_IMPORT:
				print (len( People ), Level, person)
			
		elif lexeme.token == "*":					# additional marriage
			person = FindPersonOnStack( lexeme.name )
			Level = person.level
			title = lexeme.title
			if False and TRACE_TEXT_IMPORT:
				print (len( People ), Level, "xUnion:", person, title)
	
		elif lexeme.token == "+":					# marriage
			spouse = Person( lexeme, title=title )
			UnionsStack[ Level ] = marriage = Union( PeopleStack[ Level ], spouse )
			if TRACE_TEXT_IMPORT:
				print (len( People ), Level, marriage)
			title = None
			
		else:
			raise "impossible token" # "cannot" happen


# Utilities ###########################################################

def FindPersonOnStack( name ):
	""" locate by name the highest-level person on the PeopleStack """
	level = Level
	while level > 0:
		if PeopleStack[ level ].name == name:
			return PeopleStack[ level ]
		level -= 1
	raise "Person not found: " + name	# "cannot happen"
	

def FindPersonOnList( name ):
	""" locate by name the most recent descendant created """
	for person in reversed( People ):
		if person.GetName() == name:
			return person
	return None

def MostRecentUnionIfAny():
	""" return the most recent union or null if there is none """
	try:
		return UnionsStack[ Level - 1 ]
	except KeyError:
		return None

def FindUnions( person ):
	""" yield all relevant unions, in order and number them """
	index = 0
	for union in Unions:
		if person in [ union.a, union.b ]:
			index += 1
			yield union, index




MONTH = {
	"jan":	1,	"feb":	2,	"mar":	3,
	"apr":	4,	"may":	5,	"jun":	6,
	"jul":	7,	"aug":	8,	"sep":	9,
	"oct":	10,	"nov":	11,	"dec":	12,
	}

def INT( s ):
	try:				return int( s )
	except ValueError:	return 0
		
def Month( mm ):
	try:
		return MONTH[ mm.lower()[:3]]
	except ( KeyError, AttributeError ):
		if type( mm ) == str and mm.isdigit():
			mm = int( mm )
		if 1 <= mm <= 31:
			return mm

#	print ("#!! error converting '%s' to month:" % mm)
	return 0
	
def DATE( yy, mm="0", dd="0" ):
	Y = INT( yy )
	M = Month( mm )
	if "," in dd:
		dd = dd.replace(",","")
	D = INT( dd )
	
	if Y > 1000:
		try:
#			print ("yymmdd:", yy, mm, dd)
			return Date.Date( Y, M, D )
		except ( ValueError, IndexError, KeyError ) as e:
			pass
	return None

def ExtractDateAndPlace( attr ):
	# Sometimes we have a date, sometimes just a place, sometimes both.
	# Furthermore, dates come in several forms: 
	#		mm-dd-yy
	#		mm-yy
	#		Month Day, Year
	#		Month Year
	#		Year only
	
	date, place = GenieDB.NullDate, ""
	fields = attr.split()
	if fields:
		remainder = 0

		if "-" in fields[0].lower():	# mm-dd-yy or mm-yy
			mmddyy = fields[0].split( "-" )
			if len( mmddyy ) == 3:
				date = DATE( mmddyy[2], mmddyy[0], mmddyy[1])
			elif len( mmddyy ) == 2:
				date = DATE( mmddyy[1], mmddyy[0])
			if date:
				remainder = 1

		elif fields[0].isdigit() and int( fields[0]) > 1000:	# Year only
			date = DATE( int( fields[0]))
			if date:
				remainder = 1

		else:							
			mm = Month( fields[0])
			if 1 <= mm <= 31:			# M D, Y; M Y; else no date
				if len( fields ) >= 3:
					date = DATE( fields[ 2 ], mm, fields[ 1 ])
				if date:
					remainder = 3
				else:
					if len( fields ) >= 2:
						date = DATE( fields[ 1 ], mm )
					if date:
						remainder = 2
					else:
						date = DATE( fields[ 0 ])
					if date:
						remainder = 1

		place = " ".join( fields[ remainder : ])
		if not date:
			date = GenieDB.NullDate

	if attr and TRACE_DATE_EXTRACTION:
		print (attr, "=>")
		print ("\t->", date)
		print ("\t->", place)
	return date, place




# Mainline and Unit Testing ###########################################

if __name__=='__main__':

	if 1:
		for filename in sys.argv[1:]:
			Import( filename )

	if 0:
		print ("# Exported Results ################################################")
		People[0].Export() # everything should follow from the first ancestor
		
	if not TRACE_DATE_EXTRACTION:
		try:
			if TRACE_TEXT_IMPORT:
				print ("#############################################################")
				print ("### Insert Trace ############################################")
				print ("#############################################################")
			GenieDB.MasterClear()
			for person in People:
				person.InsertDb()
			for union in Unions:
				union.InsertDb()
		except:
			import TraceBackVars
			exctype, value = sys.exc_info()[:2]
			print ("exception:", exctype, value )
			TraceBackVars.TraceBackVars()

	if REPORT_ALL_NAMES:
		out = file( "~CommonNames.txt", "wt" )
		for person in People:
			fn = person.GetFirstName()
			if fn:	print (fn, file=out)
			mn = person.GetMiddleName()
			if mn:	print (mn, file=out)
				
	if REPORT_NEW_NAMES:
		InferSexFromName.SaveDifferences( "~CommonNames.txt", "~NewNames.txt" )
				
	if REPORT_UNK_SEXES:
		for person in People:
			if not person.sex:
				print ("# Sex Unk:", person)

import datetime

from MyDb import *


if 0:
	class NullDateClass( datetime.date ):
		def __str__( self ): 	return ""
		
	NullDate = NullDateClass( datetime.MINYEAR, 1, 1 )
else:
	NullDate = ""
	
def MasterClear():
	for table in ALL_TABLES:
		DbExecute( table.AsSQLTruncate())
	Db.commit()

# Default Update Dicts ################################################


People = DbTableRow(
	"People",
	{
		"idPerson":			0,
		"Name":				"",
		"Scion":			0,
		"Qualifier":		0,
	}, {
		"Sex":				( "?", "M", "F" ),
		"BirthDate":		NullDate,
		"BirthPlace":		"",
		"DeathDate":		NullDate,
		"DeathPlace":		"",
		"idParents":		0,
	})

Unions = DbTableRow(
	"Unions",
	{
		"idUnion":			0,
		"idPerson_A":		0,
		"idPerson_B":		0,
	}, {
		"StartDate":		NullDate,
		"EndDate":			NullDate,
		"Location":			"",
	})

Offspring = DbTableRow(
	"Offspring",
	{
		"Parents": 			0,
		"Offspring": 		0,
	})

PhotoAssociations = DbTableRow(
	"PhotoAssociations",
	{
		"idPhoto": 			0,
		"idPerson": 		0,
	})

Photos = DbTableRow(
	"Photos",
	{
		"idPhoto": 			0,
	}, {
		"Filename": 		"",
	})

Scions = DbTableRow(
	"Scions",
	{
		"Predecessor":		0,
		"Successor": 		0,
	})

Namesakes = DbTableRow(
	"Namesakes",
	{
		"Predecessor":		0,
		"Successor": 		0,
	})


ALL_TABLES = [ 
	People, 
	Unions, 
	Offspring, 
	PhotoAssociations, 
	Photos, 
	Scions, 
	Namesakes 
	]

# parameterized queries ###############################################

def SelectPeopleByName( name ):
	name = "%" + name.replace(" ", "%") + "%"
	return "select * from people where name like '%s'" % name
	
def SelectPersonByID( id ):
	return "select * from people where idPerson='%s'" % str( id )
	
def SelectUnionsByPersonID( id ):
	return """select * from people p, Unions u 
		where ( u.idPerson_A=%d or u.idPerson_B=%d )
		and ( u.idPerson_A=p.idPerson or u.idPerson_B=p.idPerson  )
		and p.idPerson <> %d """ % ( id, id, id )

def SelectOffspringByUnionID( id ):
	return """select * from People p, Offspring o where o.Parents=%d and o.Offspring=p.idPerson""" % id
	
def SelectParentsByOffspringID( id ): 
	return """select * from People p, Unions u, Offspring o 
			where o.Offspring=%d and o.Parents=u.idUnion 
			and (p.idPerson = u.idPerson_A or p.idPerson = u.idPerson_B)""" % id
	
	
def GetPeopleByName( name ):
	return DbTable( SelectPeopleByName( name )).Execute()
	
def GetPersonByID( id ):
	return DbTable( SelectPersonByID( id )).Execute()
	
def GetUnionsByPersonID( id ):
	return DbTable( SelectUnionsByPersonID( id )).Execute()

def GetOffspringByUnionID( id ):
	return DbTable( SelectOffspringByUnionID( id )).Execute()
	
def GetParentsByOffspringID( id ):
	return DbTable( SelectParentsByOffspringID( id )).Execute()
	
def GetPersonAndRelated( id ):
	i = GetPersonByID( id )
	p = GetParentsByOffspringID( id )
	u = GetUnionsByPersonID( id )
	return i, p, u
	
def GetRelated( id ):
	p = GetParentsByOffspringID( id )
	u = GetUnionsByPersonID( id )
	return p, u
	

# Unit Test ###########################################################

if __name__ == "__main__":
	import sys, pprint

	INDENT = "    "
	
	if 0:
		print "People.enums:", People.enums

		print SQLInsert( "people", **People )

		print People.AsSQLInsert()

		p = People( Name="Fred Head")
		p.idPerson=33
		p.BirthDate = datetime.date( 2006, 8, 9 )
		p.Sex = "M"
		try:
			p.Sex = "X" # type error
		except ValueError:
			pass
		else:
			raise Error
		
		print SQLInsert( "people", **p )


	

	if 1 and len( sys.argv ) > 1:
		pp = pprint.PrettyPrinter( indent=4 )

		if len( sys.argv ) == 2:
			try:
				n = int( sys.argv[ 1 ])
			except TypeError:
				n = 22
				print "Substituting", n
			people = GetPersonByID( n ).GetData()
		else:
			people = GetPeopleByName( " ".join( sys.argv[ 1 : ])).GetData()

		if len( people ) > 1:
			print "People:"
			for pp in people:
				print pp

		else:
			person = people[ 0 ]
			parents, unions = GetRelated( person[ "idPerson" ])
			print "Person:"
			print INDENT, person[ "name" ], person[ "sex" ], "(", person[ "idPerson" ], ")"
			
			print INDENT, "Born:", person[ "BirthDate" ], person[ "BirthPlace" ]
			if person[ "DeathDate" ]:
				print INDENT, "Died:", person[ "DeathDate" ], person[ "DeathPlace" ]
			
			print "Parents:"
			for parent in parents.GetData():
				print INDENT, parent[ "name" ]
			
			print "Unions:"
			for union in unions.GetData():
				if union:
					print INDENT, 
					if union[ "Date" ]:
						print union[ "Date" ],
					print "Married:", union[ "name" ]
					if union[ "Location" ]:
						print INDENT, union[ "Location" ]
					children =  GetOffspringByUnionID( union[ 10 ]).GetData()
					if children:
						print INDENT, "Children with", union[ "name" ] + ":"
						for child in children:
							print INDENT*2, child[ "name" ], child[ "BirthDate" ], child[ "BirthPlace" ]

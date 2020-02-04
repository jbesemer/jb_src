
import os, sys
import datetime

import MySQLdb

import Date


try:
	USERNAME = os.environ[ "USERNAME" ]
	PASSWORD = os.environ[ "PASSWORD" ]
except KeyError:
	USERNAME = "root"
	PASSWORD = "Reject0"
#	print "Internal error: missing database USERNAME or PASSWORD"
#	sys.exit(0)

try:
	Db = MySQLdb.connect( db="geanie", user=USERNAME, passwd=PASSWORD )
except:
	print ("Internal error: unable to open database, possible bad USERNAME or PASSWORD?")
	
	
class DbQuery( object ):
	def __init__( self, query, Db=Db ):
		self.Db = Db
		self.Cur = Db.cursor()
		self.query = query
		self.error = False
		self.count = None

	def __len__( self ): return self.count

	def Execute( self ):
		try:
			self.count = self.Cur.execute( self.query )
			self.error = False
		except MySQLdb.IntegrityError as err:
			print ("Db Error:", err, file=sys.stderr)
			self.error = True
			self.count = 0

	def Commit( self ):
		if not self.error:
			self.Db.commit()

	
class DbExecute( DbQuery ):	
	def __init__( self, query, Db=Db ):
		DbQuery.__init__( self, query, Db )
		self.Execute()

	
class DbTable( DbQuery ):
	def __init__( self, query, Db=Db ):
		DbQuery.__init__( self, query, Db )

	class DbTableRow( object ):
		def __init__( self, table, data ):
			self.table = table
			self.FieldDict = table.FieldDict
			self.data = list(data)
			self.FieldWidths = []
	
		def GetFieldNames( self ): return self.table.FieldList
		def GetData( self ): return self.data
	
		def GetFieldWidths( self ):
			if not self.FieldWidths:
				self.FieldWidths = [ len(str(self.Normalize( item ) for item in self.data ))]
			return self.FieldWidths
		
		def Normalize( self, item ):
			if type( item ) == type( long ):
				return int( item )
				
			elif type( item ) == datetime.datetime:
				if item.hour or item.minute:
					return "%04d-%s-%02d %02d:%02d" % (
							item.year, Date.MONTH_NAMES[ item.month ], item.day, item.hour, item.minute )
				else:
					return "%04d-%s-%02d" % ( 
							item.year, self.MONTHS[ item.month ], item.day )
			return item

		def __getitem__( self, index ): 
			""" fetch a column value by index or field name """
			
			# if name then convert to index
			if type(index) == str and index.lower() in self.FieldDict.keys():
				index = self.FieldDict[ index.lower()]

			# fetch item, mapping non-x ones to None
			try:	item = self.data[ index ]
			except KeyError:	return None

			# normalize format and cache result
			item = self.data[ index ] = self.Normalize( item )
			return item

	def Execute( self ):
		DbQuery.Execute( self )
		self.description = self.Cur.description
		self.rowcount = self.Cur.rowcount
		self.data = self.Cur.fetchall()
		self.Cur.close()

		self.FieldDict = {}
		self.FieldList = []
		self.FieldWidths = []
		for i in range( len( self.description )):
			name = self.description[i][0]
			self.FieldDict[ name.lower()] = i
			self.FieldList.append( name )

		self.data = [ self.DbTableRow( self, row ) for row in self.data ]
		return self
	
	def GetFieldNames( self ): return self.FieldList
	def GetData( self ): return self.data

	def GetFieldWidths( self ):
		if not self.FieldWidths:
			self.FieldWidths = [ len( field ) for field in self.FieldList ]
			for row in self.data:
				self.FieldWidths = [ max( a, b ) for a, b in zip( self.FieldWidths, row.GetFieldWidths())]
		return self.FieldWidths

	def __getitem__( self, index ): 		
		try:
			return self.data[ index ]
		except KeyError:
			return ()



class DbTableRow( dict ):
	""" represent one row of named columns """
	# Allow access to fields via attribute, prevent extra fields
	# from being created, and enforce rudimentary type-checking on
	# field assignment.
	# Instances of this class are like meta-classes;
	# calling instances produces a new instance, a copy of the original.
	# User is expected to ensure that keys and cols are mutually disjoint.
	#
	# Todo: would like definitions to retain case of names, 
	# but access should ignore case.  Presently all must exactly match.

	def __init__( self, tableName, keys={}, cols={}, **kw ):
		dict.__init__( self )			# self is the master key->val map
		self.__dict__[ "enums" ] = {}	# dict of enum mappings
		self.__dict__[ "keys" ]  	\
					= keys.keys()		# list of key names
		self.__dict__[ "cols" ] 	\
			= cols.keys() + kw.keys()	# list of other col names
		
		self.update( keys )
		self.update( cols )
		self.update( kw )

		self.__dict__[ "tableName" ] = tableName

		# list or tuple values => enum, w/1st element the default
		for key, val in self.items():
			if type( val ) in [ type([]), type(())]:
				self.enums[ key ] = val
				self[ key ] = val[0]
		
	def GetKeys( self ):
		return dict([( key, self[ key ])
					for key in self.keys
						if self[ key ] != None ])
		
	def GetCols( self ):
		return dict([( key, self[ key ]) 
					for key in self.cols
						if self[ key ] != None ])

	def __call__( self, dict={}, **kw ):
		new = DbTableRow( self.tableName, self.GetKeys(), self.GetCols())
		new.__dict__[ "enums" ] = self.enums
		for key,val in dict.items() + kw.items():
			#print ("Updating new:", key, val)
			new.__setattr__( key, val )
		return new
	
	def __getattr__( self, name ):
		try:				return self.__dict__[ name ]
		except KeyError:	return self[ name ]

	def __setattr__( self, name, value ):
		if name not in self:
			raise KeyError

		if value == None:
			if name in self.keys:
				raise ValueError	# can't make keys null
			else:
				self[ name ] = None

		if name in self.enums.keys():
			# enumeration
			if value not in self.enums[ name ]:
				raise ValueError

		elif not issubclass( type( self[ name ]), type( value )):
			raise TypeError

		self[ name ] = value
		
	def AsSQLInsert( self, **kw ):
		return SQLInsert( self.tableName, self, **kw )
		
	def AsSQLTruncate( self ):
		return "TRUNCATE TABLE %s" % self.tableName

	def __str__( self ): return self.AsSQLInsert()




def SQLInsert( table, dict={}, **kw ):
	""" create insert table sql cmd from table name and keyword dict
	"""
	Dict = {}
	Dict.update( dict )
	Dict.update( kw )
	
	keys = []
	vals = []
	for key, val in Dict.items():
		if val == None or not str( val ):
			continue
		keys.append( "%s" % key )
		vals.append( '"%s"' % str( val ))

	return ( "insert into %s \n\t(" % table
		+ ", ".join( keys )
		+ ")\n\tVALUES ("
		+ ", ".join( vals )
		+ ")" )

def SQLUpdate( query ):
	DbExecute( query ).Commit()



if __name__ == "__main__":
	if 0:
		print (SQLInsert( "people", idPerson=5, name="George",sex="M", Birthplace="S. bend", idParents=0))
		
		
	

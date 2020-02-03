
import ConfigParser

# ------------------------------------------
# persistent settings file 

class SimpleSettings( ConfigParser.RawConfigParser ):
	
	""" maintain a pool of simple app settings in an INI file """

	INI_FILENAME = "c:/Documents and Settings/All Users/Application Data/%s.ini" 
	
	def __init__( self, appname, defaults={}):
		""" init parser and load default file """
	
		ConfigParser.RawConfigParser.__init__( self, defaults )
					
		self.appname = appname
		self.filename = self.INI_FILENAME % appname
#		print "Loading Settings from:", self.filename
		self.read( self.filename )
		self.SetSection( "Default" )
		
	def Merge( self, aDict ):
		""" override existing settings with entries from a dict """
		for key,value in aDict.items():
			self.Set( key, value )
			
	def Parse( self, arglist ):
		""" override existing settings with a=b forms in a list.
			return the list with those forms removed
			"""
		res = []
		for arg in arglist:
			if "=" in arg:
				key, value = arg.split("=",1)
				self.Set( key.strip(), value.strip())
			else:
				res.append( arg )
		return res

	def Save( self ):
#		print "Saving Settings to:", self.filename
		self.write( file( self.filename, "w" ))

	def SetSection( self, sect ):
		self.sect = sect
		if not self.has_section( sect ):
			self.add_section( sect )

	def getTuple( self, name, default=None ):
		value = self.Get( name, default=default )
		if value != default:
			return eval( value )
		else:
			return value

	def setTuple( self, name, value ):
		self.Set( name, value )

	def GetSize( self, default=None ):
		try:
			return self.getTuple( "Size", default )
		except ( ConfigParser.NoSectionError, ConfigParser.NoOptionError ):
			if default:
				return default
			else:
				raise

	def GetPos( self, default=None ):
		try:
			return self.getTuple( "Position", default )
		except ( ConfigParser.NoSectionError, ConfigParser.NoOptionError ):
			if default:
				return default
			else:
				raise

	def SetSize( self, value ):
		return self.setTuple( "Size", value )

	def SetPos( self, value ):
		return self.setTuple( "Position", value )

	def Get( self, name, default=None ):
		if self.has_option( self.sect, name ):
			return self.get( self.sect, name )
		else:
			return default
			
	def GetInt( self, name, default=None ):
		if self.has_option( self.sect, name ):
			return self.getint( self.sect, name )
		else:
			return default

	def GetBool( self, name, default=None ):
		if self.has_option( self.sect, name ):
			return self.getboolean( self.sect, name )
		else:
			return default

	def GetFloat( self, name, default=None ):
		if self.has_option( self.sect, name ):
			return self.getfloat( self.sect, name )
		else:
			return default

	def Set( self, name, value ):
		self.set( self.sect, name, str( value ))
		
	def SetInt( self, name, value ):
		self.Set( name, value )
		
	SetBool = SetFloat = SetInt
	



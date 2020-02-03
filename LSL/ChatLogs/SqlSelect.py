

class Select:
	def __init__( self, table="", columns="", where="", order="", group="" ):
		self.table = table
		self.columns = columns
		self.where = where
		self.order = order
		self.group = group

	def __str__( self ):
		return ("SELECT "
			+	self.GetColumns()
			+	self.GetTable()
			+	self.GetWhere()
			+	self.GetGroup()
			+	self.GetOrder())

	def GetColumns( self ):
		return self.columns

	def GetTable( self ):
		return " FROM " + self.table

	def GetWhere( self ):
		if self.where:
			return " WHERE " + self.where
		else:
			return ""

	def GetOrder( self ):
		if self.order:
			return " ORDER BY " + self.order
		else:
			return ""

	def GetGroup( self ):
		if self.group:
			return " GROUP BY " + self.group
		else:
			return ""

	def AddWhereClause( self, where ):
		if self.where:
			self.where += " AND " + where
		else:
			self.where = where


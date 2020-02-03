
from __future__ import nested_scopes

from string import *
import os

########################################
# extract useful bits from the environment

def getenv( name, default="" ):
	if os.environ.has_key( name ):
		return os.environ[ name ]
	else:
		return default

SCRIPT_NAME = getenv( 'SCRIPT_NAME', "/cgi.bin/issues.cgi/" )
REMOTE_ADDR =  getenv( 'REMOTE_ADDR' )
PATH_INFO = getenv( "PATH_INFO" )
HTTP_COOKIE = getenv( 'HTTP_COOKIE' )

########################################
# cookie support

class CookiesOut:
	def __init__( self ):
		self.Data = []

	def print_cookies( self ):
		for cookie in self.Data:
			print cookie

	def add_cookie( self, key, value, exp="", path="", domain="" ):
		cookie = "Set-Cookie: " + key + '=' + value
		if exp:
			cookie += '; expires=' + exp
		if path:
			cookie += '; path=' + path
		if domain:
			cookie += '; domain=' + domain

		self.Data.append( cookie )

cookiesOut = CookiesOut()

class CookiesIn:
	def __init__( self, http_cookies="" ):
		self.Data = {}
		if http_cookies:
			self.add_cookies( http_cookies )
	
	def add_cookie( self, name, value ):
		self.Data[ name ] = value

	def add_cookie2( self, nameValue ):
		( name, value ) = split( nameValue, "=" )
		self.add_cookie( name, value )
	
	def add_cookies( self, cookieList ):
		cookies = split( cookieList, ";" )
		for cookie in cookies:
			self.add_cookie2( cookie )

	def get_cookie( self, name ):
		return self.Data[ name ] # throws exception if no name

# cookiesIn = CookiesIn( HTTP_COOKIE )

########################################
# HTML generation helper library

def print_body( 
	text="#000000", 
	back="FFFFFF", 
	link="#0000EE", 
	VL="#551A8B", 
	AL="#FF0000" ):

	print '<BODY TEXT="' + text + \
		'" BGCOLOR="' + back + \
		'" LINK="' + link + \
		'" VLINK="' + VL + \
		'" ALINK="' + AL +'" >'

def print_boilerplate( head, title = "" ):
	print "Content-type: text/html"
	cookiesOut.print_cookies()
	print

	print "<HTML>"
	print "<HEAD>"
	if title:
		print "<TITLE>" + title + "</TITLE>"
	print head
	print "</HEAD>"

	print_body() #  back="#FFFFCC" )

	# <SCRIPT lang=JavaScript>
	# <!-- ... // -->
	# </SCRIPT>

def print_head( title = "", head="" ):
	print_boilerplate( head, title )

def print_trailer():
	print "</BODY>"
	print "</HTML>"

########################################
# create various HTML structures from Python objects

def quote( arg ):
	return '"' + replace( str( arg ), '"', '""' ) + '"'

def optArg( name, value ):
	if value:
		return ' ' + name + '="' + str( value ) + '"'
	else:
		return ''

def optArg0( name, value ):
	if value:
		return ' ' + name
	else:
		return ''

def select_list( name, 
		opts, 
		selected=None, 
		size=None, 
		multiple=0 ):

	res = ( '<SELECT NAME="' 
		+ name 
		+ '"'
		+ optArg( "SIZE", size )
		+ optArg0( "MULTIPLE", multiple )
		+ '>\r\n' )

	for opt in opts:
		if opt == selected:
			res = res + "<OPTION SELECTED>"
		else:
			res = res + "<OPTION>"
		res = res + opt + "\r\n"

	res = res + "</SELECT>\r\n"
	return res

def form_head( name="", action="", method="POST" ):

	if action == "":
		action = SCRIPT_NAME
	
	return (
		'<form'
		+ optArg( "name", name )
		+ optArg( "action", action )
		+ ' method=' + method 
		+ ' >')

def form_tail():
	return "</form>"

def as_form( form_body, name="", action="", method="POST" ):
	return (
		form_head( name=name, action=action, method=method )
		+ form_body
		+ form_tail())

def input_hidden( name, value ):
	return ( 
		'<input type=hidden name="' 
		+ str( name ) 
		+ '" value="' 
		+ str( value ) 
		+ '">' 
		)

def input_submit( name, value ):
	return ( 
		'<input type=submit name="' 
		+ str( name ) 
		+ '" value="' 
		+ str( value ) 
		+ '">' 
		)

def input_text( name, value="1", size=4 ):
	return (
		'<input type=text name="' 
		+ str( name ) 
		+ '" value="' 
		+ str( value ) 
		+ '" size=' 
		+ str( size ) 
		+ ">"
		)

def input_textarea( name, value, rows, cols ):
	if not value:
		value = "" # "None"
	return (
		'<textarea name='
		+ quote( name )
		+ ' rows=' 
		+ quote( rows ) 
		+ ' cols=' 
		+ quote( cols ) 
		+ " wrap=virtual>"
		+ value 
		+ "</textarea>"
		)

def input_checkbox( name, value=None ):
	return (
		'<input type=checkbox name=' 
		+ quote( name )
		+ optArg( "value", value )
		+ '>' 
		)

def input_radio( name, value=None ):
	return (
		'<input type=radio name=' 
		+ quote( name )
		+ optArg( "value", value )
		+ '>' 
		)

def input_button( value=None, onClick=None, name=None ):
        sub = '<input type=button'
	if name:
		sub += ' name="' + str( name ) + '"'
	if value:
		sub += ' value="' + str( value ) + '"'
	if onClick:
		sub += ' onClick="' + str( onClick ) + '"'
	sub += '>'

	return sub

# other way:
# <INPUT type=BUTTON value=label onClick="window.location='http://...'">
# "window.location=http://cascade-sys.com/cgi-bin/x10.cgi?"


def link_id( id ):
	id = str( id )
	return '<A HREF="' + SCRIPT_NAME + '?show=' + id + '">' + id + '</a>'

########################################
# we need to distinguish a title, heading or label that preceeds 
# the table and the column or row lables that lie within it...

def as_table_data( 
	datum,
	align		="",
	background	="",
	bgcolor		="",
	colspan		="",
	height		="",
	nowrap		="",
	rowspan		="",
	valign		="",
	width		="",
	bordercolor	="",
	bordercolorlight="",
	bordercolordark	="",
	abbr		="",
	axis		="",
	headers		="",
	scope		="" ):

	return ( "      <TD"
		+ optArg( "align", align )
		+ optArg( "background", background )
		+ optArg( "bgcolor", bgcolor )
		+ optArg( "colspan", colspan )
		+ optArg( "height", height )
		+ optArg( "nowrap", nowrap )
		+ optArg( "rowspan", rowspan )
		+ optArg( "valign", valign )
		+ optArg( "width", width )
		+ optArg( "bordercolor", bordercolor )
		+ optArg( "bordercolorlight", bordercolorlight )
		+ optArg( "bordercolordark", bordercolordark )
		+ optArg( "abbr", abbr )
		+ optArg( "axis", axis )
		+ optArg( "headers", headers )
		+ optArg( "scope", scope )
		+ ">" 
		+ str( datum ) 
		+ "</TD>\n" )

as_TD = as_table_data

def as_table_header( 
	datum,
	align		="",
	background	="",
	bgcolor		="",
	colspan		="",
	height		="",
	nowrap		="",
	rowspan		="",
	valign		="",
	width		="",
	bordercolor	="",
	bordercolorlight="",
	bordercolordark	="",
	abbr		="",
	axis		="",
	headers		="",
	scope		="" ):

	return ( "      <TH"
		+ optArg( "align", align )
		+ optArg( "background", background )
		+ optArg( "bgcolor", bgcolor )
		+ optArg( "colspan", colspan )
		+ optArg( "height", height )
		+ optArg( "nowrap", nowrap )
		+ optArg( "rowspan", rowspan )
		+ optArg( "valign", valign )
		+ optArg( "width", width )
		+ optArg( "bordercolor", bordercolor )
		+ optArg( "bordercolorlight", bordercolorlight )
		+ optArg( "bordercolordark", bordercolordark )
		+ optArg( "abbr", abbr )
		+ optArg( "axis", axis )
		+ optArg( "headers", headers )
		+ optArg( "scope", scope )
		+ ">" 
		+ str( datum ) 
		+ "</TH>\n" )

as_TH = as_table_header

def as_table_row( 
		data,
		align="",
		bgcolor="",
		valign="",
		background="",
		bordercolorlight="",
		bordercolordark="" ):

	return ( "  <TR"
		+ optArg( "align", align )
		+ optArg( "bgcolor", bgcolor )
		+ optArg( "valign", valign )
		+ optArg( "background", background )
		+ optArg( "bordercolorlight", bordercolorlight )
		+ optArg( "bordercolordark", bordercolordark )
		+ ">\n"
		+ data
		+ "  </TR>\n" )

as_TR = as_table_row

def as_table( list_of_rows, title = None, **dict ):

	table = HtmlTable( list_of_rows, **dict )
	table.width = "98%"
	table.rowattr[1].bgcolor = "#F0F0F0"
	table.rowattr[2].bgcolor = "#FFFFFF"

	caption = ""
	if title != None:
		caption += ( "<H3>" 
			+ title 
			+ " ( " + str( len( list_of_rows ) - 1 )
			+ " )</H3>\n" )
	return caption + str( table )

def as_table_old( 
	list_of_rows, 
	title = None, 
	rules="", 
	border="2", 
	frame="",
	align="",
	bgcolor="",
	cellpadding="",
	width="98%" ):

	table = ( "<TABLE "
		+ optArg( "rules", rules )
		+ optArg( "border", border )
		+ optArg( "frame", frame )
		+ optArg( "align", align )
		+ optArg( "bgcolor", bgcolor )
		+ optArg( "cellpadding", cellpadding )
		+ optArg( "width", width )
		+ " >\n" )

	if title != None:
		table += ( "<H3>" 
			+ title 
			+ " ( " + str( len( list_of_rows ) - 1 )
			+ " )</H3>\n" )

	colorA = "#F0F0F0"
	colorB = "#FFFFFF"
	alternating = colorA
	for row in list_of_rows:
		row_data = ""
		for col in row:
			row_data += as_table_data( col )
		table += as_table_row( row_data, bgcolor=alternating )

		if alternating == colorA:
			alternating = colorB
		else:
			alternating = colorA

	table += "</TABLE>\n"

	return table

def as_bold( text ):
	return "<B>" + text + "</B>"

def as_ital( text ):
	return "<I>" + text + "</I>"

def pick_col( array, col ):
	result = []
	for row in array:
		result.append( row[ col ])
	return result

def pr_field( name, value ):
	print "<b>", name, "</b>", value, "  ",

def pr_text( name, value ):
	print "<P><b>", name, "</b><br>"
	print value, "<br>"

def as_edit( name, value, width ):
	return input_text( name, value, width )

def pr_editf( name, value, width ):
	print "<b>", name, "</b>", input_text( name, value, width ), "  ",

def pr_textarea( name, value, rows, cols ):
	print "<P><b>", name, "</b><br>"
	print input_textarea( name, value, rows, cols )

def as_select( name, selected, opts ):
	if not selected in opts:	## may want to revisit this policy
		opts.append( selected )
	return	select_list( name, opts, selected )

def pr_select( name, selected, opts ):
	print "<b>", name, "</b>", as_select( name, selected, opts )


# other way: 
# <INPUT type=BUTTON value=label onClick="window.location='http://...'">



#########################################################################
# Improved Table class
#
# This allows the various components of an HTML table
# to be assembled and manipulated independently of the
# HTML representation.  Of particular convenience, it
# allows you to specify some column attributes on a 
# per-column basis, instead of having to specify it 
# individually for each cell.
#
# Tables consist of several independent components.
# These are done as separate classes so that the data
# all may be accessed as attributes of the main table object.
#
#	E.g.,  
#
#		tab = HtmlTable( "Caption" )
#		tab.colattr[ 3 ].span = 2
#		tab.colattr[ 2 ].align = "left"
#		tab.caption.align = "center"
#			
# Note: several of the objects define a __getitem__() method.  This
# allows things like "tab.colattr[ i ].span=2" to work.  Unfortunately,
# for...in iterators also evidently rely on __getitem__ to raise an
# exception when out of data, so iterating on these arrays result in
# infinite loops.  Thus we typically use 'for i in xrange(len(foo)):'
# instead.

####
# common subclass for all table attribute objects
#
# instance vars to these type objects must start with "_"
# else they'll appear in the HTML output.
#

class HtmlTableObject:

	def __init__( self, pre="", post=">", ignore=None, **dict ):
		self.__dict__ = dict
		self._pre = pre
		self._post= post
		if ignore:
			self._ignore = ignore
		else:	
			self._ignore = []

	def args( self ):
		args = ""
		for key in self.__dict__.keys():
			if key[0] != '_' and not key in self._ignore:
				val = self.__dict__[ key ]
				if val:
					args += optArg( key, val )
		return args

	def __repr__( self ):
		args = self.args()
		return self._pre + args + self._post

	def write( self, file ):
		file.write( str( self ))

# variation: if no args, resentation is ""

class HtmlOptTableObject( HtmlTableObject ):
	
	def __repr__( self ):
		args = self.args()
		if args:
			return self._pre + args + self._post
		else:
			return ""


####
# common subclass for arrays of table attributes
#
# If you specify too many or too few column attributes then
# it's up to the Viewer to decide how to handle.

class HtmlTableDynArray:

	def __init__( self, type = HtmlTableObject ):
		self.data = []
		self.element_type = type

	def grow( self, num ):
		for i in xrange( len( self ), num ):
			self.data.append( self.element_type())

	def __len__( self ):
		return len( self.data )

	# this lets the user assign to cols[i].colAttr
	
	def __getitem__( self, key ):	
		self.grow( key + 1 )
		return self.data[ key ]

	# it's usually a mistake to ask for these guys' rep

	def __repr__( self ):
		return "<<HtmlTableDynArray[" + str( len( self )) + "]>>"
		

####
# column attributes
#
#	align	= left | right | center
#	char	= alignment character, e.g., '.'
#	charoff	= dist to alignment char
#	span	= number of columns to include
#	valign	= top | middle | bottom | baseline
#	width	= pixes | percentage
#

class HtmlTableColAttributes( HtmlOptTableObject ):

	def __init__( self, **dict ):

		HtmlOptTableObject.__init__( self, pre = "    <COL", post = ">\n", **dict )

		# eventually this should be generalized to independently
		# track col attrs that appear in <colgroup> sections vs.
		# the ones that only appear within <th> and <td> sections.

# array of column attributes

class HtmlTableColAttrs( HtmlTableDynArray ):

	def __init__( self ):
		HtmlTableDynArray.__init__( self, HtmlTableColAttributes )

	def __repr__( self ):
		repr = ""
		for i in xrange( len( self )):
			repr += str( self.data[ i ])
		if repr:
			repr = "  <COLGROUP>\n" + repr
		return repr


####
# row attributes
#
#	align			= left | right | center
#	valign			= top | middle | bottom | baseline
#	bgcolor			= background color
#	background		= image URL
#	bordercolor		= center portion
#	bordercolorlight= light shade for 3d borders
#	bordercolordark	= dark shade for 3d borders
#

class HtmlTableRowAttributes( HtmlTableObject ):

	def __init__( self, **dict ):
		HtmlTableObject.__init__( self, pre = "  <TR", post = ">\n", **dict )


BlankHtmlTableRowAttributes = HtmlTableRowAttributes()

####
# a dynamic array of row attributes

class HtmlTableRowAttrs( HtmlTableDynArray ):

	def __init__( self ):
		HtmlTableDynArray.__init__( self, HtmlTableRowAttributes )

# if you specify too many row attributes, the extra ones are ignored.
#
# if you specify too few, they're treated as follows 
# (where NRA = number of row attributes):
#
#	if NRA <= 0 then nothing happens
#
#	if self.headrows > 0 AND self.headrows > NRA then
#
#		attributes are applied to header rows until they run out
#		and no other actions take place.
#
#	if self.headrows < NRA then
#
#		the first N row attributes map 1:1 to the header rows.
#
#		the remaining attributes are applied to to the regular data rows
#
#		if there are fewer attributes remaining than there are regular rows
#		then the row attributes in xrange( self.headrows, NRA ) repeat
#		mod however many there are.
#
#		if there are too many, the extra ones are ignored.
#
# The intent of all this is to allow you to precisely control the header
# rows and then specify a repeating pattern for the rest of the table.
# E.g., suppose you have 1 headerrow and then you want to alternate
# background colors of the actual data rows (without affecting the header):
#
#	table.rowattr[1].bgcolor = color1
#	table.rowattr[2].bgcolor = color2
#
#	Note that rowattr[0] is NOT defined and thus gets browser defaults.
#	The first data row gets color1, the second color2, and they continue
#	alternating like that.
# 
# This logic lives in the table class itself, not the row attr array.
##

####
# cell attributes
#
#	cell attributes are only used to OVERRIDE row and col attributes.
#	E.g., to highlight cells or to specify column or row spanning.
#
#	cells are indexed by zero-origin, (col,row) tuples.
#
#	caller has to know if it's being used as a TD or TH field
		
class HtmlTableCellAttributes( HtmlTableObject ):

	def __init__( self, **dict ):
		HtmlTableObject.__init__( self, **dict )

	def as_data( self, data ):
		self._pre = "      <TD"
		self._post = ">"
		return str( self ) + str( data ) + "</TD>\n"

	def as_head( self, data ):
		self._pre = "      <TH"
		self._post = ">"
		return str( self ) + str( data ) + "</TH>\n"

BlankTableCellAttributes = HtmlTableCellAttributes()
		
####
# dynamic array of cell attributes
#
# Note the indicies are (col,row) pairs
#
# this allows you to override the TD/TH attributes on a per-cell
# exception basis.

class HtmlTableCellAttrs:		##( HtmlTableDynArray ):

	def __init__( self, **dict ):
		self.data = dict

	def __len__( self ):
		return len( self.data )

	def __getitem__( self, index ):
		try:
			return self.data[ index ]
		except:
			self.data[ index ] = HtmlTableCellAttributes()
			return self.data[ index ]

	def select_obj( self, col, row ):
		index = (col,row)
		if index in self.data.keys():
			return self.data[ index ]
		else:
			return BlankTableCellAttributes

	def as_data( self, col, row, data ):
		return self.select_obj( col, row ).as_data( data )
		
	def as_head( self, col, row, data ):
		return self.select_obj( col, row ).as_head( data )
		

####
# manipulate the caption
#
#	caption		= caption to appear at top of table
#	summary		= longer text for brail, etc.
#	align		= top | bottom | left | right | center
#	valign		= top | bottom
#

class HtmlTableCaption( HtmlOptTableObject ):

	def __init__( self, caption, **dict ):
		HtmlOptTableObject.__init__( self, **dict )
		self._caption = caption

	def __repr__( self ):

		args = self.args()
		if args or self._caption:
			return ("  <CAPTION"
					+ args 
					+ ">"
					+ self._caption
					+ "</CAPTION>\n"
					)
		else:
			return ""

####
# a dynamic array of rows
#
# each row is an array of columns
#
# generally, the number of columns should be the same for all rows.
# The exception is where rows or columns are being spanned.
#

class HtmlTableRows:					# ( HtmlTableObject ):

	def __init__( self, rows = None ):
		if rows:
			self.rows = rows
		else: 
			self.rows = []

	def __len__( self ):
		return len( self.rows )

	def grow( self, length ):
		for i in xrange( len( self ), length ):
			self.rows.append([])
	
	def __getitem__( self, index ):
		self.grow( index + 1 )
		return self.rows[ index ]

	def addRow( self, row ):
		self.rows.append( row )

	def addRows( self, rows ):
		self.rows += rows

####
# the table object itself pulls it all together...
#
#	rows			= initial number of rows
#	caption			= caption text
#	rules			= none | groups | rows | cols | all
#	hspace			= pixes left and right of an aligned table
#	height			= overall height, pixels or %window height
#	border			= border width  ( 2 )
#	frame			= void | above | below | hsides 
#							| lhs | rhs | vsides | box | border
#	align			= left | right | center
#	bgcolor			= #rrggbb or color name
#	cellpadding		= pixels within the cell
#	cellspacing		= pixels between cells  ( 2 )
#	vspace			= vertical space
#	background		= image URL
#	bordercolor		= center portion
#	bordercolorlight= light shade for 3d borders
#	bordercolordark	= dark shade for 3d borders
#	headrows		= number of header rows (<TH> instead of <TD>)
#	headcols		= number of header columns
#	width			= width of table ("98%" ):
#

class HtmlTable( HtmlTableObject ):
	def __init__( self, 
		rows		= None, 
		caption		= "", 
		headrows	= 0, 
		headcols	= 0, 
		**dict ):

		HtmlTableObject.__init__(
			self,
			pre = "<TABLE",
			post = ">\n",
			ignore = [ 
					"rows", 
					"caption", 
					"headrows", 
					"headcols", 
					"colattr", 
					"rowattr", 
					"cellattr" ],
						**dict )

		# Other HtmlTable instance vars

		self.rows	= HtmlTableRows( rows )
		self.caption	= HtmlTableCaption( caption )
		self.headrows	= headrows
		self.headcols	= headcols

		self.colattr	= HtmlTableColAttrs()
		self.rowattr	= HtmlTableRowAttrs()
		self.cellattr	= HtmlTableCellAttrs()


	def headAsString( self ):

		return (
			str( HtmlTableObject.__repr__( self )) 
			+ str( self.caption ) 
			+ str( self.colattr )
			)

	def tailAsString( self ):
		return "</TABLE>\n"

	# interpret row attribute distribution

	def headrow_attr( self, index ):
		if index >= len( self.rowattr ):
			return BlankHtmlTableRowAttributes
		else:
			return self.rowattr[ index ]

	def bodyrow_attr( self, index ):
		n = len( self.rowattr ) - self.headrows
		 
		if n <= 0:
			return BlankHtmlTableRowAttributes
		else:
			m = ( index - self.headrows ) % n
			return self.rowattr[ m + self.headrows ]

	def as_headrow( self, index, data ):
		return str( self.headrow_attr( index )) + data + "\n  </TR>\n"

	def as_bodyrow( self, index, data ):
		return str( self.bodyrow_attr( index )) + data + "\n  </TR>\n"

	def bodyAsString( self ):
		table = ""
#		for row in self.rows:	# this doesn't work

		for r in xrange( self.headrows ):
			row = self.rows[ r ]
			row_data = ""
			for c in xrange( len( row )):
				col = row[ c ]
 				row_data += self.cellattr.as_head( c, r, col )
			table += self.as_headrow( r, row_data )

		for r in xrange( self.headrows, len( self.rows )):
			row = self.rows[ r ]
			row_data = ""
			for c in xrange( self.headcols ):
				col = row[ c ]
 				row_data += self.cellattr.as_head( c, r, col )
			for c in xrange( self.headcols, len( row )):
				col = row[ c ]
 				row_data += self.cellattr.as_data( c, r, col )
			table += self.as_bodyrow( r, row_data )
		return table

	def __repr__( self ):
		return (  self.headAsString()
				+ self.bodyAsString()
				+ self.tailAsString()
				)

	def addRow( self, row ):
		self.rows.addRow( row )

	def addRows( self, rows ):
		self.rows.addRows( rows )

####################################################
# unit test code

def testTable():
	t = HtmlTable( caption="Caption booble" )
	t.caption.align = "center"
	t.width = "60%"
	t.addRows( 
		[[ 'aa', 'ab', 'ac', 'ad' ], 
		[ 'ba', 'bb', 'bc', 'bd' ], 
		[ 'ca', 'cb', 'cc', 'cd' ], 
		[ 'da', 'db', 'dc', 'dd' ]])
	t.colattr[ 0 ].align="center"
	t.colattr[ 1 ].align="left"
	t.cellattr[ 1,1 ].colspan =6
	t.headrows = 1
	t.headcols = 1
	t.rowattr[1].bgcolor = "#00FF00"
	t.rowattr[2].bgcolor = "#FF00FF"
	print t

	## TODO: colattr needs to go to colgroup, which only IE implements
	## replace it with a colattr that works like rowattr

if __name__ == "__main__":
	testTable()

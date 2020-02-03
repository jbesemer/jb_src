string	VERSION = "1.4d";

integer	TRACE = 0;

// give notecard [ TBD ]

string	CONFIG_SEP = "=";        // separator between name and value in config files

float	DWELL_THRESHOLD = 2.0;

integer	PICTURE_CHAN = 77;
integer	DIALOG_CHAN;			// set to rand number at init time

string	QueryNotecardName = "Configuration";
integer	QueryIndex;
key		QueryId;

vector 	WhiteColor      = <1,1,1>;
vector 	BlackColor      = <0,0,0>;
vector 	RedColor        = <1,0,0>;
vector	YellowColor     = <1,1,0>;
vector	GreenColor      = <0,1,0>;

vector	LockedColor     = <0,1,0>;
vector	UnlockedColor   = <1,0,0>;
float	LockedAlpha     = 0.1;
float	UnlockedAlpha   = 0.3;

string CMD_SHOW_DEFAULT = "Show Default";
string CMD_SET_DEFAULT  = "Set Default";
string CMD_NEXT         = "Show Next";
string CMD_PREV         = "Show Prev";
string CMD_SHOW_TRACE   = "Show Trace";
string CMD_HIDE_TRACE   = "Hide Trace";
string CMD_START_CYCLE  = "Start Cycle";
string CMD_STOP_CYCLE   = "Stop Cycle";
string CMD_LOCK         = "Lock";
string CMD_UNLOCK       = "Unlock";

list BUTTONS = [
	CMD_SET_DEFAULT,
	CMD_SHOW_DEFAULT,
	CMD_NEXT,
	CMD_PREV,
	//    CMD_SHOW_TRACE,
	//    CMD_HIDE_TRACE,
	//    CMD_LOCK, 		// LOCK or UNLOCK added dynamically
	//    CMD_UNLOCK,
	CMD_START_CYCLE,
	CMD_STOP_CYCLE ];

list OriginalNames	= [];	// texture name (original case)
list Names			= [];	// texture name (all upper case, for mapping config names ignoring case)
list Ratios			= [];	// texture aspect ratio
list FullBrights	= [];	// texture fullbright setting

integer	NAME_COUNT;     // number of textures

integer	ALL_FULLBRIGHT = 0;
integer	NO_FULLBRIGHT = 0;

integer	Index;
string	current_name;
string	default_name;
float	current_ratio;
vector	current_size;

// Text Output ///////////////////////////////////////////////////////

vector	TEXT_COLOR = WhiteColor;
float	TEXT_ALPHA = 1.0;

Say( string msg )
{
	llOwnerSay( msg );
}

Trace( string msg )
{
	if( TRACE )
		Say( msg );
}

SetText( string message, vector color )
{
	llSetText( message, color, TEXT_ALPHA );
}

// Configuration File Processing /////////////////////////////////////

integer	SIDE_FRONT = 2;     // cube's +x
integer	SIDE_BACK = 4;      // cube's -x
float	ALPHA_OPAQUE = 1.0;
float	ALPHA_TRANS = 0.0;

string	SIDE_TEXTURE	= TEXTURE_BLANK;        // this isn't working for TRANSPARENT
string	BACK_TEXTURE	= TEXTURE_BLANK;        // this isn't working for TRANSPARENT
string	FRONT_TEXTURE	= TEXTURE_PLYWOOD;
vector	SIDE_COLOR		= BlackColor;
vector	BACK_COLOR		= BlackColor;
vector	FRONT_COLOR		= WhiteColor;
float	SIDE_ALPHA		= ALPHA_OPAQUE;
float	BACK_ALPHA		= ALPHA_OPAQUE;
float	FRONT_ALPHA		= ALPHA_OPAQUE;

OneTimeInitialization()
{
	current_size = llGetScale();
	DIALOG_CHAN = (integer)(llFrand(-1000000000.0) - 1000000000.0);
	Trace( "Dialog Chan: " + (string)DIALOG_CHAN );

	llSitTarget(<0, 0, 0.1>, ZERO_ROTATION); // needed for llAvatarOnSitTarget to work
	llSetTouchText( "Next Image" );
	llSetSitText( "NO Sit" );	// llSetSitText( "Get Note" );

	llSetPrimitiveParams([
		PRIM_COLOR, ALL_SIDES, SIDE_COLOR, SIDE_ALPHA,
		PRIM_TEXTURE, ALL_SIDES, SIDE_TEXTURE, <1,1,0>, <0,0,0>, 0.0]);

	llSetPrimitiveParams([
		PRIM_COLOR, SIDE_BACK, BACK_COLOR, BACK_ALPHA,
		PRIM_COLOR, SIDE_FRONT, FRONT_COLOR, FRONT_ALPHA,
		PRIM_TEXTURE, SIDE_BACK, BACK_TEXTURE, <1,1,0>, <0,0,0>, 0.0,
		PRIM_TEXTURE, SIDE_FRONT, FRONT_TEXTURE, <1,1,0>, <0,0,0>, 0.0]);

	pick_texture_by_name( default_name );
}

LoadImageNames()
{
	integer i;
	string s = "not null";

	Names = [];
	Ratios = [];
	FullBrights = [];

	// fetch inventory names

	for( i=0; s != ""; i++ ){
		s = llGetInventoryName( INVENTORY_TEXTURE, i );
		if( s != "" ){
			Trace( s );
			OriginalNames += [ s ];
			if( i == 0 )
				default_name = s;	// first name is default (unless overriden in config)
			s = llToUpper( s );
			Names += [ s ];
			Ratios += [ 1.0 ];		// default 1:1 A.R. (and ensures Names and Ratios are same len)
			FullBrights += [ 0 ];
		}
	}

	NAME_COUNT = llGetListLength( Names );
}

StoreImageParams( list params )
{
	string name = llList2String( params, 0 );
	integer K = llListFindList( Names, [ llToUpper( name )]);

	if( K < 0 ){
		Say( "Config names image not in inventory: " + name );
		return;
	}

	integer N = llGetListLength( params );

	if( N >= 2 && llToUpper( llList2String( params, -1 )) == "FULLBRIGHT" ){
		FullBrights = llListReplaceList( FullBrights, [ 1 ], K, K );
		Trace( "Fullbright: " + name );
		N--;
	}

	if( N >= 3 ){
		float R = llList2Float( params, 1 ) / llList2Float( params, 2 );
		Ratios = llListReplaceList( Ratios, [ R ], K, K );
		Trace( "AR: " + name + " = " + (string)R );
	}
}

list TextureMap = [
	"BLANK",		TEXTURE_BLANK,
	"DEFAULT",		TEXTURE_DEFAULT,
	"PLYWOOD",		TEXTURE_PLYWOOD,
	"TRANSPARENT",	TEXTURE_TRANSPARENT,
	"MEDIA",		TEXTURE_MEDIA ];

string MapTexture( string name )
{
	integer K = llListFindList( TextureMap, [ llToUpper( name )]);
	if( K >= 0 ){
		string new_name = llList2String( TextureMap, K + 1 );
		Trace( name + ": " + new_name );
		return new_name;
	} else
	return name;
}

list ColorMap = [
	"BLACK",    <0,0,0>,
	"WHITE",    <1,1,1>,
	"RED",      <1,0,0>,
	"GREEN",    <0,1,0>,
	"BLUE",     <0,0,1>,
	"YELLOW",   <1,1,0>
		];

vector MapColor( string value )
{
	integer K = llListFindList( ColorMap, [ llToUpper( value )]);
	if( K >= 0 )
		return llList2Vector( ColorMap, K + 1 );
	else
		return (vector)value;
}

string StripComments( string data )
{
	integer pos = llSubStringIndex( data, "#" );

	if( pos >= 0 )
		data = llDeleteSubString( data, pos, -1 );

	return llStringTrim( data, STRING_TRIM );
}

ProcessConfigLine( string Data )
{
	// strip comments, leading and trailing whitespace, and ignore blank lines
	string data = StripComments( Data );
	if( data == "" )
		return;

	if( llSubStringIndex( data, CONFIG_SEP ) >= 0 ){        // "Name=Value" parameters

		list tmp = llParseString2List( data, [CONFIG_SEP], []);
		string settingNoUp = llStringTrim( llList2String( tmp, 0 ), STRING_TRIM );
		string setting = llToUpper( settingNoUp );
		string value = llList2String( tmp, 1 );

		Trace( setting + " -> " + value );

		if( "TRACE" == setting )
			TRACE = (integer)value;

		else if( "CHAN" == setting )
			PICTURE_CHAN = (integer)value;

		else if( "DEFAULT" == setting )
			default_name = settingNoUp;

		else if( "DWELL" == setting )
			DWELL_THRESHOLD = (float)value;

		else if( "CYCLE_TIME" == setting )
			CYCLE_TIME = (float)value;

		else if( "BACK_TEXTURE" == setting )
			BACK_TEXTURE = MapTexture( value );

		else if( "SIDE_TEXTURE" == setting )
			SIDE_TEXTURE = MapTexture( value );

		else if( "BACK_COLOR" == setting )
			BACK_COLOR = MapColor( value );

		else if( "SIDE_COLOR" == setting )
			SIDE_COLOR = MapColor( value );

		else if( "BACK_ALPHA" == setting )
			BACK_ALPHA = (float)value;

		else if( "SIDE_ALPHA" == setting )
			SIDE_ALPHA = (float)value;

		else if( "FRONT_ALPHA" == setting )
			FRONT_ALPHA = (float)value;

		else if( "TEXT_COLOR" == setting )
			TEXT_COLOR = MapColor( value );

		else if( "TEXT_ALPHA" == setting )
			TEXT_ALPHA = (float)value;

		else if( "ALL_FULLBRIGHT" == setting )
			ALL_FULLBRIGHT = (integer)value;

		else if( "NO_FULLBRIGHT" == setting )
			NO_FULLBRIGHT = (integer)value;

		else if( "BOTH_SIDES" == setting )
			BOTH_SIDES = (integer)value;

		else
			Say( "Config: Ignoring: " + Data );

	} else {
		StoreImageParams( llCSV2List( data ));
	}
}

// Changing Current Image /////////////////////////////////////////////

set_fullbright( integer index )
{
	integer fullbright;
	
	if( NO_FULLBRIGHT )
		fullbright = 0;
	else if( ALL_FULLBRIGHT )
		fullbright = 1;
	else
		fullbright = llList2Integer( FullBrights, index );

	Trace( "Fullbright: " + (string)fullbright );
	llSetPrimitiveParams([ PRIM_FULLBRIGHT, SIDE_FRONT, fullbright ]);
}

pick_texture_by_name( string name )
{
	pick_texture_by_index( llListFindList( Names, [ llToUpper( name )]));
}

integer BOTH_SIDES = 0;

pick_texture_by_index( integer index )
{
//	string name = llList2String( Names, index );
	current_name = llList2String( OriginalNames, index );
	
	llSetTexture( current_name, SIDE_FRONT );
	ResetAspectRatio( llList2Float( Ratios, index ));
	
	if( BOTH_SIDES )
		llSetTexture( current_name, SIDE_BACK );

	set_fullbright( index );
	
	llSetObjectDesc( current_name );
	llSetText( current_name, TEXT_COLOR, TEXT_ALPHA );
	
	Trace( "Picking " + current_name + " " + (string)current_ratio );
}

pick_next_texture()
{
	Index = ( Index + 1 ) % NAME_COUNT;
	pick_texture_by_index( Index );
}

pick_prev_texture()
{
	Index = ( Index + NAME_COUNT - 1 ) % NAME_COUNT;
	pick_texture_by_index( Index );
}

pick_default_texture()
{
	Trace( "Show default" );
	pick_texture_by_name( default_name );
}

MakeCurrentTextureDefault()
{
	Trace( "Set default" );
	default_name = current_name;
}

ChangeSize( vector new_size )
{
	vector size = llGetScale();

	if( llVecDist( size, new_size ) > 0.01	// ignore tiny changes
		&&  llVecMag( new_size ) > 0.1 )		// reject tiny sizes
		{
			llSetScale( new_size );
		}
}

ResetAspectRatio( float ratio )	// area-preserving, if possible
{
	// x dimension is thickness
	// y dim is horizontal extent
	// z is vertical

	current_ratio = ratio;
	vector size = llGetScale();
	float area = size.y * size.z ;
	Trace( "Area: " + (string)area );

	vector new_size;
	new_size.x = size.x;
	new_size.y = llSqrt( area * ratio );
	new_size.z = area / new_size.y;

	if( new_size.y > 10.0 ){
		float E = ( new_size.y - 10.0 ) / 10.0;
		new_size.y = 10.0;
		new_size.z = E * new_size.z;
	}

	if( new_size.z > 10.0 ){
		float E = ( new_size.z - 10.0 ) / 10.0;
		new_size.z = 10.0;
		new_size.y = E * new_size.y;
	}

	ChangeSize( new_size );
	Trace( "Size: " + (string)size + " -> " + (string)new_size );
}

// Automatically Cycle Thru Images //////////////////////////////////////

float CYCLE_TIME = 5.0;
integer CyclingImages = 0;

start_cycle(){
	CyclingImages = 1;
	llSetTimerEvent( CYCLE_TIME );
	Say( "Starting auto-cycle, every " + (string)CYCLE_TIME + " sec." );
}

stop_cycle(){
	CyclingImages = 0;
	llSetTimerEvent( 0 );
	Say( "Stopping auto-cycle" );
}

// Locking and Unlocking Controls ////////////////////////////////////////

integer Locked = 0;

lock(){
	// SetText( "[locked]", LockedColor );
	Trace( "Locked" );
	Locked = 1;
}

unlock(){
	// SetText( "[UNlocked]", UnlockedColor );
	Trace( "Unlocked" );
	Locked = 0;
}

// Show Dialog and Dispense Notecard ////////////////////////////////////

float	touch_start_time;
integer DialogLaunched;

show_dialog( key id ){
	string LockStatus;
	if( Locked )
		LockStatus = "[Locked]";
	else
		LockStatus = "[Unlocked]";
	
	string message
		= llGetScriptName() + " Version " + VERSION + " " + LockStatus + "\n"
		+ "Image: " + current_name + ", " + current_size.y + " x " + current_size.z + "\n"
		+ "Choose action:"
		;

	list Buttons = BUTTONS;
	if( Locked )
		BUTTONS += [ CMD_UNLOCK ];
	else
		BUTTONS += [ CMD_LOCK ];

	llDialog( id, message, BUTTONS, DIALOG_CHAN );
}

DispenseNotecard( key avatar )
{
	if( avatar != NULL_KEY ){
		llUnSit( avatar );
	}
}

// Process Dialog or PICTURE_CHAN messages ///////////////////////////////////////

ProcessMessage( string message )
{
	if( message == CMD_SHOW_DEFAULT ){
		pick_default_texture();

	} else if( message == CMD_NEXT ){
		pick_next_texture();

	} else if( message == CMD_PREV ){
		pick_prev_texture();

	} else if( message == CMD_SET_DEFAULT ){
		MakeCurrentTextureDefault();

	} else if( message == CMD_LOCK ){
		lock();

	} else if( message == CMD_UNLOCK ){
		unlock();

	} else if( message == CMD_START_CYCLE ){
		start_cycle();

	} else if( message == CMD_STOP_CYCLE ){
		stop_cycle();

	}
}

// default/startup state //////////////////////////////////////////

default
{
	state_entry(){
		Say( llGetScriptName() + " Version " + VERSION + " initializing..." );

		Trace( "Read Inventory" );
		SetText( "Loading Image Names", YellowColor );
		LoadImageNames();

		Trace( "Read Config" );
		SetText( "Processing Config", YellowColor );
		QueryIndex = 0;
		QueryId = llGetNotecardLine( QueryNotecardName, QueryIndex );
	}

	state_exit()
	{
		unlock();
		OneTimeInitialization();
	}

	dataserver( key queryId, string data ){
		if( queryId != QueryId )
			return;

		if( data == EOF )
			state Running;

		ProcessConfigLine( data );

		// fetch next config file line

		QueryId = llGetNotecardLine( QueryNotecardName, ++QueryIndex );
	}

	changed( integer change ){
		if( change & ( CHANGED_INVENTORY | CHANGED_SCALE ))
			llResetScript();
	}

	on_rez( integer param ){
		llResetScript();
	}
}

// Running state /////////////////////////////////////////////////////////////


state Running
{
	state_entry(){
		Trace( "Running..." );
		SetText( "Running", GreenColor );
		
		DialogLaunched = 0;
		
		llListen( PICTURE_CHAN, "", NULL_KEY, "" );
		llListen( DIALOG_CHAN, "", NULL_KEY, "" );
	}
	
	state_exit(){
		llSetTimerEvent( 0 );
	}

	touch_start( integer total_number ){
		if( !Locked || llDetectedKey( 0 ) == llGetOwner()){
			DialogLaunched = 0;
			touch_start_time = llGetTimeOfDay();
		}
	}

	touch( integer number ){
		if( !Locked || llDetectedKey( 0 ) == llGetOwner()){
			float dwell_time = llGetTimeOfDay() - touch_start_time;

			if( !DialogLaunched && dwell_time >= DWELL_THRESHOLD ){
				DialogLaunched = 1;
				show_dialog( llDetectedKey( 0 ));
			}
		}
	}

	touch_end(integer total_number){
		if( !Locked || llDetectedKey( 0 ) == llGetOwner()){
			if( !DialogLaunched )
				pick_next_texture();
			DialogLaunched = 0;
		}
	}

	listen( integer channel, string name, key id, string message ){
		ProcessMessage( message );
		if( channel == DIALOG_CHAN )
			show_dialog();
	}

	timer(){
		if( CyclingImages )
			pick_next_texture();
		else
			llSetTimerEvent( 0 );
	}

	changed( integer change ){
		if( change & CHANGED_INVENTORY )
			llResetScript();

		if( change & CHANGED_SCALE )
			ResetAspectRatio( current_ratio );

		if( change & CHANGED_LINK )
			DispenseNotecard( llAvatarOnSitTarget());
	}

	on_rez( integer param ){
		llResetScript();
	}
}

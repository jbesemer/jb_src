string VERSION = "1.4c";

integer TRACE = 0;

// float text invisible
// hover mouse to see name of art
// give notecard


vector  WhiteColor      = <1,1,1>;
vector  BlackColor      = <0,0,0>;
vector  RedColor        = <1,0,0>;
vector  YellowColor     = <1,1,0>;
vector  GreenColor      = <0,1,0>;

float   TEXT_ALPHA       = 1.0;

vector  LockedColor     = <0,1,0>;
vector  UnlockedColor   = <1,0,0>;
float   LockedAlpha     = 0.1;
float   UnlockedAlpha   = 0.3;

string	CONFIG_SEP = "=";        // separator between name and value in config files

float	DWELL_THRESHOLD   = 2.0;

integer PICTURE_CHAN    = 77;
integer DIALOG_CHAN     = -234234;  // TODO: make rand number, timeout

string  QueryNotecardName = "Configuration";
integer QueryIndex;
key     QueryId;

string CMD_SHOW_DEFAULT = "Show Default";
string CMD_SET_DEFAULT  = "Set Default";
string CMD_LOCK         = "Lock";
string CMD_UNLOCK       = "Unlock";
string CMD_NEXT         = "Show Next";
string CMD_SHOW_TRACE   = "Show Trace";
string CMD_HIDE_TRACE   = "Hide Trace";
string CMD_START_CYCLE  = "Start Cycle";
string CMD_STOP_CYCLE   = "Stop Cycle";

list BUTTONS = [ 
    CMD_SET_DEFAULT, 
    CMD_SHOW_DEFAULT, 
    CMD_NEXT, 
    CMD_SHOW_TRACE, 
    CMD_HIDE_TRACE, 
    CMD_LOCK, 
    CMD_UNLOCK,
    CMD_START_CYCLE,
    CMD_STOP_CYCLE ];

list Names = [];        // texture name
list Ratios = [];       // texture aspect ratio
list FullBrights = [];  // texture fullbright setting

integer	NAME_COUNT;     // number of textures

integer	ALL_FULLBRIGHT = 0;
integer	NO_FULLBRIGHT = 0;

integer	Index;
string	current_name;
string	default_name;
float	current_ratio;
vector	current_size;

float	start_time;

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

string StripComments( string data ){
    integer pos = llSubStringIndex( data, "#" );

    if( pos >= 0 )
        data = llDeleteSubString( data, pos, -1 );

    return llStringTrim( data, STRING_TRIM );
}

set_texture( string name )
{
    current_name = name;
    llSetTexture( name, SIDE_FRONT );
    // llSetTexture( current_name, SIDE_BACK );
}

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

pick_texture_name( string name )
{    
    pick_texture( llListFindList( Names, [ name ]));
}

pick_texture( integer index )
{
    set_texture( llList2String( Names, index ));
    set_fullbright( index );
    ResetAspectRatio( llList2Float( Ratios, index ));
    Trace( "Picking " + current_name + " " + (string)current_ratio );
}

pick_next_texture()
{
    Index = ( Index + 1 ) % NAME_COUNT;
    pick_texture( Index );
}

pick_default_texture()
{
    Trace( "Show default" );
    pick_texture_name( default_name );
}

MakeCurrentTextureDefault()
{
    Trace( "Set default" );
    default_name = current_name;
}

SetSize( vector new_size )
{
    vector size = llGetScale();
    
    if( llVecDist( size, new_size ) < 0.1
    ||  llVecMag( new_size ) < 0.1 )
        return;
        
    llSetScale( new_size );
}

ResetAspectRatio( float ratio )
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
     
    SetSize( new_size );
    Trace( "Size: " + (string)size + " -> " + (string)new_size );
}

StoreImageParams( string name, list params )
{
    integer K = llListFindList( Names, [ name ]);
    
    if( K < 0 ){
        Say( "Config names image not in inventory: " + name );
        return;
    }
        
    integer N = llGetListLength( params );
    
    if( N >= 1 && llToUpper( llList2String( params, -1 )) == "FULLBRIGHT" ){
        FullBrights = llListReplaceList( FullBrights, [ 1 ], K, K );
        Trace( "Fullbright: " + name );
        N--;        
    }
    
    if( N >= 2 ){
        float R = llList2Float( params, 0 ) / llList2Float( params, 1 );
        Ratios = llListReplaceList( Ratios, [ R ], K, K );
        Trace( "AR: " + name + " = " + (string)R );
    }
}

list TextureMap = [
    "BLANK", TEXTURE_BLANK,
    "DEFAULT", TEXTURE_DEFAULT,
    "PLYWOOD", TEXTURE_PLYWOOD,
    "TRANSPARENT", TEXTURE_TRANSPARENT,
    "MEDIA", TEXTURE_MEDIA ];
    
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

integer SIDE_FRONT = 2;     // cube's +x
integer SIDE_BACK = 4;      // cube's -x
float ALPHA_OPAQUE = 1.0;
float ALPHA_TRANS = 0.0;

string SIDE_TEXTURE = TEXTURE_BLANK;        // this isn't working for TRANSPARENT
string BACK_TEXTURE = TEXTURE_BLANK;        // this isn't working for TRANSPARENT
string FRONT_TEXTURE = TEXTURE_PLYWOOD;
vector SIDE_COLOR = BlackColor;
vector BACK_COLOR = BlackColor;
vector FRONT_COLOR = WhiteColor;
float SIDE_ALPHA = ALPHA_OPAQUE;
float BACK_ALPHA = ALPHA_OPAQUE;
float FRONT_ALPHA = ALPHA_OPAQUE;

InitSidesAndBack()
{
    llSetPrimitiveParams([
        PRIM_COLOR, ALL_SIDES, SIDE_COLOR, SIDE_ALPHA,
        PRIM_TEXTURE, ALL_SIDES, SIDE_TEXTURE, <1,1,0>, <0,0,0>, 0.0]);
    llSetPrimitiveParams([
        PRIM_COLOR, SIDE_BACK, BACK_COLOR, BACK_ALPHA,
        PRIM_COLOR, SIDE_FRONT, FRONT_COLOR, FRONT_ALPHA,
        PRIM_TEXTURE, SIDE_BACK, BACK_TEXTURE, <1,1,0>, <0,0,0>, 0.0,
        PRIM_TEXTURE, SIDE_FRONT, FRONT_TEXTURE, <1,1,0>, <0,0,0>, 0.0]);
}

float CYCLE_TIME = 5.0;
integer CycleMode = 0;

start_cycle(){
    CycleMode = 1;
    llSetTimerEvent( CYCLE_TIME );
    Say( "Starting auto-cycle" );
}

stop_cycle(){
    CycleMode = 0;
    llSetTimerEvent( 0 );
    Say( "Stopping auto-cycle" );
}

integer Locked = 0;

lock(){
    llSetText( "[locked]", LockedColor, LockedAlpha );
    Trace( "Locked" );
    Locked = 1;
}

unlock(){
    llSetText( "[UNlocked]", UnlockedColor, UnlockedAlpha );
    Trace( "Unlocked" );
    Locked = 0;
}

show_dialog( key id ){    
    llDialog( id, "Choose action", BUTTONS, DIALOG_CHAN );
}

integer DialogLaunched;

// default/startup state //////////////////////////////////////////

default
{
    state_entry(){
        Say( llGetScriptName() + " Version " + VERSION + " initializing..." );
        current_size = llGetScale();
        
        integer i;
        string s = "not null";
        
        // fetch inventory names
        
        for( i=0; s != ""; i++ ){
            s = llGetInventoryName( INVENTORY_TEXTURE, i );
            if( s != "" ){
                if( i == 0 )
                    default_name = s;
                Names += [ s ];
                Ratios += [ 1.0 ];        // default 1:1 A.R. (and ensures Names and Ratios are same len)
                FullBrights += [ 0 ];
                Trace( s );
            }
        }
        
        NAME_COUNT = llGetListLength( Names ); 
        
        // read config file
        
        Trace( "ReadConfig" );
        SetText( "Processing Config", YellowColor );

        // start reading the config file

        QueryIndex = 0;
        QueryId = llGetNotecardLine( QueryNotecardName, QueryIndex );
    }
    
    dataserver( key queryId, string data ){
        if( queryId != QueryId )
            return;

        if( data == EOF )
            state Running;
        
        string Data = data;     // keep copy for err messages

        // strip comments, leading and trailing whitespace, and ignore blank lines
        data = StripComments( data );
        if( data != "" ){
        
            // parse individual config settings

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
                        default_name = value;
                
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
                
                else if( "ALL_FULLBRIGHT" == setting )    
                        ALL_FULLBRIGHT = (integer)value;

                else if( "NO_FULLBRIGHT" == setting )    
                        NO_FULLBRIGHT = (integer)value;
 
                else
                    StoreImageParams( settingNoUp , llCSV2List( value ));

            } else {
                    Say( "Config:Ignoring: " + Data );
            }
        }

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
        lock();

        InitSidesAndBack();

        pick_texture_name( default_name );

        llListen( PICTURE_CHAN, "", NULL_KEY, "" );
        llListen( DIALOG_CHAN, "", NULL_KEY, "" );
    }

    touch_start( integer total_number ){
        if( !Locked || llDetectedKey( 0 ) == llGetOwner()){
		DialogLaunched = 0;
		start_time = llGetTimeOfDay();
	}
    }
    
    touch( integer number ){
        if( !Locked || llDetectedKey( 0 ) == llGetOwner()){
            float dwell_time = llGetTimeOfDay() - start_time;

            if( !DialogLaunched && dwell_time >= DWELL_THRESHOLD ){
                DialogLaunched = 1;
                show_dialog( llDetectedKey( 0 ));
            }
        }
    }
    
    touch_end(integer total_number){
        if( !Locked || llDetectedKey( 0 ) == llGetOwner()){
            if( !DialogLaunched ){
                pick_next_texture();
            }
        }
    }
    
    listen( integer channel, string name, key id, string message ){
        if( message == CMD_SHOW_DEFAULT ){
            pick_default_texture();
            
        } else if( message == CMD_SET_DEFAULT ){
            MakeCurrentTextureDefault();
            
        } else if( message == CMD_LOCK ){
            lock();
            
        } else if( message == CMD_UNLOCK ){
            unlock();
            
        } else if( message == CMD_NEXT ){
            pick_next_texture();
        
        } else if( message == CMD_START_CYCLE ){
            start_cycle();
        
        } else if( message == CMD_STOP_CYCLE ){
            stop_cycle();
            
        }
    }
    
    timer(){
        if( CycleMode ){
            pick_next_texture();
            llSetTimerEvent( CYCLE_TIME );
        } else
            llSetTimerEvent( 0 );
    }

    changed( integer change ){
        if( change & CHANGED_INVENTORY )
            llResetScript();

        if( change & CHANGED_SCALE )
            ResetAspectRatio( current_ratio );
    }
    
    on_rez( integer param ){
        llResetScript();
    }
}

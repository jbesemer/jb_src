string VERSION = "1.0";

integer TRACE = 0;

integer CHAN = -3141596;    // channel on which to tell rezzed objects to die

string CMD_DIE = "die";

vector DEFAULT_POS = <3., 3., 1.0>;
vector DEFAULT_ROT = ZERO_VECTOR;     // ZERO_ROTATION; // <0.0, 0.0, 0.0, 1.0>;

// colors for status info

vector  ERROR_COLOR      = <1.0, 0.0, 0.0>;
vector  YELLOW_COLOR     = <1.0, 1.0, 0.2>;    // light hard yellow
vector  RED_COLOR        = <1.0, 0.0, 0.0>;
vector  GREEN_COLOR      = <0.0, 1.0, 0.0>;
float   TEXT_ALPHA       = 1.0;

// feedback to users ///////////////////////////////////////////////////////////

Say( string msg ){
    llOwnerSay( msg );
}

Trace( string msg ){
    if( TRACE )
        Say( msg );
}

Trace2( string msg ){
    if( TRACE > 1 )
        Say( msg );
}

SetText( string message, vector color ){
    llSetText( message, color, TEXT_ALPHA );
}

// item data /////////////////////////////////////////////////////////////

list ItemNames;         // names of inventory items
list ItemPos;           // positions of items
list ItemRot;           // rotations of items

integer ITEM_COUNT;     // count of items

integer CurrentItem = 0;

InitItems(){
    ItemNames = [];
    ItemPos = [];
    ItemRot = [];
}

AddItem( string s ){
    // Trace( "Inventory: " + s );
    ItemNames += [ s ];
    ItemPos += [ DEFAULT_POS ];
    ItemRot += [ DEFAULT_ROT ];
}

FetchInventoryNames(){    
    InitItems();

    integer i;
    string s = "Not Null";
    for( i=0; s != ""; i++ ){
        s = llGetInventoryName( INVENTORY_OBJECT, i );
        if( s != "" )
            AddItem( s );
    }

    ITEM_COUNT = llGetListLength( ItemNames );
    Trace( "Total Items: " + (string)ITEM_COUNT );
    CurrentItem = 0;
}

// configuration file processing ///////////////////////////////////////////////

string    CONFIG_SEP = "=";        // separator between name and value in config files
string    ConfigNotecardName = "Configuration";

integer    QueryIndex;
key        QueryId;

string StripComments( string data ){
    integer pos = llSubStringIndex( data, "#" );

    if( pos >= 0 )
        data = llDeleteSubString( data, pos, -1 );

    return llStringTrim( data, STRING_TRIM );
}

StoreConfigParams( list items ){
    string name = llList2String( items, 0 ); 
    if( llGetInventoryType( name ) == INVENTORY_NONE ){
        Say( "Config refs name not in inventory: " + name );
        return;
    }
    
    integer N = llListFindList( ItemNames, [ name ]);
    if( N < 0 ){
        Say( "Config refs name not in name list: " + name );    // "cannot" happne
        return;
    }
    
    vector pos;
    if( llToLower( llList2String( items, 1 )) == "default" )
        pos = DEFAULT_POS;
    else
        pos = (vector)llList2String( items, 1 );
    ItemPos = llListReplaceList( ItemPos, [ pos ], N, N );

    if( llGetListLength( items ) > 2 ){
        vector rot = (vector)llList2String( items, 2 );
        ItemRot = llListReplaceList( ItemRot, [ rot ], N, N );
    }     
}

ProcessConfigLine( string Data ){
    // strip comments, leading and trailing whitespace, and ignore blank lines
    string data = StripComments( Data );
    if( data == "" )
        return;

    if( llSubStringIndex( data, CONFIG_SEP ) >= 0 ){        // "Name=Value" parameters

        list tmp = llParseString2List( data, [CONFIG_SEP], []);
        string settingNoUp = llStringTrim( llList2String( tmp, 0 ), STRING_TRIM );
        string setting = llToUpper( settingNoUp );
        string value = llStringTrim( llList2String( tmp, 1 ), STRING_TRIM );

        Trace( setting + " -> '" + value + "'" );

        if( "TRACE" == setting )
            TRACE = (integer)value;

        else if( "CHAN" == setting )
            CHAN = (integer)value;

        else
            Say( "Config: Ignoring: " + Data );

    } else {
        StoreConfigParams( llCSV2List( data ));
    }
}

DumpConfig(){
    integer N = llGetListLength( ItemNames );
    integer i;
    
    for( i=0; i<N; i++ ){
        Say(
            llList2String( ItemNames, i )
            + ", "
            + (string)llList2Vector( ItemPos, i )
            + ", "
            + (string)llList2Vector( ItemRot, i ));
            
    }
}

// Action routines //////////////////////////////////////////////////////////////

RezObject( integer index ){
    string name = llList2String( ItemNames, index );
    vector pos = (vector)llList2String( ItemPos, index );
    vector vect = (vector)llList2String( ItemRot, index );
    rotation rot = llEuler2Rot( vect * DEG_TO_RAD );
 
    Trace( "Rezzing " + name ); 
    // Trace( "vec2rot: " + (string)vect + " -> " + (string)rot );

    llRezObject( 
        name,
        pos + llGetPos(),
        ZERO_VECTOR,    // never a velocity
        rot,
        CHAN | TRACE );         // tell rez'd object comm chan and if trace should be enabled
}

RezNextObject(){
    RezObject( CurrentItem );
    CurrentItem = ( CurrentItem + 1 ) % ITEM_COUNT;
}

RemovePrevObjects(){
    llRegionSay( CHAN, CMD_DIE );
}

// default/starup state ///////////////////////////////////////////////////////////////

default
{
    state_entry(){
        Say( "Version " + VERSION );
        
        // fetch inventory names
        
        FetchInventoryNames();

        Trace( "Read Configuration" );
        SetText( "Processing Configuration", YELLOW_COLOR );
        QueryIndex = 0;
        QueryId = llGetNotecardLine( ConfigNotecardName, QueryIndex );
    }
    
    state_exit(){
        if( TRACE )
            DumpConfig();
    }

    dataserver( key queryId, string data ){
        if( queryId != QueryId )
            return;

        if( data == EOF ){
            if( QueryIndex == 0 )
                Say( "Warning: missing or empty configuration file" );
            
            state Running;
        }

        ProcessConfigLine( data );

        // fetch next config file line

        QueryId = llGetNotecardLine( ConfigNotecardName, ++QueryIndex );
    }

    
    changed( integer change ){
        if( change & CHANGED_INVENTORY )
            llResetScript();
    }
}

// state Running ///////////////////////////////////////////////////////////////

state Running {
    state_entry(){
        Trace( "Running" );
        SetText( "", GREEN_COLOR );
    }

    touch_start(integer total_number){
        RemovePrevObjects();
        RezNextObject();
    }
    
    changed( integer change ){
        if( change & CHANGED_INVENTORY )
            llResetScript();
    }
}


// watch for and report agents not owned by script owner

string VERSION = "1.0";

// Parameters ////////////////////////////////////////////

integer TRACE = 0;

// 4K sqare property = 64 x 64 => 32 radius minima, 45.254833 radius to maxima

float MAX_RANGE = 96.0;
float SENSOR_RADIUS = MAX_RANGE;
float REPEAT_PERIOD = 3.0;

// Constants ////////////////////////////////////////////////

vector COLOR_ACTIVE = <0,1,0>;
vector COLOR_INACTIVE = <0,0,1>;
vector  ErrorColor      = <1., 0., 0.>;
vector  YellowColor     = <1., 1., 0.2>;    // light hard yellow
vector  RedColor        = <1., 0., 0.>;
vector  GreenColor      = <0., 1., 0.>;
float   TextAlpha       = 1.0;

integer CMD_CHAN_BASE = 160000;
integer CMD_CHAN_RANGE = 10000;
integer CMD_CHAN;   // ranges from -160000 thru -169999
integer ListenHandle;

string CMD_ARM = "activated";
string CMD_DISARM = "deactivated";

string CONFIG_SEP = "=";

list buttons = [
    CMD_ARM,
    CMD_DISARM
	];

// Variables ///////////////////////////////////////////////////////

string  QueryNotecardName = "Configuration";
integer QueryIndex;
key     QueryId;

list Trustees = [];
list Owners = [];
list Names = [];


// Helpers ////////////////////////////////////////////////////

Say( string msg )
{
    llOwnerSay( msg );
    // llShout( msg );
}

Trace( string msg )
{
    if( TRACE )
        Say( msg );
}

string strip_comments( string data )
{
    integer pos = llSubStringIndex( data, "#" );

    if( pos >= 0 )
        data = llDeleteSubString( data, pos, -1 );
    return llStringTrim( data, STRING_TRIM );
}

string UnQuote( string s )
{
    s = llStringTrim( s, STRING_TRIM );

    if( llGetSubString( s, 0, 0 ) == "\"" )
        s = llGetSubString( s, 1, -1 );
    if( llGetSubString( s, -1, -1 ) == "\"" )
        s = llGetSubString( s, 0, -2 );

    return s;
}

integer same( string a, string b )
{
    return llToLower( a ) == llToLower( b );
}

string FormName( string name, list owners, integer index )
{
	return llList2String( owners, index ) + ":" + name ;
}

// principal actions

NotifyServer( string action, string name )
{
    string url =         "http://cascade-sys.com/cgi-bin/visitor.cgi"
            + "?time="
            + llGetTimestamp()
            + "&sensor="
            + llGetObjectName()
            + "&action="
            + action
            + "&name="
            + llEscapeURL(name);

    // llOwnerSay( "sending: " + url );
    llHTTPRequest(
        url,
        [],
        "" );
}

departed( string name )
{
    Say( "Departure: " + name );
//    Log = ( Log = []) + Log + [ llGetTimestamp() + " gone " + name ];
    NotifyServer( "Departure", name );
}

arrived( string name )
{
    Say( "Intrusion: " + name );
//    Log = ( Log = []) + Log + [ llGetTimestamp() + " HERE " + name ];
    NotifyServer( "Intrusion", name );
}

// script only listens while dialog is up

show_menu()
{
    if( llDetectedOwner( 0 ) != llGetOwner()){
        llSay( 0, "Only respond to owner" );
        return;
    }

    clear_menu();
    CMD_CHAN = - CMD_CHAN_BASE - (integer)llFrand( CMD_CHAN_RANGE );
    ListenHandle = llListen( CMD_CHAN, "", llGetOwner(), "" );
    llDialog( llGetOwner(), "Select Function", buttons, CMD_CHAN );
    llSetTimerEvent( 60*3 );
}

clear_menu()
{
    llSetTimerEvent( 0 );
    llListenRemove( ListenHandle );
}


// default/startup state ////////////////////

default
{
    state_entry()
	{
        Say( llGetScriptName() + ": Version: " + VERSION );
        state ReadConfig;
    }
}


// ReadConfig state //////////////////////////////////////////

state ReadConfig
{
    state_entry()
	{
        Say( "ReadConfig" );
        llSetText( "Processing Config", YellowColor, TextAlpha );
        llSetColor( YellowColor, ALL_SIDES );

        // start reading the config file

        QueryIndex = 0;
        QueryId = llGetNotecardLine( QueryNotecardName, QueryIndex );
    }

    state_exit()
	{
        Say( " Free Memory: " + (string)llGetFreeMemory());
    }

    dataserver( key queryId, string data )
	{
        if( queryId != QueryId )
            return;

        if( data == EOF )
            state Active;

        string Data = data;     // keep copy for err messages

        // strip comments, leading and trailing whitespace, and ignore blank lines
        data = strip_comments( data );
        if( data != "" ){

            // parse individual config settings

            if( llSubStringIndex( data, CONFIG_SEP ) >= 0 ){
                list tmp = llParseString2List( data, [CONFIG_SEP], []);
                string setting = llToUpper( llStringTrim( llList2String( tmp, 0 ), STRING_TRIM ));
                string value = llStringTrim( llList2String( tmp, 1 ), STRING_TRIM );

                Trace( setting + " -> " + value );

                     if( "SENSOR_RADIUS" == setting )
                        SENSOR_RADIUS = (float)value;

                else if( "REPEAT_PERIOD" == setting )
                        REPEAT_PERIOD = (float)value;

                else if( "TRACE" == setting )
                        TRACE = (integer)value;

                else if( "TRUSTEES" == setting ){
                    list names = llCSV2List( value );
                    if( llGetListLength( names ) > 0 )
                        Trustees = llListInsertList( Trustees, names, llGetListLength( Owners ));
                    Say( "Trustees: " + (string)Trustees);

                } else
                    Say( "Config:Ignoring: " + Data );

            } else
                Say( "Config:Missing '" + CONFIG_SEP + "' in: " + Data );
        }

        // fetch next config file line

        QueryId = llGetNotecardLine( QueryNotecardName, ++QueryIndex );
    }

    changed( integer change )
	{
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }

    on_rez( integer param )
	{
        llResetScript();
    }
}


// inactive state ////////////////////

state Inactive
{
    state_entry()
	{
        llSetColor( COLOR_INACTIVE, ALL_SIDES );
        llSetText( "Inactive", RedColor, TextAlpha );
        Say( "Deactivated" );
    }

    touch_start(integer num_detected)
	{
        show_menu();
    }

    timer()
	{
        clear_menu();
    }

    listen( integer chan, string name, key id, string message )
	{
        clear_menu();

        if( message == CMD_ARM )
            state Active;
        else if( message == CMD_DISARM )
            state Inactive;
        else
            Say(
                llGetScriptName()
                + ": Ignoring: "
                + message
                + " on "
                + (string)chan );
    }

    changed( integer change )
	{
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }

    on_rez( integer param )
	{
        llResetScript();
    }
}

// active state ////////////////////////////////

state Active
{
    state_entry()
	{
        Names = [];
        Owners = [];
        llSetText( "Active", GreenColor, TextAlpha );
        llSetColor( COLOR_ACTIVE, ALL_SIDES );
        Say( "Activated" );

        // llSensorRepeat( "", "", AGENT, SENSOR_RADIUS, PI, REPEAT_PERIOD );
        llSensorRepeat( "", "", (ACTIVE | PASSIVE | SCRIPTED), SENSOR_RADIUS, PI, REPEAT_PERIOD );
    }

    state_exit()
	{
        llSensorRemove();
    }

    touch_start(integer num_detected)
	{
        show_menu();
    }

    timer()
	{
        clear_menu();
    }

    listen( integer chan, string name, key id, string message )
	{
        clear_menu();

        if( message == CMD_ARM )
            state Active;
        else if( message == CMD_DISARM )
            state Inactive;
        else
            Say(
                llGetScriptName()
                + ": Ignoring: "
                + message
                + " on "
                + (string)chan );
    }

    sensor(integer num_detected)
	{
        list NewNames = [];
        list NewOwners = [];
        integer i, count;

        for( i=0; i < num_detected ; ++i ){
			key owner = llDetectedOwner( i );
			if( owner != llGetOwner()){
				NewNames += [ llDetectedName( i )];
				NewOwners += [ owner ];
			}
        }

        // see who's new
		count = llGetListLength( NewNames );
        for( i=0; i < count; ++i ){
            string name = llList2String( NewNames, i );
            if( llListFindList( Names, [ name ]) == -1 ){
                arrived( FormName( name, NewOwners, i ));
			}
        }

        // see who's left
		count = llGetListLength( Names );
        for( i=0; i < count; ++i ){
            string name = llList2String( Names, i );
            if( llListFindList( NewNames, [ name ]) == -1 ){
                departed( FormName( name, Owners, i ));
			}
        }

        Names = NewNames;
        Owners = NewOwners;
    }

    no_sensor()
	{
        integer count = llGetListLength( Names );
        integer i;

        for( i=0; i < count ; ++i ){
            departed( FormName( llList2String( Names, i ), Owners, i ));
        }

        Names = [];
        Owners = [];
    }

	// arrived() and departed() submit http requests
    http_response(key id, integer status, list meta, string body)
	{
        if ( status == 499 )
            llOwnerSay("name2key request timed out");
        else if ( status != 200 )
            llOwnerSay("the internet exploded!!");
    }


    changed( integer change )
	{
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }

    on_rez( integer param )
	{
        llResetScript();
    }
}


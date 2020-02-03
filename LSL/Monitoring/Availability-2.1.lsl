string VERSION = "2.1";

integer TRACE = 1;

integer CHAN = 888;

vector  TextColor       = <1,1,0>;
vector  ErrorColor      = <1,0,0>;
vector  GREEN_COLOR      = <0.0, 1.0, 0.0>;
vector  YELLOW_COLOR    = <1.0, 1.0, 0.2>;    // light hard yellow
float   TextAlpha       = 1.0;
float   TEXT_ALPHA       = 1.0;
float   TEXT_ALPHA2      = 0.2;

integer RETRY_COUNT_MAX = 3;

string MONITOR_URL = "http://cascade-sys.com/cgi-bin/lookupavname.cgi/watch";

key PRI1_SOUND = "219c5d93-6c09-31c5-fb3f-c5fe7495c115";

string CONFIG_SEP = "=";        // separator between name and value in config files

integer REPEAT_INTERVAL = 5;

list Names = [];    // list of names to scan for
list Keys = [];     // list of keys corresponding to the names
list Flags = [];     // associated priority flag
list Online = [];   // online/offline status of corresponding name
list QID = [];      // current outstanding QuereyID for corresponding name

integer NAME_COUNT = 0;

float   DWELL_THRESHOLD = 4.0;
float   touch_start_time;

string  QueryNotecardName = "Configuration";
integer QueryIndex;
key     QueryId;

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

AddNameAndKey( list fields )
{
    string k = llList2String( fields, 0 );
    string name = llList2String( fields, 1 );
    integer pri = (integer)llList2String( fields, 2 );

    Trace( name + " -> " + k + ", " + (string)pri );
    Names += [ llStringTrim( name, STRING_TRIM )];
    NAME_COUNT = llGetListLength( Names );
    Keys += [ k ];
    Flags += [ pri ];
    Online += [ -1 ];
    QID += [ NULL_KEY ];
}

AddNamesAndKeys( string body )
{
    list lines = llParseString2List( body, ["\n"], [] );
    integer N = llGetListLength( lines );
    integer i;

    for( i=0; i<N; i++ ){
        string line = llList2String( lines, i );
        list fields = llParseString2List( line, [","], []);
        if( llGetListLength( fields ) >= 3 )
            AddNameAndKey( fields );
    }
}

showAllOnlineFriends()
{
    string friends = "";
    string sep = "";
    integer i;
    
    for( i=0; i < NAME_COUNT; i++ ){
        integer isOnline = llList2Integer( Online, i );
        if( isOnline ){
            string name = llList2String( Names, i );
            friends += sep + name;
            sep = "\n";
        }
    }

    llSetText( 
        friends,
        TextColor, 
        TextAlpha );
}

showStatus( integer index, integer isOnline )
{
    string name = llList2String( Names, index );
    if( isOnline )
        llOwnerSay( "ONline: " + name  );
    else
        llOwnerSay( "OFFline:      " + name );
}

showAllStatus()
{
    integer i;
    
    for( i=0; i < NAME_COUNT; i++ ){
        showStatus( i, llList2Integer( Online, i ));
    }
    //         llSetText( "Now Playing:\n" 
}

updateOnline( key qid, integer data)
{
    integer N = llListFindList( QID, [ qid ]);
    
    if( N >= 0 ){
        integer WasOnline = llList2Integer( Online, N );
        integer Pri = llList2Integer( Flags, N );
        Online = llListReplaceList(Online, [data], N, N );
        if( WasOnline < data && Pri == 1 )
            llPlaySound( PRI1_SOUND, 1.0 );
        if( WasOnline != data ){
            showStatus( N, data );
            showAllOnlineFriends();
        }
    }
}

queueRequests()
{
    integer i;
    
    // llOwnerSay( "Making Requests" );
    for( i=0; i < NAME_COUNT; i++ ){
        string uuid = llList2String( Keys, i );
        key qid = llRequestAgentData((key)uuid, DATA_ONLINE); // 0.1 sec delay
        QID = llListReplaceList( QID, [ qid ], i, i );
    }
    // llOwnerSay( "Requests Made" );
}

key http_request_id;
integer RetryCount;

SubmitMonitorRequest( integer skip )
{
    string body;
    if( skip > 0 )
        body = "skip=" + (string)skip;
    else
        body = "";

    http_request_id
        = llHTTPRequest(
            MONITOR_URL,
        [ HTTP_METHOD, "POST",
        HTTP_MIMETYPE, "application/x-www-form-urlencoded" ],
        body );
}

default 
{
    state_entry()
    {
        llOwnerSay( "Restarting" );
        llSetText( 
            "[ Initializing ]",
            TextColor, 
            TextAlpha );
            
        QueryIndex = 0;
        QueryId = llGetNotecardLine( QueryNotecardName, QueryIndex );
    }
    
    dataserver( key queryId, string data ){
        if( queryId != QueryId )
            return;

        if( data == EOF )
            state FetchNamesAndKeys;

        string Data = data;     // keep copy for err messages

        // strip comments, leading and trailing whitespace, and ignore blank lines
        data = StripComments( data );
        if( data != "" ){

            // parse individual config settings

            if( llSubStringIndex( data, CONFIG_SEP ) >= 0 ){
                list tmp = llParseString2List( data, [CONFIG_SEP], []);
                string setting = llToUpper( llStringTrim( llList2String( tmp, 0 ), STRING_TRIM ));
                string value = llList2String( tmp, 1 );

                Trace( setting + " -> " + value );

                if( "TRACE" == setting )
                    TRACE = (integer)value;

                else if( "REPEAT_INTERVAL" == setting )
                    REPEAT_INTERVAL = (integer)value;

                else
                    Say( "Config:Ignoring: " + Data );
            } else
                Say( "Config:Missing '" + CONFIG_SEP + "' in: " + Data );
        }
        QueryId = llGetNotecardLine( QueryNotecardName, ++QueryIndex );
    }
    
    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }
    
    on_rez( integer param ){
        llResetScript();
    }
}


// LookupKeys state //////////////////////////////////////////

state FetchNamesAndKeys {
    state_entry() {
        Say( "Fetch Names Free Memory: " + (string)llGetFreeMemory());
        SetText( "Fetching Names", YELLOW_COLOR );
        SubmitMonitorRequest( 0 );
    }

    http_response(key id, integer status, list meta, string body)
    {
        if ( id != http_request_id )
            return;

        integer count = NAME_COUNT;
        
        if ( status == 200 ){
            AddNamesAndKeys( body );
            if( count == NAME_COUNT )
                state Running;

        } else if( RetryCount++ >= RETRY_COUNT_MAX ){
            return;
        }
        
        SubmitMonitorRequest( NAME_COUNT );
    }

    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }

    on_rez( integer param ){
        llResetScript();
    }
}


// Running State //////////////////////////////////////////////

state Running {
    state_entry()
    {
        llSetText( "Running", GREEN_COLOR, TEXT_ALPHA2 );
        Say( "Running Free Memory: " + (string)llGetFreeMemory());

        queueRequests();
        llSetTimerEvent( REPEAT_INTERVAL );
    }

    timer()
    {
        queueRequests();
    }

    dataserver(key queryid, string data)
    {
        updateOnline( queryid, (integer)data );
    }

    touch_start( integer total_number ){
        if( llDetectedKey( 0 ) != llGetOwner()){
            llSay( 0, "Only owner can operate" );
            return;
        }

        touch_start_time = llGetTimeOfDay();
        Say( "Will reset in " + (string)DWELL_THRESHOLD + " sec." );
    }

    touch( integer number ){
        if( llDetectedKey( 0 ) != llGetOwner())
            return;

        float dwell_time = llGetTimeOfDay() - touch_start_time;

        if( dwell_time >= DWELL_THRESHOLD ){
            llResetScript();
        }
    }

    touch_end(integer total_number){
        if( llDetectedKey( 0 ) != llGetOwner())
            return;

        Say( "Reset cancelled" );
    }

    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }

    on_rez( integer param ){
        llResetScript();
    }
}

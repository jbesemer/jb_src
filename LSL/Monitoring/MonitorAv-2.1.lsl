string VERSION = "2.1";

integer TRACE = 0;
integer TESTING = 0;

// colors for status info

vector  ERROR_COLOR      = <1.0, 0.0, 0.0>;
vector  YELLOW_COLOR     = <1.0, 1.0, 0.2>;    // light hard yellow
vector  RED_COLOR        = <1.0, 0.0, 0.0>;
vector  GREEN_COLOR      = <0.0, 1.0, 0.0>;
float   TEXT_ALPHA       = 1.0;
float   TEXT_ALPHA2      = 0.2;

string CONFIG_SEP = "=";        // separator between name and value in config files

float   DWELL_THRESHOLD = 4.0;
float   touch_start_time;

integer RETRY_COUNT_MAX = 3;
integer REPEAT_INTERVAL = 200;

string UPDATE_URL = "http://cascade-sys.com/cgi-bin/avatar.cgi";
string MONITOR_URL = "http://cascade-sys.com/cgi-bin/lookupavname.cgi/monitor";

// two levels of text output to owner

Say( string msg )
{
    llOwnerSay( msg );
}

Trace( string msg )
{
    if( TRACE )
        Say( msg );
}

Trace2( string msg )
{
    if( TRACE > 1 )
        Say( msg );
}

SetText( string message, vector color )
{
    llSetText( message, color, TEXT_ALPHA );
}

// major data structures //////////////////////////////////////////////

list Names = [];    // list of names to scan for
list Keys = [];     // list of keys corresponding to the names
list Flags = [];     // associated priority flag
list Online = [];   // online/offline status of corresponding name
list QID = [];      // current outstanding QuereyID for corresponding name
list Times = [];    // time of last status

integer NAME_COUNT = 0;

// for reading config file ////////////////////////////////////////////

string  QueryNotecardName = "Configuration";
integer QueryIndex;
key     QueryId;

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

    Trace2( name + " -> " + k + ", " + (string)pri );
    
    Names += [ llStringTrim( name, STRING_TRIM )];
    NAME_COUNT = llGetListLength( Names );
    Keys += [ k ];
    Flags += [ pri ];
    Online += [ -1 ];
    QID += [ NULL_KEY ];
    Times += [ "" ];
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


// for querying and updating status ///////////////////////////////////

UpdateOnlineStatus( key qid, integer data)
{
    integer N = llListFindList( QID, [ qid ]);

    OnlineUpdates++;

    if( N >= 0 ){
        Trace2( "Update: " + (string)data + " " + llList2String( Names, N ));
        string ts = llGetTimestamp();
        // integer WasOnline = llList2Integer( Online, N );
        Online = llListReplaceList( Online, [ data ], N, N );
        Times = llListReplaceList( Times, [ ts ], N, N );
    } else
        Say( "Unexpected OnlineStatus qid: " + (string)qid );
}

integer OnlineUpdates;

QueueOnlineRequests()
{
    Trace( "QueueOnlineRequests: " + (string)NAME_COUNT );
    OnlineUpdates = 0;

    integer i;
    for( i=0; i < NAME_COUNT; i++ ){
        string uuid = llList2String( Keys, i );
        key qid = llRequestAgentData((key)uuid, DATA_ONLINE ); // 0.1 sec delay
        QID = llListReplaceList( QID, [ qid ], i, i );
    }
    
    Trace2( "QueueOnlineRequests DONE" );
}

// HTTP requests //////////////////////////////////////////////////////

key http_request_id;
integer RetryCount;

SubmitHttpPost( string body )
{
    Trace2( "SubmitHttpPost: " + body );

    if( !TESTING )
        http_request_id
            = llHTTPRequest(
                UPDATE_URL,
        [ HTTP_METHOD, "POST",
        HTTP_MIMETYPE, "application/x-www-form-urlencoded" ],
        body );
}

SubmitMonitorRequest( integer skip )
{
    if( !TESTING ){
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
}

string NameValuePair( string name, string value )
{
    return llEscapeURL( name ) + "=" + llEscapeURL( value );
}

string AddMemoryUpdate()
{
    return "&" + NameValuePair( "memory", (string)llGetFreeMemory())
        + "&" + NameValuePair( "time", llGetTimestamp());
}

SubmitUpdate()
{
    Say( "Submitting Update: " + (string)OnlineUpdates );
    string body = "";
    integer i;

    for( i=0; i < NAME_COUNT; i++ )
    {
        if( i > 0 )
            body += "&";    // between each pair

        string name = "u";
        string value
            = llList2String( Names, i )
                + ","
                + (string)llList2Integer( Online, i )
                + ","
                + llList2String( Times, i );
        body += NameValuePair( name, value );

        Trace2( "SubmitUpdate: " + value + " " + name  );
    }

    body += AddMemoryUpdate();

    SubmitHttpPost( body );
}

NotifyEvent( string message )
{
    string URL = UPDATE_URL
        + "?"
        + NameValuePair( "event", message )
        + "&"
        + NameValuePair( "time", llGetTimestamp());

    Trace( "Notify " + URL );

    http_request_id = llHTTPRequest( URL, [], "" );
}


// default/startup state ////////////////////////////////////////

default {
    state_entry()
    {
        SetText( "[wait]", RED_COLOR );
        NotifyEvent( "Restarting "
            + llGetObjectName()
            + " "
            + llGetScriptName()
            + " "
            + (string)llGetKey());
    }

    http_response(key id, integer status, list meta, string body)
    {
        state ReadConfig;
    }

    state_exit(){
        Say( "Initial Free Memory: " + (string)llGetFreeMemory());
    }
}

// ReadConfig state //////////////////////////////////////////

state ReadConfig {
    state_entry(){
        Say( "ReadConfig" );
        SetText( "Processing Config", YELLOW_COLOR );

        // start reading the config file

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

                else if( "TESTING" == setting )
                    TESTING = (integer)value;

                else if( "RETRY_COUNT_MAX" == setting )
                    RETRY_COUNT_MAX = (integer)value;

                else if( "REPEAT_INTERVAL" == setting )
                    REPEAT_INTERVAL = (integer)value;

                //    else if( "UPDATE_URL" == setting )
                //        UPDATE_URL = value;

                //  else if( "NAME2KEY_URL" == setting )
                //      NAME2KEY_URL = value;

                //  else if( "NAME" == setting || "NAMES" == setting )
                //      AddNames( llCSV2List( value ));

                else
                    Say( "Config:Ignoring: " + Data );
            } else
            Say( "Config:Missing '" + CONFIG_SEP + "' in: " + Data );
        }

        // fetch next config file line

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
    
    state_exit(){
        Trace( "Names: " + (string)NAME_COUNT );
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

        llSetTimerEvent( REPEAT_INTERVAL );
        QueueOnlineRequests();
    }

    timer()
    {
        SubmitUpdate();
        QueueOnlineRequests();
    }

    dataserver(key queryid, string data)
    {
        UpdateOnlineStatus( queryid, (integer)data );
    }

    http_response(key id, integer status, list meta, string body)
    {
        if ( id != http_request_id )
            return;
            
        if( status == 200 )
            Trace( "http response OK" );
        else
            Trace( "http response bad: " + (string)status );
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

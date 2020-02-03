// MonitorAv-A -- setup and scan for changes

string    VERSION = "3.1";

integer TRACE = 0;

integer    CMD_OFFLINE = 0;            // same as online status code
integer    CMD_ONLINE = 1;            // same as online status code
integer    CMD_SEND_BUFFER = 2;
integer    CMD_RESET_BUFFER = 3;
integer    CMD_INIT = 4;

// colors for status info

vector  ERROR_COLOR      = <1.0, 0.0, 0.0>;
vector  YELLOW_COLOR     = <1.0, 1.0, 0.2>;    // light hard yellow
vector  RED_COLOR        = <1.0, 0.0, 0.0>;
vector  GREEN_COLOR      = <0.0, 1.0, 0.0>;
float   TEXT_ALPHA       = 1.0;
float   TEXT_ALPHA2      = 0.2;

string    CONFIG_SEP = "=";        // separator between name and value in config files

float   DWELL_THRESHOLD = 4.0;
float   touch_start_time;

integer REPEAT_INTERVAL = 200;                    // seconds
integer MASTER_UPDATE_INTERVAL = 0; //3600;    // seconds (0 => never)

string    UPDATE_URL = "http://cascade-sys.com/cgi-bin/avatar.cgi";
string    MONITOR_URL = "http://cascade-sys.com/cgi-bin/lookupavname.cgi/monitor";

// two levels of text output to owner

Say( string msg ){
    llOwnerSay( "A: " + msg );
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

// major data structures //////////////////////////////////////////////

list Names = [];    // list of names to scan for
list Keys = [];     // list of keys corresponding to the names
// list Flags = [];     // associated priority flag
list Online = [];   // most recent online/offline status of corresponding name
list Times = [];    // time of last status update

integer NAME_COUNT = 0;

// loading user names and data ////////////////////////////////////////

AddNameAndKey( list fields ){
    string k = llList2String( fields, 0 );
    string name = llList2String( fields, 1 );
    integer pri = (integer)llList2String( fields, 2 );

    Trace2( name + " -> " + k + ", " + (string)pri );

    Names += [ llStringTrim( name, STRING_TRIM )];
    NAME_COUNT = llGetListLength( Names );

    Keys += [ k ];
    // Flags += [ pri ];
    // Online += [ -1 ];    // forces first readings to be all updates
    Times += [ "" ];
}

AddNamesAndKeys( string body ){
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


integer MasterUpdateElapsed = 0;

ResetOnlineStatus(){
    MasterUpdateElapsed = 0;
    Online = [];

    integer i;
    for( i=0; i<NAME_COUNT; i++ ){
        Online += [ -1 ];    // forces next readings to be all updates
    }
}

UpdateMasterInterval(){
    if( MASTER_UPDATE_INTERVAL > 0 ){
        MasterUpdateElapsed += REPEAT_INTERVAL;
        if( MasterUpdateElapsed >= MASTER_UPDATE_INTERVAL )
            ResetOnlineStatus();
    }
}

// Link message forwarding ////////////////////////////////////////////

SendLinkMessage( integer cmd ){
    llMessageLinked( LINK_THIS, cmd, "", NULL_KEY );
}

SendLinkResetBuffer(){
    SendLinkMessage( CMD_RESET_BUFFER );
}

SendLinkSendBuffer(){
    SendLinkMessage( CMD_SEND_BUFFER );
}

SendLinkInit(){
    llMessageLinked( LINK_THIS, CMD_INIT, (string)TRACE, NULL_KEY );
}

SendLinkStatusChanged( string name, integer isOnline, string time ){
    llMessageLinked( LINK_THIS, isOnline, name, time );
}

// for querying and recording status ///////////////////////////////////

// The strategy here is to submit status requests one at a time and wait for the reply.
// The reply handler checks for transitions and updates the update buffer with any changes.
// When all entries have been updated, the changes (if any) are sent to the server.
// This cascade of events is triggered in Running.state_entry, and in the Running.timer handler.
//
// Cascade chain is as follows:
//
//        QueueFirstOnlineRequest -> UpdateOnlineStatus <-> QueueNextOnlineRequest -> SubmitUpdate

integer CurrentIndex;
integer UpdateCount;
key     QueryId;

// list helpers for accessing items at CurrentIndex

integer CurrentInt( list name ){
    return llList2Integer( name, CurrentIndex );
}

string CurrentString( list name ){
    return llList2String( name, CurrentIndex );
}

// shit -- this doesn't work -- system hangs after the replace, with 12K free before the function call
//      with the call inline, the program runs to completion with a steady 12K free
//
//  list ReplaceCurrent( list name, list item ){
//      Trace2( "Memory2: " + (string)llGetFreeMemory());
//      list r = llListReplaceList( name, [ item ], CurrentIndex, CurrentIndex );
//      Trace2( "Memory3: " + (string)llGetFreeMemory());
//      return r;
//  }

// request queuing

QueueCurrentOnlineRequest(){
    Trace2( "QueueCurrentOnlineRequest[ " + (string)CurrentIndex + " ]: " + CurrentString( Names ));
    QueryId = llRequestAgentData((key)CurrentString( Keys ), DATA_ONLINE ); // 0.1 sec delay
}

QueueFirstOnlineRequest(){
    UpdateCount = 0;
    CurrentIndex = 0;

    QueueCurrentOnlineRequest();
}

QueueNextOnlineRequest(){
    if( ++CurrentIndex < NAME_COUNT )
        QueueCurrentOnlineRequest();
    else
        SubmitUpdate();
}

// formatting update buffer

AppendUpdateEntry( string name, integer isOnline, string t1, string t2 ){
    if( t1 != "" )
        SendLinkStatusChanged( name, 1 - isOnline, t1  );
    SendLinkStatusChanged( name, isOnline, t2 );
    UpdateCount++;
}

UpdateOnlineStatus( key qid, integer isOnline ){
    if( qid == QueryId ){
        string name = CurrentString( Names );
        integer wasOnline = CurrentInt( Online );
        string curTime = llGetTimestamp();

        Trace2( "Update: " + name + ": " + (string)wasOnline + " -> " + (string)isOnline );

        if( isOnline != wasOnline ){
            Trace( "Update: " + name + ": " + (string)wasOnline + " -> " + (string)isOnline );
            string prevTime = CurrentString( Times );
            AppendUpdateEntry( name, isOnline, prevTime, curTime );
            Online = llListReplaceList( Online, [ isOnline ], CurrentIndex, CurrentIndex );        
        }
        Times = llListReplaceList( Times, [ curTime ], CurrentIndex, CurrentIndex );        
    } else
        Say( "Unexpected query ID: " + (string)qid );

    QueueNextOnlineRequest();
}

// HTTP requests //////////////////////////////////////////////////////

key http_request_id;

SubmitHttpPost( string why, string url, string body ){
    Trace( "SubmitHttpPost-A." + why + ": " + url );

    http_request_id
        = llHTTPRequest(
            url,
            [ HTTP_METHOD, "POST",
                HTTP_MIMETYPE, "application/x-www-form-urlencoded" ],
            body );
            
    if( http_request_id == NULL_KEY ){
        Say( "#### SubmitHttpPost: request failed or denied" );
    } else {    
        Trace( "SubmitHttpPost-A.id:" + (string)http_request_id );
        Trace2( "SubmitHttpPost-A.body: " + body );
    }
}

SubmitMonitorRequest( integer skip ){
    string body;
    if( skip > 0 )
        body = "skip=" + (string)skip;
    else
        body = "";

    SubmitHttpPost( "MonitorRequest[ " + (string)skip + " ]", MONITOR_URL, body );
}

SubmitUpdate(){
    Trace( "Submitting Update: " + (string)UpdateCount );
    if( UpdateCount > 0 )
        SendLinkSendBuffer();
//    else
//        Trace( "No changes => no Submission" );
}

NotifyEvent( string message ){
    string body
        = NameValuePair( "event", message )
            + "&"
            + NameValuePair( "time", llGetTimestamp());

    SubmitHttpPost( "NotifyEvent", UPDATE_URL, body );
}

string NameValuePair( string name, string value ){
    return llEscapeURL( name ) + "=" + llEscapeURL( value );
}

integer ProcessHttpResponse(key id, integer status, list meta, string body){
    if ( id != http_request_id ){
        Say( "Spurious http response-A: " + (string)id );
        return 0;
    }

    if( status == 200 ){
        Trace2( "http response OK" );
        return 1;
    } else {
        Say( "http response bad: " + (string)status );
        return 0;
    }
}

// default/startup/ReadConfig state ///////////////////////////////////////

default {
    state_entry(){
        Say( "\n================================================\n"
            + "Initial Free Memory:\n" + (string)llGetFreeMemory());
        SetText( "[wait]", RED_COLOR );

        SendLinkResetBuffer();

        NotifyEvent(
            "Restarting "
            + llGetObjectName()
            + " "
            + llGetScriptName());
    }

    http_response(key id, integer status, list meta, string body){
        if( ProcessHttpResponse(id, status, meta, body))
            state FetchNamesAndKeys;
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
        Trace( "Fetch Names Free Memory: " + (string)llGetFreeMemory());
        SetText( "Fetching Names", YELLOW_COLOR );
        SubmitMonitorRequest( 0 );
    }

    state_exit(){
        Say( "Name Count: " + (string)NAME_COUNT );
        ResetOnlineStatus();
        SendLinkInit();
    }

    http_response(key id, integer status, list meta, string body){
        integer count = NAME_COUNT;

        if( ProcessHttpResponse( id, status, meta, body )){
            AddNamesAndKeys( body );
            if( count == NAME_COUNT )    // if none added
                state Running;
        }

        // if there's an error, tihs will retry forever
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
    state_entry(){
        llSetText( "Running", GREEN_COLOR, TEXT_ALPHA2 );
        Say( "A-Running Free Memory: " + (string)llGetFreeMemory());

        QueueFirstOnlineRequest();

        llSetTimerEvent( REPEAT_INTERVAL );
    }

    timer(){
        Trace2( "Timer tick" );
        UpdateMasterInterval();
        QueueFirstOnlineRequest();
    }

    dataserver(key queryid, string data){
        UpdateOnlineStatus( queryid, (integer)data );
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

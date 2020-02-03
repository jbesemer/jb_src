string	VERSION = "3.0";

integer TRACE = 2;
integer TESTING = 0;

// colors for status info

vector  ERROR_COLOR      = <1.0, 0.0, 0.0>;
vector  YELLOW_COLOR     = <1.0, 1.0, 0.2>;    // light hard yellow
vector  RED_COLOR        = <1.0, 0.0, 0.0>;
vector  GREEN_COLOR      = <0.0, 1.0, 0.0>;
float   TEXT_ALPHA       = 1.0;
float   TEXT_ALPHA2      = 0.2;

string	CONFIG_SEP = "=";        // separator between name and value in config files

float   DWELL_THRESHOLD = 4.0;
float   touch_start_time;

integer REPEAT_INTERVAL = 200;					// seconds
integer MASTER_UPDATE_INTERVAL = 0; //3600;	// seconds

string	UPDATE_URL = "http://cascade-sys.com/cgi-bin/avatar.cgi";
string	MONITOR_URL = "http://cascade-sys.com/cgi-bin/lookupavname.cgi/monitor";

// two levels of text output to owner

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

// major data structures //////////////////////////////////////////////

list Names = [];    // list of names to scan for
list Keys = [];     // list of keys corresponding to the names
list Flags = [];     // associated priority flag
list Online = [];   // online/offline status of corresponding name
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

AddNameAndKey( list fields ){
    string k = llList2String( fields, 0 );
    string name = llList2String( fields, 1 );
    integer pri = (integer)llList2String( fields, 2 );

    Trace2( name + " -> " + k + ", " + (string)pri );

    Names += [ llStringTrim( name, STRING_TRIM )];
    NAME_COUNT = llGetListLength( Names );

    Keys += [ k ];
    Flags += [ pri ];
    // Online += [ -1 ];	// forces first readings to be all updates
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
	integer i;
	Online = [];
	for( i=0; i<NAME_COUNT; i++ ){
		Online += [ -1 ];	// forces next readings to be all updates
	}

	MasterUpdateElapsed = 0;
}

UpdateMasterInterval(){
	if( MASTER_UPDATE_INTERVAL > 0 ){
		MasterUpdateElapsed += REPEAT_INTERVAL;
		if( MasterUpdateElapsed >= MASTER_UPDATE_INTERVAL )
			ResetOnlineStatus();
	}
}

// for querying and recording status ///////////////////////////////////

// The strategy here is to submit status requests one at a time and wait for the reply.
// The reply handler checks for transitions and updates the update buffer with any changes.
// When all entries have been updated, the changes (if any) are sent to the server.
// This cascade of events is triggered in Running.state_entry, and in the Running.timer handler.
//
// Cascade chain is as follows:
//
//		QueueFirstOnlineRequests -> UpdateOnlineStatus <-> QueueNextOnlineRequests -> SubmitUpdate

integer CurrentIndex;
integer UpdateCount;	// number of entries = 2X actual number of changes
string UpdateBuffer;	// update buffer, incrementally constructed

// list helpers for accessing items at CurrentIndex

integer CurrentInt( list name ){
	return llList2Integer( name, CurrentIndex );
}

string CurrentString( list name ){
	return llList2String( name, CurrentIndex );
}

list ReplaceCurrent( list name, list item ){
	return llListReplaceList( name, [ item ], CurrentIndex, CurrentIndex );
}

// request queuing

QueueOnlineRequests(){
    Trace( "QueueOnlineRequests: " + (string)CurrentIndex );
	QueryId = llRequestAgentData((key)CurrentString( Keys ), DATA_ONLINE ); // 0.1 sec delay
}

QueueFirstOnlineRequests(){
	UpdateBuffer = "";
	UpdateCount = 0;
    CurrentIndex = 0;
	QueueOnlineRequests();
}

QueueNextOnlineRequests(){
	if( ++CurrentIndex < NAME_COUNT )
		QueueOnlineRequests();
	else
		SubmitUpdate();
}

// formatting update buffer

string NameValuePair( string name, string value ){
    return llEscapeURL( name ) + "=" + llEscapeURL( value );
}

AppendEntry( string name, integer isOnline, string t ){
	if( UpdateCount++ > 0 )
		UpdateBuffer += "&";    // between each pair

	UpdateBuffer += NameValuePair( "u", name + "," + (string)isOnline + "," + t );
}

AppendUpdateEntry( string name, integer isOnline, string t1, string t2 ){
	AppendEntry( name, 1 - isOnline, t1 );
	AppendEntry( name, isOnline, t2 );
}

UpdateOnlineStatus( key qid, integer isOnline ){
	if( qid == QueryId ){
		string name = CurrentString( Names );
		integer wasOnline = CurrentInt( Online );
		string curTime = llGetTimestamp();

		Trace( "Update: " + name + ": " + (string)wasOnline + " -> " + (string)isOnline );
		
		if( isOnline != wasOnline ){
			string prevTime = CurrentString( Times );
			AppendUpdateEntry( name, isOnline, prevTime, curTime );
			Online = ReplaceCurrent( Online, [ isOnline ]);
		}

		Times = ReplaceCurrent( Times, [ curTime ]);

	} else
		Say( "Unexpected query ID: " + (string)qid );

	QueueNextOnlineRequests();
}

// HTTP requests //////////////////////////////////////////////////////

key http_request_id;

string AddMemoryUpdate(){
    return "&" + NameValuePair( "memory", (string)llGetFreeMemory())
        + "&" + NameValuePair( "time", llGetTimestamp());
}

SubmitHttpPost( string why, string url, string body ){
    Trace( "SubmitHttpPost." + why + ": " + url );
    Trace2( "SubmitHttpPost: " + body );

    if( TESTING )
		return;

	http_request_id
		= llHTTPRequest(
			url,
			[ HTTP_METHOD, "POST",
				HTTP_MIMETYPE, "application/x-www-form-urlencoded" ],
			body );
}

SubmitMonitorRequest( integer skip ){
	string body;
	if( skip > 0 )
		body = "skip=" + (string)skip;
	else
		body = "";

    SubmitHttpPost( "MonitorRequest", MONITOR_URL, body );
}

SubmitUpdate(){
	if( UpdateCount > 0 ){
		Trace( "Submitting Update: " + (string)UpdateCount );
		UpdateBuffer += AddMemoryUpdate();
		SubmitHttpPost( "SubmitUpdate", UPDATE_URL, UpdateBuffer );
	} else
		Trace( "No changes => no Submission" );
}

NotifyEvent( string message ){
    string body
		= NameValuePair( "event", message )
			+ "&"
			+ NameValuePair( "time", llGetTimestamp());

    SubmitHttpPost( "NotifyEvent", UPDATE_URL, body );
}

integer ProcessHttpResponse(key id, integer status, list meta, string body){
	if ( id != http_request_id ){
		Say( "Spurious http response: " + (string)id );
		return 0;
	}

	if( status == 200 ){
		Trace( "http response OK" );
		return 1;
	} else {
		Say( "http response bad: " + (string)status );
		return 0;
	}
}

// default/startup/ReadConfig state ///////////////////////////////////////

default {
	state_entry(){
		Say( "Initial Free Memory: " + (string)llGetFreeMemory());
		SetText( "[wait]", RED_COLOR );

		NotifyEvent(
			"Restarting "
			+ llGetObjectName()
			+ " "
			+ llGetScriptName());
	}
	
    http_response(key id, integer status, list meta, string body){
		ProcessHttpResponse(id, status, meta, body);
		state ReadConfig;
    }

    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }

    on_rez( integer param ){
        llResetScript();
    }
}

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

                else if( "REPEAT_INTERVAL" == setting )
                    REPEAT_INTERVAL = (integer)value;

                else if( "MASTER_UPDATE_INTERVAL" == setting )
                    MASTER_UPDATE_INTERVAL = (integer)value;

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
        Trace( "Name Count: " + (string)NAME_COUNT );
		ResetOnlineStatus();
    }

    http_response(key id, integer status, list meta, string body){
        integer count = NAME_COUNT;

		if( ProcessHttpResponse( id, status, meta, body )){
            AddNamesAndKeys( body );
            if( count == NAME_COUNT )	// if none added
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
        Say( "Running Free Memory: " + (string)llGetFreeMemory());

        QueueFirstOnlineRequests();

        llSetTimerEvent( REPEAT_INTERVAL );
    }

    timer(){
		UpdateMasterInterval();
	        QueueFirstOnlineRequests();
    }

    dataserver(key queryid, string data){
        UpdateOnlineStatus( queryid, (integer)data );
    }

    http_response(key id, integer status, list meta, string body){
        ProcessHttpResponse(id, status, meta, body);
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

string    VERSION = "3.0";

integer TRACE = 2;

integer	CMD_OFFLINE = 0;			// same as online status code
integer	CMD_ONLINE = 1;			// same as online status code
integer	CMD_RESET_BUFFER = 2;
integer	CMD_SEND_BUFFER = 3;
integer	CMD_SET_TRACE = 4;

string    UPDATE_URL = "http://cascade-sys.com/cgi-bin/avatar.cgi";

// two levels of text output to owner

Say( string msg ){
    llOwnerSay( msg );
}

Trace( string msg ){
    if( TRACE )
        Say( "{" + (string)llGetFreeMemory() + "} " + msg );
}

Trace2( string msg ){
    if( TRACE > 1 )
        Say( msg );
}

// for querying and recording status ///////////////////////////////////

integer UpdateCount;    // number of entries = 2X actual number of changes
string UpdateBuffer;    // update buffer, incrementally constructed

// formatting update buffer

ResetUpdateBuffer()
{
	UpdateCount = 0;
	UpdateBuffer = "";
}

string NameValuePair( string name, string value ){
    return llEscapeURL( name ) + "=" + llEscapeURL( value );
}

AppendEntry( string name, integer isOnline, string t ){
    if( UpdateCount++ > 0 )
        UpdateBuffer += "&";    // between each pair

    UpdateBuffer += NameValuePair( "u", name + "," + (string)isOnline + "," + t );
}

//~ AppendBufferPair( string name, integer isOnline, string t1t2 )
//~ {
//~ 	list times = llCSV2List( t1t2 );
//~ 	integer N = llGetListLength( times );

//~ 	if( N != 2 ){
//~ 		Say( "Update Buffer: wrong number of times: " + (string)N );
//~ 		return;
//~ 	}

//~ 	AppendEntry( name, 1 - isOnline, llList2String( times, 0 ));
//~ 	AppendEntry( name, isOnline, llList2String( times, 1 ));
//~ }

// HTTP requests //////////////////////////////////////////////////////

key http_request_id;

SubmitHttpPost( string why, string url, string body ){
    Trace( "SubmitHttpPost." + why + ": " + url );
    Trace2( "SubmitHttpPost: " + body );

    http_request_id
        = llHTTPRequest(
            url,
            [ HTTP_METHOD, "POST",
                HTTP_MIMETYPE, "application/x-www-form-urlencoded" ],
            body );
}

SubmitUpdate(){
	Trace( "Submitting Update: " + (string)UpdateCount );
	SubmitHttpPost( "SubmitUpdate", UPDATE_URL, UpdateBuffer );
	ResetUpdateBuffer();
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

// Process link messages ////////////////////////////////////////////

ProcessLinkMessage( integer code, string str, key id ){
	Trace( "ProcessLinkMessage: " + (string)code + " " + str + " " + (string)id );
	
	if( code == CMD_OFFLINE || code == CMD_ONLINE )
		AppendEntry( str, code, (string)id  );

	else if( code == CMD_RESET_BUFFER )
		ResetUpdateBuffer();

	else if( code == CMD_SEND_BUFFER )
		SubmitUpdate();

	else if( code == CMD_SET_TRACE )
		TRACE = (integer)str;

	else
		Say( "Unrecognized command code: " + (string)code );
}

// default/startup/ReadConfig state ///////////////////////////////////////

default {
    state_entry(){
		ResetUpdateBuffer();

        NotifyEvent(
            "Restarting "
            + llGetObjectName()
            + " "
            + llGetScriptName());

        Say( "Running Free Memory: " + (string)llGetFreeMemory());
    }

	link_message( integer sender, integer code, string str, key id ){
		ProcessLinkMessage( code, str, id );
	}

    http_response(key id, integer status, list meta, string body){
        ProcessHttpResponse(id, status, meta, body);
    }

    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }

    on_rez( integer param ){
        llResetScript();
    }
}

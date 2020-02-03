// MonitorAv-B -- accumulate and send update HTTP

string    VERSION = "3.1";

integer TRACE = 0;

integer    CMD_OFFLINE = 0;            // same as online status code
integer    CMD_ONLINE = 1;            // same as online status code
integer    CMD_SEND_BUFFER = 2;
integer    CMD_RESET_BUFFER = 3;
integer    CMD_INIT = 4;

string    UPDATE_URL = "http://cascade-sys.com/cgi-bin/avatar.cgi";

// two levels of text output to owner

Say( string msg ){
    llOwnerSay(  "B: " + msg );
}

Trace( string msg ){
    if( TRACE )
        Say( msg );
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


// HTTP requests //////////////////////////////////////////////////////

key http_request_id;

SubmitHttpPost( string why, string url, string body ){
    http_request_id
        = llHTTPRequest(
            url,
            [ HTTP_METHOD, "POST",
                HTTP_MIMETYPE, "application/x-www-form-urlencoded" ],
            body );
            
    Trace2( "SubmitHttpPost-B." + why + ": " + url );
    Trace2( "SubmitHttpPost-B.id:" + (string)http_request_id );
    Trace2( "SubmitHttpPost-B: " + body );
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
        Say( "Spurious http response-B: " + (string)id );
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

// Process link messages ////////////////////////////////////////////

integer ProcessLinkMessage( integer code, string str, key id ){
    if( id != NULL_KEY )
        Trace2( "ProcessLinkMessage: " + (string)code + ", '" + str + "', " + (string)id );
    else
        Trace2( "ProcessLinkMessage: " + (string)code + ", '" + str + "'" );
    
    if( code == CMD_OFFLINE || code == CMD_ONLINE )
        AppendEntry( str, code, (string)id  );

    else if( code == CMD_INIT ){
        TRACE = TRACE | (integer)str;      // can only raise hard-wired setting
        return 1;   // was INIT

    } else if( code == CMD_RESET_BUFFER )
        ResetUpdateBuffer();

    else if( code == CMD_SEND_BUFFER )
        SubmitUpdate();

    else
        Say( "Unrecognized command code: " + (string)code );
        
    return 0;   // was NOT INIT
}

// default/startup state ///////////////////////////////////////

default {
    state_entry(){
        Say( "Running Free Memory: " + (string)llGetFreeMemory());
    }

    link_message( integer sender, integer code, string str, key id ){
        if( ProcessLinkMessage( code, str, id ))
            state Running;
    }

    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }

    on_rez( integer param ){
        llResetScript();
    }
}

// Running state ///////////////////////////////////////

state Running {
    state_entry(){
        ResetUpdateBuffer();

        Say( "B-Running Free Memory: " + (string)llGetFreeMemory());
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


integer TRACE = 1;

string URL   = "http://w-hat.com/name2key"; // name2key url

string sender;
string recipient;
string message;

integer reqid;

Say( string message )
{
    llOwnerSay( message );
}

Trace( string message )
{
    if( TRACE )
        Say( message );
}

Reply( string message )
{
    Trace( message );
    llEmail( sender, "Re: IM Relay to: " + recipient, message );
}

default 
{
    state_entry() 
    {
        Trace( "Ready for next request" );
    }
    
    link_message(integer sender_num, integer num, string str, key id)
    {
        if( num == 1 )
            sender = str;
        else if( num == 2 )
            recipient = str;
        else if( num == 3 ){
            message = str;
            state LookupKey;
        }
    }
}

state LookupKey
{
    state_entry() 
    {
        Trace( "Requesting key for " + recipient );
        
        reqid = llHTTPRequest( URL 
                        + "?terse=1&name=" 
                        + llEscapeURL( recipient ), [], "" );
    }

    http_response(key id, integer status, list meta, string body) 
    {
        if ( id != reqid ){
            Say( "Ignoring spurious http_response" );
            return;
        }
        
        if ( status == 200 ){
            if( (key)body == NULL_KEY ){
                Reply( "No Key found" );
                
            } else {
                llInstantMessage( (key)body, message );
                Reply( "IM Sent @" 
                    + llGetTimestamp()
                    + " to " + recipient 
                    + " (" + body + ")" );
            }
        } else if( status == 499 ){
            Reply( "Key request timed-out" );
            
        } else
            Reply( "Error requesting key, status = " + (string)status );
        
        state default;
    }
}

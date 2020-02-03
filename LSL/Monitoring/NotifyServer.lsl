NotifyServer( string action, string name )
{
    string url 
		=  "http://cascade-sys.com/cgi-bin/visitor.cgi"
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


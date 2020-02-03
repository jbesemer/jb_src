default {
    state_entry() 
    {
        # llEmail((string)llGetKey() + "@lsl.secondlife.com", "Test!", "This is a test message."); // Send email to self.
        
        llSetTimerEvent( 10 );
    }
    
    timer() 
    {
        llGetNextEmail( "", "" ); // Check for email with any sender address and subject.
    }
    
    email( string time, string address, string subject, string message, integer num_left ) 
    {
        string body = llDeleteSubString( message, 0, llSubStringIndex( message, "\n\n" ) + 1 );

        // queue the request via linked messages
        
        llMessageLinked( LINK_THIS, 1, address, NULL_KEY );
        llMessageLinked( LINK_THIS, 2, subject, NULL_KEY );
        llMessageLinked( LINK_THIS, 3, message, NULL_KEY );
        
        if( num_left > 0 ) 
            llGetNextEmail( "", "" ); // Check for email with any sender address and subject.
    }
}
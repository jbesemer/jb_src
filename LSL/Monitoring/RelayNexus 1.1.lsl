string VERSION = "1.1";

integer RELAY_CHAN = -50012;

float GRACE_PERIOD = 5.0;   // number of sec. to wait before arming system

string RELAY_OWNER_HERE = "here";
string RELAY_OWNER_GONE = "gone";

integer SECURITY_CHAN = 15;
integer DOOR_CHAN1 = 5010;
integer DOOR_CHAN2 = 5020;
integer DOOR_CHAN3 = 5030;

integer BLINDS_CHAN1 = 75;
integer BLINDS_CHAN2 = 76;

integer TP_CHAN1 = 90901;
integer TP_CHAN2 = 90902;

integer BUGS_CHAN = 909;
string BUGS_ON = "start";
string BUGS_OFF = "stop";

integer BALLS_CHAN1 = 1;
integer BALLS_CHAN2 = 7;
string  BALLS_SHOW = "show";
string  BALLS_HIDE = "hide";

set_secure(){
//  llRegionSay( DOOR_CHAN1, "lock" );
//  llRegionSay( DOOR_CHAN2, "lock" );
//  llRegionSay( DOOR_CHAN3, "lock" );
    
    llRegionSay( TP_CHAN2, "lock" );
    llRegionSay( BUGS_CHAN, BUGS_OFF );
    
//  llRegionSay( SECURITY_CHAN, "on" );
//  llRegionSay( BLINDS_CHAN1, "close" );
//  llRegionSay( BLINDS_CHAN2, "close" );
    
    llSay( BALLS_CHAN1, BALLS_HIDE );
    llSay( BALLS_CHAN2, BALLS_HIDE );

    llOwnerSay( "System Armed" );
}

stand_down(){
//  llRegionSay( DOOR_CHAN1, "unlock" );
//  llRegionSay( DOOR_CHAN2, "unlock" );
//  llRegionSay( DOOR_CHAN3, "unlock" );
//  llRegionSay( BLINDS_CHAN2, "open" );
            
    llRegionSay( TP_CHAN2, "unlock" );
    llRegionSay( BUGS_CHAN, BUGS_ON );

//  llRegionSay( BLINDS_CHAN2, "open" );

    llSay( BALLS_CHAN1, BALLS_SHOW );
    llSay( BALLS_CHAN2, BALLS_SHOW );

    llOwnerSay( "Standing Down" );
}


default
{
    state_entry()
    {
        llOwnerSay( "RelayNexus " + VERSION );
        llListen( RELAY_CHAN, "", NULL_KEY, "" );
    }

    touch_start(integer total_number){
//    llSay(0, "Touched.");
    }

   listen( integer chan, string name, key id, string message ){
        if( chan == RELAY_CHAN ){
            if( message == RELAY_OWNER_HERE ){
                llSetTimerEvent( 0 );
                stand_down();
                
            } else if( message == RELAY_OWNER_GONE ){
                llSetTimerEvent( GRACE_PERIOD );

            } else
                llOwnerSay( "Ignoring: " + message );
        }
    }
    
    timer(){
        llSetTimerEvent( 0 );
        set_secure();
    }
}

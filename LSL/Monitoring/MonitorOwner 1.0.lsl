string VERSION = "1.0";

list RELAY_CHANS = [ -50011, -50012, -50013 ];
list ZONE_BITS = [ 1, 2, 4 ];

float GRACE_PERIOD = 4.0;

integer ZoneBits = 0;

string RELAY_OWNER_HERE = "here";
string RELAY_OWNER_GONE = "gone";

integer RADIO_CHAN      = 2112;            // channel radio listens for commands

string RADIO_SUSPEND_CMD   = "suspend";
string RADIO_RESUME_CMD   = "resume";

integer Secured;

set_secure(){
	Secured = 1;
    llOwnerSay( "System Armed" );

	// actions when owner leaves

	llRegionSay( RADIO_CHAN, RADIO_RESUME_CMD );
}

stand_down(){
	if( Secured ){
		Secured = 0;
		llOwnerSay( "Standing Down" );
	}
}

integer OWNER_INDETERMINATE = 0;		// no change
integer OWNER_ARRIVAL = 1;
integer OWNER_DEPARTURE = 2;

integer UpdateZoneBits( integer chan, string message ){
   integer N = llListFindList( RELAY_CHANS, [ chan ]);

   if( N >= 0 ){
	   integer bit = llList2Integer( ZONE_BITS, N );
	   integer prevZoneBits = ZoneBits;

	   if( message == RELAY_OWNER_HERE ){
		   ZoneBits = ZoneBits | bit;

		} else if( message == RELAY_OWNER_GONE ){
		   ZoneBits = ZoneBits & ~bit;

		} else
			llOwnerSay( "Ignoring spurious message: " + message );

		if( !!ZoneBits != !!prevZoneBits )
			if( ZoneBits != 0 )
				return OWNER_ARRIVAL;
			else
				return OWNER_DEPARTURE;

	} else
		llOwnerSay( "Ignoring noise on spurious channel: " + (string)chan );

	return OWNER_INDETERMINATE;
}

ListenAllChannels(){
	integer N = llGetListLength( RELAY_CHANS );
	integer i;

	for( i=0; i < N; i++ )
		llListen( llList2Integer( RELAY_CHANS, i ), "", NULL_KEY, "" );
}

// default/initial -- UNKNOWN state //////////////////////////////////////

default {
    state_entry() {
        llOwnerSay( "Version: " + VERSION );
		ListenAllChannels();
    }

	// we don't know what state we're in until we see our first message

	listen( integer chan, string name, key id, string message ){
		integer action = UpdateZoneBits( chan, message );

		if( action == OWNER_ARRIVAL )
			state Disarmed;

		else if( action == OWNER_DEPARTURE )
			state Preparing;
	}
}

state Preparing {
    state_entry() {
		llSetTimerEvent( GRACE_PERIOD );
		ListenAllChannels();
    }

	state_exit(){
		llSetTimerEvent( 0 );
	}

	timer(){
		state Armed;
	}

	listen( integer chan, string name, key id, string message ){
		if( OWNER_ARRIVAL == UpdateZoneBits( chan, message ))
			state Disarmed;
	}
}

state Armed {
    state_entry() {
		set_secure();
		ListenAllChannels();
    }

	listen( integer chan, string name, key id, string message ){
		if( OWNER_ARRIVAL == UpdateZoneBits( chan, message ))
			state Disarmed;
	}
}

state Disarmed {
    state_entry() {
		stand_down();
		ListenAllChannels();
    }

	listen( integer chan, string name, key id, string message ){
		if( OWNER_DEPARTURE == UpdateZoneBits( chan, message ))
			state Preparing;
	}
}


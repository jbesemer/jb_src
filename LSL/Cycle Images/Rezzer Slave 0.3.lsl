string VERSION = "0.2";

integer TRACE = 0;

integer CHAN;    // channel on which to tell rezzed objects to die

string CMD_DIE = "die";
string CMD_ROT = "rotate";

Say( string msg ){
    llOwnerSay( msg );
}

Trace( string msg ){
    if( TRACE )
        Say( msg );
}


default
{
    on_rez(integer param)
    {
        Trace("rezzed with the number " + (string)param);
        CHAN = param & ~1;  // even channels only
        TRACE = param & 1;  // odd chans => trace on

        if( CHAN != 0 ){
            Trace( "Listening on " + (string)CHAN );
            llListen( CHAN, "", NULL_KEY, "" );
        } else
            Say( "Not Listening on any channel" );
    }

    state_entry(){
    }

    listen( integer channel, string name, key id, string message ){
        Trace( "Message: " + message );

		list params = llCSV2List( message );
		string cmd = llList2String( params, 0 );
		integer N = llGetListLength( params );

        if( cmd == CMD_DIE )
            llDie();

		else if( cmd == CMD_ROT ){
			if( N <= 1 ){
				llTargetOmega( ZERO_VECTOR, 0, 0); 	// turn off rotation
				return;
			}

			vector axis;
			float rate;

			if( N > 1 ){
				axis = (vector)llList2String( params, 1 );
				if( N > 2 )
					rate = (float)llList2String( params, 2 );
			}

			llTargetOmega( axis, TWO_PI*rate, 1.0 );
		}
        else
            Say( "Ignoring spurrious message: " + message );
    }
}

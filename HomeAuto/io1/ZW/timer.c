

// some convenient forms for 48 bit counters

typedef struct {
	int	hi;
	unsigned long lo;
} time_hi_lo;

typedef union {
	time_hi_lo	hilo;
	byte		data[ 6 ];
} time_type;

// timeclocks

void ClockReset( time_type* t )
{
	memset( (void*)t, 0, sizeof( t ));
}

void ClockIn( time_type* t )
{
	time_type t0;

	gettimer( (int*) &t0 );

	sub66( (void*) &t, (void*) &t0 );
}

void ClockOut( time_type* t )
{
	time_type t0;

	gettimer( (int*) &t0 );

	add66( (void*) &t, (void*) &t0 );
}


time_type testClock1, testClock2;

void TimerTest1()
{
	byte b;

	send( "# timer test\n" );
	
	subcode = c2b( args[ 1 ]);
	ClockReset( &testClock1 );
	ClockReset( &testClock2 );
	
	ClockIn( &testClock1 );
	for( b=0; b < subcode; b++  ){
		for( w = 0; w < 100; w++ ){
			ClockIn( &testClock2 );
			ClockOut( &testClock2 );
		}
	}
	ClockOut( &testClock1 );

	send( "# test1 " );
	sendch( args[ 1 ]);
	sendch( '=' );
	sendHex( (byte*) &testClock1, 6 );
	sendHex( (byte*) &testClock2, 6 );
	sendnl();

}

void TimerTest2()
{
		gettimer( (int*) &testClock1 );
		send( "# test4 " );
		sendHex( (byte*) &testClock1, 6 );
		sendnl();
}


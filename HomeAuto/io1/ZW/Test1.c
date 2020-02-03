
#use VDRIVER.LIB
#use RTK.LIB
// #use eziobl17.lib
// #use eziopbdv.lib
// #use ezioplc2.lib
#use STDIO.LIB

// #use aasc.lib
// #use aascscc.lib
// #use aascz1.lib


// item states

typedef struct {
	int	next;
	int	prev;
} State;

// functions on state

typedef int tabfun( State*, int, int );

// function args

typedef struct {
	tabfun*	fun;
	int		addr;
} FunArg;

// a meta function, called by more specialized function
// and possibly calling caller back in return.

xmem int metafun( tabfun* fun, State* s, int addr, int arg )
{
	printf( "metafun( %d )\n", arg );

	if( arg > 0 ){
		fun( s, addr, arg - 1 );
	}
	printf( "meta returns\n" );
}

// an example specialized function

int tabfun1( State* s, int addr, int arg )
{
	printf( "tabfun1( %d )\n", arg );

	if( arg > 0 ){
		metafun( tabfun1, s, addr, arg );
	}
	printf( "fun returns\n" );
}

// a table of funargs (constant)

FunArg tab[] = {
	tabfun1,	40,	
};

#define TABSIZE ( sizeof( tab ) / sizeof( tab[ 0 ]))

// a parallel table of states (variable)

State state[ TABSIZE ];

int apply( int index, int arg )
{
	return (*tab[ index ].fun)( &state[ index ], tab[ index ].addr, arg );
}


// a background task which interacts with the above

background()
{
	printf( "before:\n" );
	apply( 0, 40 );
	printf( "after\n\n" );
}

// other, higher priority tasks

clicker()
{
}

blinker()
{
}

idle()
{
}


// setup RTK

#define RUNKERNEL 1

int (*Ftask[])() = { blinker, clicker, background };

int TaskFreq[] =   {      1,    40 };

#define NTASKS ( sizeof( Ftask ) / sizeof( *Ftask ))

main()
{
	int i;

	// initialization

	VdInit();

//	eioResetPlcBus();
//	eioPlcRstWait();
	
	for( i=0; i< NTASKS-1; i++ )
		run_every( i, TaskFreq[ i ]);

	(*Ftask[ NTASKS - 1 ])();
}

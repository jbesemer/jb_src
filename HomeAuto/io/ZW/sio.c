///////////////////////////////////////
// TODO List
//
//	ADC: cal, test 
//
//	serial: 
//
//		chan0? 
//		seems to crash sometimes -- why?
//		flow control on serial
//
//	Event commands
//	
//	restart command, reset states, watchdog
//	


///////////////////////////////////////
// NOTES
//
// Herein, I/O devices are organized into "banks".  A bank
// consists of up to 16 individual I/O "pins".  Thus each
// individual I/O is addressable via a (bank,pin) pair.
//
// In many cases, individual I/O cards include a pair of
// I/O banks.  During initialization, each unique (card, bank) 
// pair is associated with a unique external Bank ID.
//
// Some banks are "digital" in that the state of each pin
// is 0 or 1.  Other banks are analog in that the state
// of each pin may be as many as 16 bits.
//
// Digital banks may be addressed in their entirety.  
// A single up to 16 bit number represents the state 
// of all pins.  Little-endian bit 0 is pin 0, etc.
// 


///////////////////////////////////////
// configuration control

#define XMEM	xmem
#define USEIX	useix

#define AUTO_DEF_EVENTS 1	// init defines events per config tab


///////////////////////////////////////
// imports 

#use VDRIVER.LIB
#use RTK.LIB
#use eziobl17.lib
#use eziopbdv.lib
#use ezioplc2.lib
#use STDIO.LIB

#use bitswiz.lib
#use SioSend.lib
#use events.lib

///////////////////////////////////////
// fundamental defines

// typedef unsigned char byte;
// typedef unsigned int word;

#define TPRINTF1( X ) printf X 
#define TPRINTF( X )

///////////////////////////////////////
// forwards

byte c2b( byte code );
void setMaskBit( word* mask, int pin, int value );
void HandleCmd( byte code, char* args, int len );
XMEM void HandleSerial( byte code, char* buf, int len );
XMEM USEIX void HandleDebug( char* args, byte len );
void PinOut( int pin, int value );
int	LegalBank( int bank );

	/* add more here */


////////////////////////////////////////////////////////////////////
// Commands
////////////////////////////////////////////////////////////////////

// all messages start with a command byte with a unique code,
// followed by 0 or more argument bytes.   Size and format of
// arg lists are uniquely determined by the command code.
// Non empty argument structs are enumerated below.  
//
// Some messages are bi-directional, some are receive only and
// some are send only.  A few messages are internally generated only.

typedef byte CmdCode;

///////////////////////////////////
// all possible function codes,
// some of which may be ignored or err out in a particular device type
//
// Three categories:
//

//	1. IO

#define CMD_GET				0	// @ read an input pin
#define CMD_SET				1	// a set an output pin
#define CMD_GETMASK			2	// b read monitor mask for a pin
#define CMD_SETMASK			3 	// c set monitor mask for a pin
#define CMD_POLL			4	// d read all input pins & report any changes

#define CMD_GET_BANK		5	// e read all input pins
#define CMD_SET_BANK		6	// f set all output pins to a value
#define CMD_GETMASK_BANK	7	// g read all input pins
#define CMD_SETMASK_BANK	8	// h set all output pins to a value

#define CMD_POLL_BANK		9	// i read all input pins on all banks & report any changes
#define CMD_SEND_BANK_RESULT 10	// j send .prev results to host
#define CMD_FETCH_BANK		11	// k read all input pins

#define CMD_CLEAR_BANK		12	// l clear all output pins
#define CMD_PULSE			13	// m pulse an output pin
#define CMD_TOGGLE			14	// n toggle an output pin

//	2. SYS
 
#define CMD_INIT			15	// o return type of hw interface
#define CMD_GET_MODE		16	// p get mode
#define CMD_SET_MODE		17	// q set mode
#define CMD_DEBUG			18	// r debug commands

#define CMD_EVENT_ADD		19	// s add event
#define CMD_EVENT_CHANGE	20	// t change event
#define CMD_EVENT_LIST		21	// u list event
#define CMD_EVENT_REMOVE	22	// v remove event


//	3. Serial and Analog

#define CMD_SEND_0			23	// w send N bytes to channel 0
#define CMD_SEND_1			24	// x send N bytes to channel 1
#define CMD_SEND_B			25	// y send N bytes to channel B
#define CMD_ENABLE			26	// z activate a channel
#define CMD_DISABLE			27	// z deactivate a channel

#define CMD_ADC_MODE		28	// set ADC mode
#define CMD_ADC_CAL			29	// calibrate an analog channel

// 4 Internal

#define ICMD_PINCOUNT		32	// return pin count



	/* add new ones here */


/////////////////////////////////
// command property table

// command/HW types

#define IA	1			// input analog
#define OA	2			// output analog
#define ID	4			// input digital
#define OD	8			// output digital
#define IO  (ID|OD)

#define ALLB 16			// command may be applied to all banks 
						// (further qualified by I/O bits)

	/* add others here */


// property table row definition

typedef struct {
	byte	type;		// type of this command (to match with types of HW)
	byte	quoted;		// this command takes "quoted" arguments
} CmdPropStruct;


// command argument signature is a string of chars, 1 per arg
// incoming args are unpacked per the table into above arg struct.
// 
// 

// command property table


CmdPropStruct 
CmdProps[] = {

	// 1. IO

	{ IO,		0,	},	// CMD_GET
	{ IO,		0,	},	// CMD_SET
	{ IO,		0,	},	// CMD_GETMASK
	{ IO,		0,	},	// CMD_SETMASK
	{ ID,		0,	},	// CMD_POLL

	{ IO|ALLB,	0,	}, 	// GET_BANK
	{ OD|ALLB,	0,	},	// CMD_SET_BANK
	{ IO,		0,	},	// CMD_GETMASK_BANK
	{ IO,		0,	},	// CMD_SETMASK_BANK

	{ ID|ALLB,	0,	}, 	// POLL_BANK
	{ IO|ALLB,	0,	},	// CMD_SEND_BANK_RESULT
	{ ID|ALLB,	0,	},	// CMD_FETCH_BANK		

	{ OD|ALLB,	0,	},	// CLEAR_BANK
	{ OD,		0,	},	// CMD_PULSE
	{ IO,		0,	},	// CMD_TOGGLE

	// 2. System

	{ IO,       0,	},	// CMD_INIT
	{ IO,       0,	},	// CMD_GET_MODE
	{ IO,       0,	},	// CMD_SET_MODE
	{ IO,		0,	},	// CMD_DEBUG

	{ IO,		1,	},	// CMD_EVENT_ADD
	{ IO,		1,	},	// CMD_EVENT_CHANGE
	{ IO,		1,	},	// CMD_EVENT_LIST
	{ IO,		1,	},	// CMD_EVENT_REMOVE

	// 3. Serial and analog

	{ IO,		1,	},	// CMD_SEND_0
	{ IO,		1,	},	// CMD_SEND_1
	{ IO,		1,	},	// CMD_SEND_B
	{ IO,		0,	},	// CMD_ENABLE
	{ IO,		0,	},	// CMD_DISABLE

	{ IO,		0,	},	// CMD_ADC_MODE
	{ IO,		0,	},	// CMD_ADC_CAL

	/* add new ones here */
};


#define ALL_BANKS 0xFF		// internal code for all banks (else specific 1)

#define ALL_BANKABLE( CMD ) ( CmdProps[ CMD ].type & ALLB )

#define MAX_COMMANDS ( sizeof( CmdProps ) / sizeof( CmdPropStruct ))

#define LEGAL_CMD( cmd )  ( 0 <= cmd && cmd < sizeof( CmdProps ) / sizeof( CmdPropStruct ))

// in some cases, newlines are quoted

#define QUOTE	0x80

///////////////////////////////////
// system mode settings
//

#define MODE_POLLING	0	// polling mode bits
#define MODE_POLL_LOOP	1	// poll via loop
#define MODE_POLL_EVT	2	// poll via events

#define MODE_EVENTS		1	// process events (binary)

#define MODE_SERIAL_IN	2	// enable aux serial ports if > 0

#define MODE_OSCOPE		3	// enable oscilliscope signals

#define MAX_MODE 4

int Mode[ MAX_MODE ];


////////////////////////////////////////////////
// parsing
////////////////////////////////////////////////

// char translated to number (a=1, ...)

XMEM byte
c2b( char code )
{
	if( code == '@' || code == '`' )
		code = 0;
	
	else if( code == '*' )
		code = 0xFF;

	else if( isdigit( code ))
		code -= '0';
	
	else if( isupper( code ) || ( 'Z' < code && code < 'a' ))
		code -= 'A' - 1;

	else if( islower( code ) || 'z' < code )
		code -= 'a' - 1;

	return code;
}

// 8-bit ascii char

XMEM int 
FetchChar( char** args, int* len, int* pch )
{
//	printf( "fetchChar %s, %d\n", *args, *len );

	if((*len)-- <= 0 ){
		sendError( ERR_MISSING_ARG, 0 );
		return 1;
	}

	*pch = *(*args)++;

	return 0;
}

// single byte char converted to a number

XMEM int 
FetchNum( char** args, int* len, int* pnum )
{
//	printf( "FetchNum %s, %d\n", *args, *len );

	if((*len)-- <= 0 ){
		sendError( ERR_MISSING_ARG, 1 );
		return 1;
	}

	*pnum = c2b( *(*args)++ );

	return 0;
}

XMEM void
SkipToComma( char** args, int* len )
{
	while( (*len) > 0 ){
		if( *(*args) == ',' )
			break;
		(*len)--;
		(*args)++;
	}
}


// decimal integer prefixed by a ','

XMEM int
FetchInt( char** args, int* len, int* pnum )
{
//	printf( "FetchInt %s, %d\n", *args, *len );
	
	if((*len)-- <= 0 || *(*args)++ != ',' ){
		sendError( ERR_MISSING_ARG, 2 );
		return 1;
	}

	*pnum = atoi( *args );

	SkipToComma( args, len );

	return 0;
}

// floating number prefixed by a ','

XMEM int
FetchFloat( char** args, int* len, float* pnum )
{
	if((*len)-- <= 0 || *(*args)++ != ',' ){
		sendError( ERR_MISSING_ARG, 3 );
		return 1;
	}

	*pnum = atof( *args );

	SkipToComma( args, len );

	return 0;
}


XMEM int
FetchBank( char** args, int* len, int* pbank )
{
	int code;

	if( FetchChar( args, len, pbank ))
		return 1;

	code = *pbank;

	if( code == '*' )
		*pbank = 0xFF;

	else if( isdigit( code ))
		*pbank -= '0';
	
	else if( isupper( code ))
		*pbank -= 'A';

	else if( islower( code ))
		*pbank -= 'a';
	else
		return 1;

	return !LegalBank( *pbank );
}

XMEM int
FetchPinVal( char** args, int* len, int* ppin, int* pval )
{
	return FetchNum( args, len, ppin ) 
		|| FetchNum( args, len, pval );
}


// 16 bit value from 1-4 letters

XMEM byte 
FetchWord( char** args, int* len, word* pword )
{
	register word mask;
	register int b, count;

//	printf( "fetchMask %s, %d\n", *args, *len );

	count = *len;

	if( count <= 0 ){
		sendError( ERR_MISSING_ARG, 4 );
		return 1;
	}

	if( count > 4 )
		count = 4;	// 4 max

	*len -= count;

	mask = 0;
	while( count-- > 0 ){
		b = c2b( *(*args)++ );
		mask <<= 4;
		mask |= b;
	}

	*pword = mask;

//	printf( "maskFetched: %d r%d\n", mask, *len );

	return 0;
}


////////////////////////////////////////////////////
// Actions -- core functions triggered by commands
////////////////////////////////////////////////////

// instance-specific struct (created at init time from Config Tab)

typedef struct {
	char	id;		// ID of this group
	byte	change;	// true iff state has changed since last refresh
	byte	board;	// board ID
	byte	bank;	// bank in board (should be a way to fold this into .addr)
	word	addr;	// addr bits for internal use by instance based on config
	
	word	mask;	// mask of trace bits for inputs
	word	prev;	// previously announced state of bank
	word	next;	// most recent state of bank
} IO_OpsStruct;

IO_OpsStruct *IO_OpsTabBase;

// each type of HW defines 1 function of this form

typedef int IO_Fn( 
				CmdCode code, 
				IO_OpsStruct* state, 
				char* args, 
				int len );

// structure for each bank's config data (used to init and build Ops tab)

typedef struct {
	IO_Fn*		fn;			// specific function
	byte		type;		// board type (I or O)
	byte		board;		// board ID
	byte		bank;		// bank in board
	byte		phase;		// initial polling count
	byte		period;		// polling period (0 => none)
} IO_ConfigStruct;

#define A 0	// bank A
#define B 1	// bank B

// glaring HW inconsistency:

#define BANKOFF17XX( AB ) (( AB == A ) ? 16 : 0 )	// A bank is shifted
#define BANKOFF81XX( AB ) (( AB == B ) ? 16 : 0 )	// B bank is shifted (as one would expect)

#define OFFBANK17XX( BANK ) (( BANK ) ? A : B )		

// 1700 Digital I/O Port addresses

#define IO1700_PORTA0	0x4043
#define IO1700_PORTA1	0x4042
#define IO1700_PORTB0	0x4040
#define IO1700_PORTB1	0x4041

word IO1700_PortAddrs[ 2 ][ 2 ] = {		// [ bank ][ byte ]
	{ IO1700_PORTA0, IO1700_PORTA1},
	{ IO1700_PORTB0, IO1700_PORTB1}
};


#define XP81_PINCOUNT	16
#define XP83_PINCOUNT	6
#define XP84_PINCOUNT	8
#define BL17_PINCOUNT	16
#define AD17_PINCOUNT	10


// commands: a-z
// banks, pins: A-Z
// values: 0, 1, ...


///////////////////////////////////
// Higher-level functions
//
// Some commands are implemented by a middle layer of generic functions.
// There is a different one for each board type, input, output, digital, 
// analog.
// These functions are like C++ "super classes" in that the more specific 
// functions are called first and these generic routines are called if the
// more specific function doesn't know how to handle a particular command.

// digital output

XMEM int 
IO_DigitalInput( 
	IO_Fn* sub, 
	CmdCode code, 
	IO_OpsStruct* state, 
	char* args,
	int len )
{
	register int res, pin, value;

	TPRINTF(( "sub %x, state %x\n", sub, state ));
	
	switch( code ){
	case CMD_SETMASK:		// set monitor mask for a pin
		if( FetchPinVal( &args, &len, &pin, &value ))
			return 0;

		setMaskBit( &state->mask, pin, value );
		break;
		
	case CMD_GETMASK:		// read monitor mask for a pin
		if( FetchNum( &args, &len, &pin ))
			return 0;

		sendMaskResult( 
			state->id, 
			pin, 
			( state->mask >> pin ) & 1 );
		break;
		
	case CMD_GETMASK_BANK:	// read monitor mask for all pins
		sendMaskBankResult( state->id, state->mask );
		break;

	case CMD_SETMASK_BANK:	// save monitor mask for all pins
		if( FetchWord( &args, &len, &value ))
			return 0;
		state->mask = value;
		break;

	case CMD_POLL_BANK:		// read all input pins & report any changes
		res = sub( CMD_FETCH_BANK, state, NULL, 0 );
		state->next = res;
		res = ((( state->prev ^ state->next ) & state->mask ) != 0 );
		state->change |= res;
#if 0
		printf( "PB: %c %4x %4x %d\n", 
			state->id,
			state->prev,
			state->next,
			res );
#endif
		break;

	case CMD_GET_BANK:		// read all input pins & report them
		res = sub( CMD_FETCH_BANK, state, NULL, 0 );
		state->next = res;
		state->change = 1;
		break;

	case CMD_SEND_BANK_RESULT:
		sendBankResult( state->id, state->prev );
		break;

	default:
		return ERR_ILLEGAL_OP;
	}

	return NO_ERROR;
}

// digital output

XMEM int 
IO_DigitalOutput( 
	IO_Fn* sub, 
	CmdCode code, 
	IO_OpsStruct* state, 
	char* args,
	int len )
{
	auto char bpv[ 4 ];
	register pin, value, ticks, count;

	switch( code ){
	case CMD_SETMASK:		// set monitor mask for a pin
	case CMD_GETMASK:		// read monitor mask for a pin
	case CMD_GETMASK_BANK:	// read monitor mask for all pins
	case CMD_SETMASK_BANK:	// save monitor mask for all pins
		IO_DigitalInput( sub, code, state, args, len );
		break;

	case CMD_CLEAR_BANK:		// clear all output pins
		value = 0;
		goto set_bank;
		
	case CMD_SET_BANK:		// set all output pins to a value
		if( FetchWord( &args, &len, &value ))
			return 0;
set_bank:
		count = (*sub)( ICMD_PINCOUNT, state, NULL, 0 );
		bpv[ 0 ] = pin;
		bpv[ 1 ] = value;
		for( pin = 0; pin < 16; pin++ )
			(*sub)( CMD_SET, state, bpv, 2 );

		// state->prev = mask // redundant w/sub call
		state->change = 1;
		break;

	case CMD_TOGGLE:
		if( FetchNum( &args, &len, &pin ))
			return 0;

		value = !(( state->next >> pin ) & 1 );

		bpv[ 0 ] = pin;
		bpv[ 1 ] = value;

		return sub( CMD_SET, state, bpv, 2 );

	case CMD_PULSE:
		if( FetchPinVal( &args, &len, &pin, &value )
		||	FetchWord( &args, &len, &ticks ))
			return 0;

		bpv[ 0 ] = 'A' + ( state - IO_OpsTabBase );
		bpv[ 1 ] = '@' + pin;

		if( ticks > 0 ){
			bpv[ 2 ] = '0' + !value;
//			printf( "bpv: %d, %d, %d\n", bpv[0], bpv[1], bpv[2]);
			AddEvent( '!', ticks, 0, CMD_SET, bpv, 3 );
//			AddEvent( '!', ticks, 0, CMD_TOGGLE, bpv, 2 );
		}
		
		bpv[ 2 ] = value;
		
		return sub( CMD_SET, state, bpv+1, 2 );

	case CMD_GET:			// read an input pin
		if( FetchNum( &args, &len, &pin ))
			return 0;

		sendResult( 
			state->id, 
			pin, 
			( state->next >> pin ) & 1 );
		break;

	case CMD_GET_BANK:		// read all input pins
		sendBankResult( state->id, state->next );
		break;

	case CMD_SEND_BANK_RESULT:
//		printf( "prev=%x\n", state->prev );
		sendBankResult( state->id, state->prev );
		break;

	case CMD_POLL:			// read all input pins & report any changes

	default:
		return ERR_ILLEGAL_OP;
	}

	return NO_ERROR;
}

void 
CmdSet( IO_OpsStruct* state, int pin, int value )
{
	setMaskBit( &state->next, pin, value );
	state->change |= ((( state->prev ^ state->next ) & state->mask ) != 0 );
}


// analog input

#if 0
int IO_AnalogInput( 
	IO_Fn* sub, 
	CmdCode code, 
	IO_OpsStruct* state, 
	byte pin, 
	byte value )
{
	return ERR_ILLEGAL_OP;
}

// analog output

int IO_AnalogOutput( 
	IO_Fn* sub, 
	CmdCode code, 
	IO_OpsStruct* state, 
	byte pin, 
	byte value )
{
	return ERR_ILLEGAL_OP;
}
#endif


///////////////////////////////////
// hardware-specific functions

// for CMD_INIT only, this global var is used to pass in an uncommon argument

IO_ConfigStruct* configStruct;

// XP8100 output bank

int 
IO_xp8100_O( 
	CmdCode code, 
	IO_OpsStruct* state, 
	char* args, 
	int len )
{
	register pin, value;

	TPRINTF(( "IO_xp8100_O( %d, %d, %s, %d )\n", code, state->addr, args, len ));
	
	switch( code ){
	case CMD_INIT:			// return type of hw interface
		state->addr = configStruct->board*32 + BANKOFF81XX( configStruct->bank );
		break;
		
	case ICMD_PINCOUNT:
		return XP81_PINCOUNT;

	case CMD_SET:			// set an output pin
		if( FetchPinVal( &args, &len, &pin, &value ))
			return 0;

		if( !plcXP81Out( state->addr + Sw2Hw[ pin ], value ))			// 0 => OK
			return ERR_HW_FAIL;

		CmdSet( state, pin, value );
		break;
		
	default:
		return IO_DigitalOutput( IO_xp8100_O, code, state, args, len );
	}

	return NO_ERROR;
}

// XP8100 input bank

int 
IO_xp8100_I( 
	CmdCode code, 
	IO_OpsStruct* state, 
	char* args, 
	int len )
{
	register int addr, base, pin, value;
	register int b1, b0;
	
	TPRINTF(( "IO_xp8100_I %x, state %x\n", IO_xp8100_I, state ));

	switch( code ){
	case CMD_INIT:			// return type of hw interface
		state->addr = configStruct->board * 32 
			+ BANKOFF81XX( configStruct->bank );
		break;
		
	case ICMD_PINCOUNT:
		return XP81_PINCOUNT;

	case CMD_GET:			// read an input pin
		if( FetchNum( &args, &len, &pin ))
			return 0;

		value = !plcXP81In( state->addr + Sw2Hw[ pin ]);
		sendResult( state->id, pin, value );
		setMaskBit( &state->prev, pin, value );
		break;

	case CMD_POLL:
		if( FetchNum( &args, &len, &pin ))
			return 0;

		DI();

		value = !plcXP81In( state->addr + Sw2Hw[ pin ]) & 1;
		
		EI();

		if((( state->prev >> pin ) & 1 ) != value ){
			
			if(( state->mask >> pin ) & 1 )
				sendResult( state->id, pin, value );

			setMaskBit( &state->prev, pin, value );
		}
		break;
		
	case CMD_FETCH_BANK:		// read all input pins
		
		DI();
		
		addr = _eioPlcXP81Addr( state->board );
		eioPlcAdr12( addr );
		base = (( addr >> 8 ) & 0x8 ) + ( state->bank ? 6 : 4 );
		eioPlcAdr4( base );
		b0  = ( _eioReadD1() & 0xF ) << 4;
		b0 |= ( _eioReadD0() & 0xF );
		eioPlcAdr4( base + 1 );
		b1  = ( _eioReadD1() & 0xF ) << 4;
		b1 |= ( _eioReadD0() & 0xF );
		
		EI();

#if 0
		printf( 
			"Fetch1[ %d ]: %3x, %2x, %02x, %02x\n", 
			state - IO_OpsTabBase, 
			addr, 
			base, 
			b0, 
			b1 );
#endif

		return ( HW2SW[ 255 & ( ~b1 )] << 8 ) | HW2SW[ 255 & ( ~b0 )];
		
	// following are handled by generic handler:

	default:
		return IO_DigitalInput( IO_xp8100_I, code, state, args, len );
	}

	return NO_ERROR;
}

// XP8300 heavy duty relay card

int 
IO_xp8300_O( 
	CmdCode code, 
	IO_OpsStruct* state, 
	char* args, 
	int len )
{
	register pin, value;

  	TPRINTF(( "IO_xp8300_O( %d, %d, %s, %d )\n", code, state->addr, args, len ));
	
	switch( code ){
	case CMD_INIT:			// return type of hw interface
		state->addr = configStruct->board * 8;
		break;
		
	case ICMD_PINCOUNT:
		return XP83_PINCOUNT;

	case CMD_SET:			// set an output pin
		if( FetchPinVal( &args, &len, &pin, &value ))
			return 0;

		plcXP83Out( state->addr + pin, value );

		CmdSet( state, pin, value );
		break;
		
	default:
		return IO_DigitalOutput( IO_xp8300_O, code, state, args, len );
	}

	return NO_ERROR;
}

// XP8400 reed relay card

int 
IO_xp8400_O( 
	CmdCode code, 
	IO_OpsStruct* state, 
	char* args, 
	int len  )
{
	register pin, value;

	TPRINTF(( "IO_xp8400_O( %d, %d, %s, %d )\n", code, state->addr, args, len ));

	switch( code ){
	case CMD_INIT:			// return type of hw interface
		state->addr = configStruct->board * 8;
		break;
		
	case ICMD_PINCOUNT:
		return XP84_PINCOUNT;

	case CMD_SET:			// set an output pin
		if( FetchPinVal( &args, &len, &pin, &value ))
			return 0;

		plcXP84Out( state->addr + pin, value );

		CmdSet( state, pin, value );
		break;

	default:
		return IO_DigitalOutput( IO_xp8400_O, code, state, args, len );
	}

	return NO_ERROR;
}

// BL1700 digital input bank

int 
IO_bl1700_I( 
	CmdCode code, 
	IO_OpsStruct* state, 
	char* args, 
	int len )
{
	register int bank, pin, value, b0, b1;
	
	TPRINTF(( "IO_bl1700_I %x, state %x\n", IO_bl1700_I, state ));

	switch( code ){
	case CMD_INIT:			// return type of hw interface
		state->addr = BANKOFF17XX( configStruct->bank );
		state->prev = 0;
		break;
		
	case ICMD_PINCOUNT:
		return BL17_PINCOUNT;

	case CMD_GET:			// read an input pin
		if( FetchNum( &args, &len, &pin ))
			return 0;

		value = !eioBrdDI( state->addr + Sw2Hw[ pin ]);	// => 0 or 1
		sendResult( state->id, pin, value );		// => 0 or 1
		setMaskBit( &state->prev, pin, value );
		break;
		
	case CMD_POLL:
		if( FetchNum( &args, &len, &pin ))
			return 0;

		value = !eioBrdDI( state->addr + Sw2Hw[ pin ]) & 1;
		if((( state->prev >> pin ) & 1 ) != value ){

			if(( state->mask >> pin ) & 1 )
				sendResult( state->id, pin, value );

			setMaskBit( &state->prev, pin, value );
		}
		break;

	case CMD_FETCH_BANK:		// read all input pins
		
//		DI();
		
		bank = OFFBANK17XX( state->addr );
		b0 = inport( IO1700_PortAddrs[ bank ][ 1 ]);
		b1 = inport( IO1700_PortAddrs[ bank ][ 0 ]);
		
//		EI();

#if 0		
		printf( 
			"Fetch2[ %d ]: %3x, %2x, %02x, %02x\n", 
			state - IO_OpsTabBase, 
			state->addr, 
			bank, 
			b0, 
			b1 );
#endif
		return ( HW2SW[ 255 & ( ~b1 )] << 8 ) | HW2SW[ 255 & ( ~b0 )];

	// following are handled by generic handler:

	default:
		return IO_DigitalInput( IO_bl1700_I, code, state, args, len );
	}

	return NO_ERROR;
}

// BL1700 digital output bank

int 
IO_bl1700_O( 
	CmdCode code, 
	IO_OpsStruct* state, 
	char* args, 
	int len )
{
	register int bank, mask, pin, value;
	
	TPRINTF(( "IO_bl1700_O( %d, %d, %s, %d )\n", code, state->addr, args, len ));

	switch( code ){
	case CMD_INIT:			// return type of hw interface
		state->addr = BANKOFF17XX( configStruct->bank );
		break;
		
	case ICMD_PINCOUNT:
		return BL17_PINCOUNT;

	case CMD_CLEAR_BANK:	// clear all output pins
		value = 0;
		goto set_bank;

	case CMD_SET_BANK:		// set all output pins to a value (pin,value is 1 16 bit quantity)
		if( FetchWord( &args, &len, &value ))
			return 0;

set_bank:
		bank = OFFBANK17XX( state->addr );

		outport( 
			IO1700_PortAddrs[ bank ][ 0 ], 
			SW2HW[ value & 0xFF ]);
		outport( 
			IO1700_PortAddrs[ bank ][ 1 ], 
			SW2HW[( value >> 8 ) & 0xFF ]);

		state->prev = value;
		state->change = 1;
		break;
		
	case CMD_SET:			// set an output pin
		if( FetchPinVal( &args, &len, &pin, &value ))
			return NO_ERROR;	// IS error but reported lower down

		if( eioBrdDO( state->addr + Sw2Hw[ pin ], value ) == -1 )
			return ERR_HW_FAIL;

		CmdSet( state, pin, value );
		break;
		
	default:
		return IO_DigitalOutput( IO_bl1700_O, code, state, args, len );
	}

	return NO_ERROR;
}

// BL1700 analog readings & setup

#define AD_CHAN_COUNT AD17_PINCOUNT
#define AD_BANK_COUNT 4

extern struct _eioAdcCalib eioBrdAICalib[EIO_BRD_NUM_ADC];


useix XMEM int 
IO_bl1700_A( 
	CmdCode			code, 
	IO_OpsStruct*	state, 
	char*			args, 
	int				len )
{
	float		ad_float[ AD_CHAN_COUNT ];
	unsigned	ad_unsigned[ AD_CHAN_COUNT ];
	byte		ad_change[ AD_BANK_COUNT ][ AD_CHAN_COUNT ];
	int		d1, d2;
	float		v1, v2;

	register int	pin, bank;
	char			buf[ 30 ];
	auto char		p[ 2 ];
	int				i, j;

	TPRINTF(( "IO_bl1700_A( %d, %d, %d, %d )\n", code, state->addr, pin, value ));

	switch( code ){
	case CMD_INIT:			// return type of hw interface
		eioBrdInit( 0 );	// init ADC
		state->addr = configStruct->bank;
		for( i=0; i < AD_CHAN_COUNT; i++ ){
			ad_float[ i ] = 0.1 * i;
			ad_unsigned[ i ] = i;
			for( j=0; j < AD_BANK_COUNT; j++ ){
				ad_change[ j ][ i ] = 0;
			}
		}
		break;

	case ICMD_PINCOUNT:
		return AD_CHAN_COUNT;

	case CMD_GET:			// read an input pin
		if( FetchNum( &args, &len, &pin ))
			return NO_ERROR;	// IS error but reported lower down

		bank = state->addr;

		if( pin < 0 || pin >= AD_CHAN_COUNT || bank < 0 || bank > 3 )
			return ERR_NONX_PIN;

		switch( bank ){
		case 0:
//			ad_float[ pin ] = eioBrdAI( pin );
			ad_float[ pin ] 
				= (( eioBrdAICalib[ pin ].zeroOffset != 0xFFFF )
					? ( eioBrdAICalib[ pin ].invGain 
						* ((long)eioBrdAICalib[ pin ].zeroOffset
							- (long)_eioBrdAI( pin )))
							: -1.0 );
				break;
		case 1:
//			ad_unsigned[ pin ] = (unsigned)eioBrdAI( pin + 16 );
			ad_unsigned[ pin ] = _eioBrdAI( pin );
		}
		ad_change[ bank ][ pin ] = 1;
		state->change = 1;

		break;

	case CMD_SEND_BANK_RESULT:
		bank = state->addr;
		for( i=0; i < AD_CHAN_COUNT; i++ ){
			if( ad_change[ bank ][ i ]){

				sprintf( 
					buf, 
					"%c%c: ", 
					state->id, 
					aHexNibble( i ));
				send( buf );

				switch( bank ){
				case 0:
					sprintf( buf, "%g\n", ad_float[ i ]);
					break;
				case 1:
					sprintf( buf, "%u\n", ad_unsigned[ i ]);
					break;
				case 2:
					sprintf( buf, "%g\n", eioBrdAICalib[ i ].invGain );
					break;
				case 3:
					sprintf( buf, "%u\n", eioBrdAICalib[ i ].zeroOffset );
					break;
				}

				send( buf );
				
				ad_change[ bank ][ i ] = 0;
			}
		}
		break;

	case CMD_GET_BANK:		// read all input pins
		for( i=0; i < AD_CHAN_COUNT; i++ ){
			p[ 0 ] = 'a' + i;
			p[ 1 ] = 0;
			IO_bl1700_A( CMD_GET, state, p, 1 );
		}
		break;
		
	case CMD_ADC_MODE:		// set ADC mode
		if( state->bank != 0 )
			return ERR_ILLEGAL_OP;

		if( FetchNum( &args, &len, &pin )	// dataLen
		||	FetchNum( &args, &len, &bank )	// dataFormat
		||	FetchNum( &args, &len, &i ))	// polarFormat
			return 0;

		if( eioBrdAdcMode( pin, bank, i ) != 1 )
			return ERR_MISSING_ARG;
		break;

	case CMD_ADC_CAL:		// calibrate a channel
		if( state->bank != 0 )
			return ERR_ILLEGAL_OP;

		if( FetchNum( &args, &len, &pin )
		||	FetchInt( &args, &len, &d1 )
		||	FetchInt( &args, &len, &d2 )
		||	FetchFloat( &args, &len, &v1 )
		||	FetchFloat( &args, &len, &v2 ))
			return 0;

		if( eioBrdACalib( pin, d1, d2, v1, v2 ))
			return ERR_NONX_PIN;
		break;

	case CMD_SET:
		if( FetchNum( &args, &len, &pin ))
			return NO_ERROR;

		// this allows setting the ADC cal parameters TEMPORARILY.
		// at init time the one stored in NVRAM will be used again.

		switch( state->bank ){
		case 0:
		case 1:
			return ERR_ILLEGAL_OP;

		case 2:
			if( FetchFloat( &args, &len, &v1 ))
				return NO_ERROR;
			eioBrdAICalib[ pin ].invGain = v1;
			break;

		case 3:
			if( FetchInt( &args, &len, &d1 ))
				return NO_ERROR;
			eioBrdAICalib[ pin ].zeroOffset = d1;
			break;
		}

		break;

	case CMD_POLL_BANK:		// read all input pins & report any changes
	case CMD_SETMASK:		// set monitor mask for a pin
	case CMD_GETMASK:		// read monitor mask for a pin

	default:
		return ERR_ILLEGAL_OP;
//		return IO_AnalogInput( &IO_bl1700_A, code, state, args, len );
	}

	return NO_ERROR;
}


#if 0
useix
int 
IO_error( 
	CmdCode			code, 
	IO_OpsStruct*	state, 
	char*			args, 
	int				len )
{
	switch( code ){
	case CMD_INIT:			// return type of hw interface
		return NO_ERROR;

	default:
		return ERR_ILLEGAL_OP;
	}
}
#endif


int BankTypeMatchesCmdType( int bank, CmdCode code )
{
	return 1;
}



///////////////////////////////////
// map Bank IDs onto specific portions of hardware
//
// Note: mapping a device to the wrong type can crash the system.

XMEM
IO_ConfigStruct
IO_ConfigTab[] = {
	//           fn,    ty, bd ba, ph, pd
	{	IO_xp8100_I,	ID,	0, 	A, 1, 1 },		// A -- 8100.A
	{	IO_xp8100_I,	ID,	0, 	B, 1, 1 },		// B -- 8100.B
	{	IO_xp8100_I,	ID,	1, 	A, 1, 1 },		// C -- 8100.A
	{	IO_xp8100_I,	ID,	1, 	B, 1, 1 },		// D -- 8100.B
	{	IO_xp8100_I,	ID,	2, 	B, 1, 1 },		// E -- 8100.B
	{	IO_bl1700_I,	ID,	0,	A, 1, 1 },		// F -- 1700.A

	{	IO_bl1700_O,	OD,	0, 	B, 0, 0 },		// G -- 1700.B
	{	IO_xp8100_O,	OD,	2, 	A, 0, 0 },		// H -- 8100.A

	{	IO_xp8300_O,	OD,	0, 	0, 0, 0 },		// I -- relays
	{	IO_xp8400_O,	OD,	1, 	0, 0, 0 },		// J -- relays
	{	IO_xp8400_O,	OD,	2, 	0, 0, 0 },		// K -- relays

	{	IO_bl1700_A,	IA,	0,	A, 0, 0 },		// L -- Analog calibrated floats
	{	IO_bl1700_A,	IA,	0,	B, 0, 0 },		// M -- Analog raw ADC values
	{	IO_bl1700_A,	IA,	0,	2, 0, 0 },		// N -- Analog cal inverter Gain
	{	IO_bl1700_A,	IA,	0,	3, 0, 0 },		// O -- Analog cal zero Offset
//	{	IO_error,		IA,	0,	0, 0, 0 },		// P -- illegal past end of table
};

#define POWER_BANK			( 'I' - 'A' )		// bank w/power relays
#define	POWER_PIN_12VDC		0					// enable 12vdc
#define	POWER_PIN_FANS		1					// enable fans

#define _1700_BANK_B		( 'G' - 'A' )		// on-board outputs

#define MAX_BANK  ( sizeof( IO_ConfigTab ) / sizeof( *IO_ConfigTab ))


int	
LegalBank( int bank )
{
	return ( 0 <= bank && bank < MAX_BANK );
}


// i/o mask

IO_OpsStruct IO_OpsTab[ MAX_BANK ];


XMEM void
IO_Init()
{
	IO_ConfigStruct* ct;
	IO_OpsStruct* ot;
	byte res;
	byte i;
	int id;

	ct = IO_ConfigTab;
	ot = IO_OpsTab;
	IO_OpsTabBase = IO_OpsTab;

	for( i=0; i < MAX_MODE; i++ )
		Mode[ i ] = 0;

	for( i=0; i < MAX_BANK; i++, ct++, ot++ ){
		ot->mask = 0xFFFF;
		ot->prev = ot->addr = ot->next = ot->change = 0;
		ot->board = ct->board;
		ot->bank = ct->bank;
		ot->id = 'A' + i;
		configStruct = ct;
		res = (*ct->fn)( CMD_INIT, ot, 0, 0 );

#if AUTO_DEF_EVENTS
		id = ot->id;		
		if( ct->period != 0 )
			AddEvent( 
				ot->id, 
				ct->phase, 
				ct->period, 
				CMD_POLL_BANK, 
				(byte*)&id, 
				1 );
#endif

#if 0
		printf( 
			"Init[%d] %c, b/b=%d/%d, a=%d\n", 
			i, 
			ot->id, 
			ct->board, 
			ct->bank, 
			ot->addr );
#endif

		if( res ){
			sendError( CMD_INIT, 0 );
			break;
		}
	}

//	ListAllEvents();

	send( "IO_Init() done\n" );
}

// #funcchain _GLOBAL_INIT IO_Init

// call an I/O function selected by external bank ID

int IO_ToBank( byte bank, CmdCode code, char* args, int len )
{
//	printf( "IO_ToBank( %c/%d, %d, %s, %d )\n", bank, index, code, args, len );

	// reject if out of bounds

	// banks are numbered a,b,c,... 0,1,2,...
	// must be a single, legal bank type at this point

	if( !LegalBank( bank )){
		sendError( ERR_NONX_BANK, bank );
		return ERR_NONX_BANK;
	}

	// gate to selected function
	
	return 
		(*IO_ConfigTab[ bank ].fn)( 
			code, 
			&IO_OpsTab[ bank ], 
			args,
			len );
}


///////////////////////////////////
// handle mode commands
//

void
HandleMode( CmdCode code, char* args, int len )
{
	register int sub, value;

	if(	FetchNum( &args, &len, &sub ) 
	||	sub < 0 
	||	sub >= MAX_MODE )
	{
		sendError( ERR_NONX_MODE, 0 );
		return;
	}

	switch( code ){
	case CMD_SET_MODE:
		if( FetchNum( &args, &len, &value ))
			return;

		Mode[ sub ] = value;

		/*FALLTHROUGH*/

	case CMD_GET_MODE:
		sendMode( sub, Mode[ sub ]);
	}
}


///////////////////////////////////
// apply an incoming command code to an arg list
//
// default incoming format is: code, bank, pin, value
//
//	code, pin, ... then gets routed to the appropriate bank
//

void
HandleBank( CmdCode code, char* args, int len )
{
	register int bank, res;

	if( FetchBank( &args, &len, &bank ))
		return;
 
	if( !LegalBank( bank ) && bank != ALL_BANKS ){
		sendError( ERR_NONX_BANK, bank );
		return;
	}

	res = NO_ERROR;

	// banks are numbered a,b,c,... 0,1,2...
	// bank 0xFF is a special signal for "all banks"
	
	if( bank == ALL_BANKS ){
		if( ALL_BANKABLE( code )){
			// if all banks and all bankable then apply to all banks

			for( bank = 0; bank < MAX_BANK; bank++ ){
				if( BankTypeMatchesCmdType( bank, code )){
					res = IO_ToBank( bank, code, args, len );
					if( res != NO_ERROR )
						break;
				}
			}
		} else {
			// all banks and not all bankable
			res = ERR_NON_BANKABLE;		
		}
	} else {
		// single bank
		res = IO_ToBank( bank, code, args, len );
	}

	if( res != NO_ERROR )
		sendError( res, bank );
}


XMEM void
HandleEvent(
	CmdCode	code, 
	char*	args, 
	int		len )
{
	int id;
	word ticks, repeat;
	int index, command;

	if( FetchChar( &args, &len, &id ))
		return;

	if( code <= CMD_EVENT_CHANGE ){
		if(	FetchInt( &args, &len, &ticks )
		||	FetchInt( &args, &len, &repeat )
		||	( args++, len-- < 0 )	// skip comma
		||	FetchNum( &args, &len, &command ))
			return;
	}

	switch( code ){
	case CMD_EVENT_ADD:
		AddEvent( id, ticks, repeat, command, args, len );
		break;

	case CMD_EVENT_CHANGE:
		ChangeEvent( id, ticks, repeat, command, args, len );
		break;

	case CMD_EVENT_LIST:
		if( id == '*' )
			ListAllEvents();
		else
			index = GetEvent( id );
			if( index <= 0 )
				sendError( ERR_NONX_EVENT, id );
		break;

	case CMD_EVENT_REMOVE:
		if( FetchInt( &args, &len, &index ))
			return;

		index = FindEvent( id, index );
		if( index >= 0 )
			RemoveEvent( index );
		else
			sendError( ERR_NONX_EVENT, id );
		break;
	}
}


void 
HandleCmd( 
	CmdCode	code, 
	char*	args, 
	int		len )
{
	register int bank, n;
	register int pin, value, ticks;

	code = c2b( code );

	if( !LEGAL_CMD( code )){
		sendError( ERR_ILLEGAL_OP, code );
		return;
	}

	// special-case (non-bank I/O) commands

	switch( code ){
	case CMD_SEND_0:
	case CMD_SEND_1:
	case CMD_SEND_B:

	case CMD_ENABLE:
	case CMD_DISABLE:
		HandleSerial( code, args, len );
		return;

	case CMD_DEBUG:
		HandleDebug( args, len );
		return;

	case CMD_SET_MODE:
	case CMD_GET_MODE:
		HandleMode( code, args, len );
		return;

	case CMD_EVENT_ADD:
	case CMD_EVENT_REMOVE:
	case CMD_EVENT_CHANGE:
	case CMD_EVENT_LIST:
		HandleEvent( code, args, len );
		return;

	default:

		// bank I/O commands (all unless special-cased above)

		HandleBank( code, args, len );
	}
}


/////////////////////////////////////////////////////////////
// Tasks
/////////////////////////////////////////////////////////////


///////////////////////////////////
// background task
//
// assemble incoming input commands and
// route them to the appropriate HW function
//


void 
readerCycle()
{
	char	inbuf[ 128 ];
	int		inlen;
	int		quoting, quoted;
	int		n, ch;
	
	segchain _GLOBAL_INIT {
		quoting = 0;
		quoted = 0;
		inlen = 0;
	}

	ch = recvch();

	if( quoted ){
		quoted = 0;	// quote just the current char

	} else {

		// normal character processing (bypassed if quoting)

		switch( ch ){

		case -1:
			return;

		case QUOTE:
			// if quoting, flag to quote next incoming char
			// otherwise add QUOTE to inbuf
			if( quoting ){
				quoted = 1;
				return;
			}
			break;

		case '\r':
		case '\n':							
			// process 1 command
			if( inlen == 0 )
				return;

			inbuf[ inlen ] = 0;
			HandleCmd( inbuf[ 0 ], &inbuf[ 1 ], inlen - 1 );

			inlen = quoted = quoting = 0;

			return;
		}
	}

	// error if no room

	if( inlen >= sizeof( inbuf ) - 1 ){
		sendError( ERR_INPUTOVERFLOW, 0 );
		inlen = 0;
		return;
	}

	// decide if we're quoting this command's args

	if( inlen == 0 ){
		ch = c2b( ch );
		quoting = CmdProps[ ch ].quoted;
	}

	// actually append the char to the buffer

	inbuf[ inlen++ ] = ch;
}



/////////////////////////////////////////////////////////////
// Library routines
/////////////////////////////////////////////////////////////


XMEM void 
enable_12v( int onOff )
{
	auto char pv[ 2 ];
	pv[ 0 ] = POWER_PIN_12VDC;
	pv[ 1 ] = onOff;
	
	IO_ToBank( 
		POWER_BANK, 
		CMD_SET, 
		pv, 
		2 );
//	plcXP83Out( 0, onOff );	
}


XMEM void 
enable_fans( int onOff )
{
	auto char pv[ 2 ];
	pv[ 0 ] = POWER_PIN_FANS;
	pv[ 1 ] = onOff;
	
	IO_ToBank( 
		POWER_BANK, 
		CMD_SET, 
		pv, 
		2 );
//	plcXP83Out( 1, onOff );	
}


// set pins for debug purposes
//

void PinOut( int pin, int value )
{
	if( Mode[ MODE_OSCOPE ])
		eioBrdDO( Sw2Hw[ pin ], value );	
}


void 
setMaskBit( 
	word* mask, 
	int pin, 
	int value )
{
	if( value )
		*mask |= ( 1 << pin );
	else
		*mask &= ~( 1 << pin );
}

////////////////////////////////////////////////////////
// send to one of the other channels if they are active

XMEM void
HandleSerial( byte code, char* args, int len )
{
	int chan, flags, speed;
	CHANNEL selected;
	byte i, n;
	int j, m;

#if 0
	printf( "SendComm( %d )\n", code );
#endif

	switch( code ){
	default:
		sendError( ERR_ILLEGAL_OP, code );
		break;
		
	case CMD_ENABLE:
		if( FetchNum( &args, &len, &chan)
		||	FetchInt( &args, &len, &speed )		// N * 1200 
		||	FetchInt( &args, &len, &flags ))	// 
			return;

		Activate( chan, speed, flags );
		break;

	case CMD_DISABLE:
		if( FetchNum( &args, &len, &chan))
			return;
		Deactivate( chan );
		break;

	case CMD_SEND_0:
	case CMD_SEND_1:
	case CMD_SEND_B:

//		printf( "HandleSerial( %s, %d )\n", args, len );

		selected = ActiveChan[ code - CMD_SEND_0 ];
		if( selected != NULL )
			while( aascWriteBlk( selected, args, len, 1 ) == 0 )
				continue;
		else
			sendError( ERR_INACTIVE, code );
		break;
	}
}

////////////////////////////////////////////////////////
// see if data is pending on any serial channels, 
// and forward it to host if so.

XMEM void
SendSerial( int i, int ch )
{
	char buf[ 6 ];
	int count;

	buf[0] = '>';
	count = 1;
	buf[ count++ ] = 'A' + i;

	if( ch == '\n' || ch == '\r' || ch == '\0' ){
		buf[ count++ ] = QUOTE;
	}

	buf[ count++ ] = ch;
	buf[ count++ ] = '\n';

//	printf( "SendSerial( '%s', %d )\n", buf, count );

	sendn( buf, count );
}


XMEM void
PollSerial()
{
	unsigned char ch;
	int i;
	int skip;

	if( Mode[ MODE_SERIAL_IN ] <= 0 )
		return;

	if(( skip++ % Mode[ MODE_SERIAL_IN ]) != 0 )
		for( i = 0; i < MAXCHAN; i++ )
			if( ActiveChan[ i ] != NULL )
				if( aascReadChar( ActiveChan[ i ], &ch ) == 1 )
					SendSerial( i, ch );
} 


///////////////////////////////////
// poller task
//
// monitor transitions and output them

int 
pollerCycle()
{
	byte bank;

	for( bank = 0; bank < MAX_BANK; bank++ ){

		if(( Mode[ MODE_POLLING ] & MODE_POLL_LOOP ) 
		&& IO_ConfigTab[ bank ].type == ID )
			IO_ToBank( bank, CMD_POLL_BANK, NULL, 0 );

		if( IO_OpsTab[ bank ].change ){
			
			DI();

			IO_OpsTab[ bank ].change = 0;
			IO_OpsTab[ bank ].prev = IO_OpsTab[ bank ].next;

			EI();

			IO_ToBank( bank, CMD_SEND_BANK_RESULT, NULL, 0 );
		}
	}
}


///////////////////////////////////
// background task -- trigger scheduled events
//

int 
backgroundTask()
{
	int toggle;
	toggle = 0;

	send( "READY\n" );
	
	for(;;){

		PinOut( 2, ( toggle = !toggle ));

		readerCycle();
		pollerCycle();
		PollSerial();
	}
}

///////////////////////////////////
// scheduler task -- trigger scheduled events
//

scheduler()
{
	// this task runs at top priority, 
	// so no locks are required by it's callees.

	PinOut( 0, 1 );	
	PinOut( 0, 0 );
	
	if( Mode[ MODE_EVENTS ]){
		PinOut( 1, 1 );	

		TriggerAllEvents();

		PinOut( 1, 0 );	
	}
}


///////////////////////////////////
// clicker task

XMEM void 
clicker()
{
#if 0
	IO_ToBank( POWER_BANK, CMD_SET, 5, 1 );
	suspend( 5 );
	IO_ToBank( POWER_BANK, CMD_SET, 5, 0 );
#endif
}


///////////////////////////////////
// blinker task -- a sign of life

XMEM int 
blinker()
{
	switchLED( 1 );
	suspend( 5 );
	switchLED( 0 );
	suspend( 5 );
	switchLED( 1 );
	suspend( 5 );
	switchLED( 0 );	
}

idle()
{
}

/////////////////////////////////////////////////////////////
// Main program & launch threads
/////////////////////////////////////////////////////////////

// setup RTK

#define RUNKERNEL 1

int (*Ftask[])() = { scheduler, clicker, blinker, backgroundTask };

int TaskFreq[] =   {      1,    80,    40 };

#define NTASKS ( sizeof( Ftask ) / sizeof( *Ftask ))

main()
{
	int i;

	// initialization

	VdInit();
	SerialInit();

	send( "IO Restarted!\n" );

	send( "# Resetting PLC Bus..." );
	eioResetPlcBus();
	eioPlcRstWait();
	send( "Resetted\n" );

	IO_Init();

//	scanForPlcBoards();

//	IO_Debug();

	enable_12v( 0 );
	enable_fans( 0 );
	
	// thread frequencies

	send( "# Starting tasks...\n" );

	for( i=0; i< NTASKS-1; i++ )
		run_every( i, TaskFreq[ i ]);

	(*Ftask[ NTASKS - 1 ])();
}



/////////////////////////////////////////////////////////////
// various debug commands

XMEM USEIX void
HandleDebug( char* args, byte len )
{
	int i, j, l, m, n, prev, pin, samples[ 32 ];
	char test_data[ IOSIZEA ];
	IO_OpsStruct* state; 

	switch( toupper( *args )){
	case 0:
	case '@':
		send( "# PING\n" );
		break;

	// searching & misc.

	case 'A':
		switch( args[ 1 ]){
		case '1':
			printf( "scanning for boards....\n" );
			for( i=0; i <= 7; i++ ){
				if( plcXP81In( i * 32 ) != -1 )
					printf( "Found XP8100 board %d\n", i );
			}
			for( i=0; i <= 7; i++ ){
				if( plcXP83Out( i * 8, 0 ) != -1 )
					printf( "Found XP8300/XP8400 board %d\n", i );
			}
			printf( "done\n" );
			break;

		case '2':
			printf( "MAX_BANK = %d\n", MAX_BANK );
			printf( "MAX_COMMANDS = %d\n", MAX_COMMANDS );
			printf( "sizeof( IO_ConfigTab ) == %d\n", sizeof( IO_ConfigTab ));
			printf( "sizeof( *IO_ConfigTab ) == %d\n", sizeof( *IO_ConfigTab ));

			for( i=0; i<MAX_BANK; i++ ){
				printf( "%d %04x\n", i, IO_ConfigTab[ i ].fn );
			}
			break;

		case '3':
			for( i=0; i <= CMD_DEBUG; i++){
				printf( "Prop[%d]: %d\n", 
					i,
					CmdProps[i].type );
			}
		default:
			goto illegal_op;
		}
		break;

	// PERFORMANCE measurements

	case 'B':

		switch( args[ 1 ]){

		case '1':
			IO_xp8100_I( CMD_POLL_BANK, IO_OpsTab, NULL, 0 );
			break;
		
		case '2':
			IO_ToBank( c2b( args[ 2 ]), CMD_POLL_BANK, NULL, 0 );
			break;

		case '3':
			HandleCmd( CMD_POLL_BANK, args+2, len-2 );
			break;
		
		case '4':		// toggle output pin as fast as possible
 
			pin = 0;
			n = (( args[ 2 ] == 0 )
					? 10
					: atoi( args + 2 ));

			send( "{kk\n" );

			for( i=0; i < n; i++ ){
				for( j=0; j < 1270; j++ ){
					// measured 25 uSec on time, about 40 uSec off
					eioBrdDO( Sw2Hw[ pin ], 1 );	
					eioBrdDO( Sw2Hw[ pin ], 0 );
				}
			}
			send( "}\n" );
			break;

		case '5':		// toggle output pin as fast as possible via decoder mechanism

			pin = 0;
			n = (( args[ 2 ] == 0 )
					? 10
					: atoi( args + 2 ));

			args[ 0 ] = 'A' + _1700_BANK_B;
			args[ 1 ] = '0';

			send( "{kk\n" );

			for( i=0; i < n; i++ ){
				for( j=0; j < 333; j++ ){
					// measured 1500 uSec on and off, 3msec round trip
					args[ 2 ] = 1;
					HandleCmd( CMD_SET, args, 3 );	
					args[ 2 ] = 0;
					HandleCmd( CMD_SET, args, 3 );
				}
			}
			send( "}\n" );
			break;

		case '6':		// read 2 input pins as fast as possible
 
			n = (( args[ 2 ] == 0 )
					? 10
					: atoi( args + 2 ));

			send( "{kk\n" );

			///////////
			// TIMES
			//
			// pair of raw reads, 4/3/01:
			//
			//    n samp sec
			//	100 200K  10 
			//  500   1M  54 
			// 1000   2M 109
			//
			// inport and mask 2, 4/4/01:
			//
			//    n samp sec
			//	100 200K   4
			//  500   1M  20
			// 1000   2M  41
			//
			

			prev = 0;
			for( i=0; i < n; i++ ){
				for( j=0; j < 1000; j++ ){
					l = inport( IO1700_PORTA0 );	// 4 bits
				}
			}
			send( "}\n" );
			break;
		
		case '7':		// read 2 input pins as fast as possible
			n = (( args[ 2 ] == 0 )
					? 10
					: atoi( args + 2 ));

			send( "{kk\n" );

			///////////
			// TIMES
			//
			// pair raw reads + logic, 4/3/01:
			//
			//    n samp sec
			//	100 200K  27 
			//  500   1M 136 
			// 1000   2M 273
			//
			// inport and mask 2, 4/4/01:
			//
			//    n samp sec
			//	100 200K  16 
			//  500   1M  84
			// 1000   2M 169
			//

			prev = 0;
			for( i=0; i < n; i++ ){
				for( j=0; j < 1000; j++ ){
					l = inport( IO1700_PORTA0 ) & 3;	// mask 2 of 4 bits

					samples[ l | (prev<<2) ] = test_data[ 0 ] | ( test_data[ 1 ] << 8 );
					prev = l;
				}
			}
			send( "}\n" );
			break;

		case '8':		// read 1 input as fast as possible
			n = (( args[ 2 ] == 0 )
					? 10
					: atoi( args + 2 ));

			send( "{kk\n" );

			///////////
			// TIMES
			//
			// reads + logic, 4/4/01:
			//
			//    n samp sec
			//	100 200K  10
			//  500   1M  51
			// 1000   2M 102
			//

			prev = 0;
			for( i=0; i < n; i++ ){
				for( j=0; j < 1000; j++ ){
					l = inport( IO1700_PORTA0 ) & 1;	// mask 1 of 4 bits

					if( prev < l ){	// rising edge
						samples[ l ] = inport( 0x14 ) | ( inport( 0x15 ) << 8 );
					}
					prev = l;
				}
			}
			send( "}\n" );
			break;

		case '9':		// sample data as fast as possible, ASM version
			n = (( args[ 2 ] == 0 )
					? 10
					: atoi( args + 2 ));

			send( "{kk\n" );

			///////////
			// TIMES
			//
			// reads + logic, 4/4/01:
			//
			//    n samp sec
			//	100 200K  
			//  500   1M  
			// 1000   2M 
			//

			prev = 0;
			for( i=0; i < n; i++ ){
				for( j=0; j < 1000; j++ ){
					l = inport( IO1700_PORTA0 ) & 1;	// mask 1 of 4 bits

					if( prev < l ){	// rising edge
						samples[ l ] = inport( 0x14 ) | ( inport( 0x15 ) << 8 );
					}
					prev = l;
				}
			}
			send( "}\n" );
			break;

		default:
			goto illegal_op;
		}
		break;

	case 'E':
		switch( args[ 1 ]){
		case 'T':
			AddEvent( 'Z', 20, 20, CMD_TOGGLE, (byte*)"I1", 2 );
			break;

		case 'P':
			AddEvent( 'Z', 60, 60, CMD_PULSE, (byte*)"I11p", 4 );
			break;

		case 'K':
			i = FindEvent( 'Z', 0 );
			if( i < 0 )
				send( "# event not found\n" );
			RemoveEvent( i );
			break;

		case 'L':
 			ListAllEvents();
			break;

		default:
			goto illegal_op;
		}
		break;

	case 'M':
		state = &IO_OpsTab[ c2b( args[ 1 ])];
		state->next = ( args[ 2 ] << 8 ) | args[ 3 ];
		state->change |=  ((( state->prev ^ state->next ) & state->mask ) != 0 );
		break;

	case 'N':
		break;
	
	case 'O':
		i = 1;
		do {
			sendMaskBankResult( '?', i );
			i <<= 1;
		} while( i != 0 );
		break;

	case 'P':
		i = c2b( args[ 1 ]) - 1;
		state = &IO_OpsTab[ i ];
		j = IO_ToBank( i, CMD_FETCH_BANK, NULL, 0 );
		sendBankResult( 'A' + i, j );
		break;

	case 'S':
		if( len > 0 )
			n = c2b( args[1]);		// number of K to send
		else
			n = 4;

		if( len > 1 )
			m = 1 << c2b( args[2]);		// line len
		else
			m = 128;

		if( m > sizeof( test_data ))
			m = sizeof( test_data );
		
		send( "{" );
		send( args + 1 );
		send( "\n" );
#if 0
		printf( "SENDK %s\n", args + 1 );
#endif
		memset( test_data, (int)'~', m );
		test_data[ m - 1 ] = '\n';
		
		for( i=0; i < n; i++ ){
			for( j=0; j < 1024 / m; j++ ){
				sendn( test_data, m );
			}
		}
#if 0
		printf( "DONE\n" );
#endif
		send( "}\n" );
		break;

	case 'Z':
		sendError( args[ 1 ], 0 );
		break;

illegal_op:
	default:
		sendError( ERR_ILLEGAL_OP, 0 );
	}

	send( "# DIAG Done\n" );
}


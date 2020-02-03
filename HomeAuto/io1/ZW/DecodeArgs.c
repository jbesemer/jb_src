// common code to unpack arg packet into global arg struct

byte 
DecodeArgs( CmdCode code, char* args, byte len )
{
	register char*	sig;

	arg.code = code;
	arg.args = args;
	arg.len = len;

	sig = CmdProps[ code ].argSig;
	arg.pin = arg.value = 0;

//	printf( "Decode( %d, '%s' ), '%s', %d\n", code, sig, args, len  );

	while( *sig ){
		
//		printf( "Sig %c, arg %c, len %d\n", *sig, *arg.args, arg.len );

		switch( *sig++ ){

		case 'b':
			if( FetchNum( &arg.bank ))
				return 1;

			// externally banks are numbered a,b,c,... 1,2,3,...
			// bank 0 or '@' is a special signal for "all banks".
			// however, internally bank 1 has index 0 in the IO table
			// everywhere past this point, "bank" is the index
			// in the table, and not the origin-1 external ID.
			// The reverse translation takes place on output.

			if( arg.bank == 0 )
				arg.bank = ALL_BANKS;
			else
				arg.bank--;
			break;

		case 'p':
			if( FetchNum( &arg.pin ))
				return 1;
			break;

		case 'v':
			if( FetchNum( &arg.value ))
				return 1;
			break;

		case 'm':
			if( FetchMask( &arg.mask ))
				return 1;
			break;

		case 'h':
			if( FetchNum( &arg.chan ))
				return 1;
			if( arg.chan > MAX_CHAN ){
				sendError( ERR_NONX_CHAN );
				return 1;
			}
			break;

		case 's':
			if( FetchNum( &arg.sub ))
				return 1;
			break;

		case 'f':
		
		#ifndef MAX_FLAGS
		#define MAX_FLAGS (16+8+4+2)
		#endif
		
			if( FetchNum( &arg.flags ))
				return 1;
			if( arg.flags > MAX_FLAGS ){
				sendError( ERR_NONX_FLAGS );
				return 1;
			}
			break;

		case 'r':
			if( FetchNum( &arg.rate ))
				return 1;
			break;

		case 'c':
			if( FetchChar( &arg.ch ))
				return 1;
			break;

		case '*':		// callee will parse remainder
				// arg.args and arg.len already are set right
			return 0;

		default:
			sendError( ERR_NONX_ARGSIG );
			return 1;
		}
	}

//	printf( "len == %d\n", arg.len  );

	if( arg.len > 0 ){
		sendError( ERR_EXTRA_ARGS );
		return 1;
	}

	return 0;
}


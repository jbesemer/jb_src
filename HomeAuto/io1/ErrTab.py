########################################
# error messages

from util import *

ErrTab = [
	( "NO_ERROR" , "SUCCESS -- not an error" ),
	( "ERR_NONX_PIN", "addressed pin does not exist" ),
	( "ERR_NONX_BANK", "addressed bank does not exist" ),
	( "ERR_ILLEGAL_OP", "operation is not supported for this bank/pin" ),
	( "ERR_HW_FAIL", "HW function reported a problem" ),
	( "ERR_MISSING_ARG", "not enough argument bytes for given command" ),
	( "ERR_INPUTOVERFLOW", "imput command too long" ),
	( "ERR_INACTIVE", "attempted send on inactive channel" ),
	( "ERR_CANTOPEN", "cannot activate port" ),
	( "ERR_NONX_ARGSIG", "internal error (argument signature)" ),
	( "ERR_EXTRA_ARGS", "too many args specified" ),
	( "ERR_NONX_CHAN", "invalid channel number" ),
	( "ERR_NONX_FLAGS", "invalid flags" ),
	( "ERR_NON_BANKABLE", "command cannot be applied to all banks" ),
	( "ERR_NONX_EVENT", "non-existant event" ),
	( "ERR_NONX_MODE", "non-existant mode" ),
	( "ERR_CANT_EVENT", "cannot create event (table full)" ),
	]

def ErrMessage( code ):
	index = c2b( code )
	if index < len( ErrTab ):
		return ErrTab[ index ][1] + " (" + ErrTab[ index ][0] + ")"
	else:
		return "Unrecognized error code #%d (%s)" % ( index, code )




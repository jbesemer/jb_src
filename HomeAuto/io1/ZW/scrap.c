#if 0
int pins[2][32];

int poller2()
{  
	char buf[99];
	int addr = 7*32;
	int pin;
	int value;

	for( pin=16; pin < 32; pin++ ){
		value = eioBrdDI( pin );
		if( pins[0][pin] != value ){
			sprintf( buf, "pin[0][%d] -> %d\r\n", pin, value );
			send( buf );
		}
		pins[0][pin] = value;
	}

	for( pin=0; pin < 32; pin++ ){
		value = plcXP81In( addr + pin );
		if( pins[1][pin] != value ){
			sprintf( buf, "pin[1][%d] -> %d\r\n", pin, value );
			send( buf );
		}
		pins[1][pin] = value;
	}
}

int task1()
{
//	char* msg = "Task     1\r\n";
//	send( msg );
}

int task2()
{
//	char* msg = "Task         2\r\n";
//	send( msg );
}
#endif

#if 0
int blinker1()
{
	int state;
	state = !state;
	switchLED( state );
}
#endif

#!/usr/bin/perl

%command_synonyms = ( 
	"alloff",	"A0", 
	"lightson",	"L1", 
	"lightsoff",	"L0", 
	"lights1",	"L1", 
	"lights0",	"L0" );

sub normalize_command
{
	my( $cmd ) = @_;
	$cmd = uc( $cmd );

	$cmd = $command_synonyms{ $cmd } if( exists $command_synonyms{ $cmd });

	return substr( $cmd, 0, 2 );
}

sub normalize_address
{
	my( $addr ) = @_;
	my( $house, $unit );

	$house = uc( substr( $addr, 0, 1 ));
	$unit = substr( $addr, 1 );

#	print "normalize: $addr -> $house, $unit\n";

	return sprintf( "%s%02d", $house, $unit ) 
		if( $house =~ /[ABCDEFGHIJKLMNOP]/);
	
	print "Warning: unable to normalize illegal address: $addr\n";
	return "";
}

$alias_file = "x10_aliases";

sub load_address_aliases
{
	my( $i, $name, $alias );

	if( open( ALI, $alias_file )){
		while( <ALI> ){
			chomp;
			s/#.*//;
			s/\/\/.*//;
			s/[ \t]+/ /g;
			$i = index $_, "=";
			if( $i >= 0 ){
				$name = trim( substr( $_, 0, $i - 1 ));
				$alias = trim( substr( $_, $i + 1 ));
				$address_alias{ lc( $name )} = lc( $alias );
#				print "alias \"$name\" = \"$alias\"\n";
			}
		}
		close ALI;
	} else {
		print "Warning: cannot open address alias file: $alias_file\n";
	}
}

sub trim
{
	local( $s ) = @_;
	$s =~ s/^[ \t\r\n]+//;
	$s =~ s/[ \t\r\n]+$//;
	return $s;
}

sub process_arg_list
{
	my( $arg );

	foreach $arg (@_){
#		print "foreach \"$arg\"\n";
		&process_arg( $arg );
	}
}

sub process_arg
{
	my( $arg ) = @_;
	$arg = lc( $arg );

	if( $arg =~ /^[0-9]+$/ ){
		if( $command eq "DI" || $command eq "BR" ){
			send_command( sprintf( "R%02d", $arg ));
			return;
		}
		print "Warning: repeat count ignored\n";
		return;
	}

	if( exists $address_alias{ $arg }){
		my( @list ) = split( /[ \t]+/, $address_alias{ $arg });
		&process_arg_list( @list );
	} else {
		# print "$command $arg\n";
		&process_command( $command, $arg );
	}
}

sub process_command
{
	my( $cmd, $addr ) = @_;
	my( $house, $unit );

	$addr = &normalize_address( $addr );

	return if( $addr eq "" );

	$house = substr( $addr, 0, 1 );

	send_command( $addr );
	send_command( $house . $cmd ); 
}

sub tty_send
{
	my( $cmd ) = @_;

	print TTYO "$cmd\r";
#	print TTYO "$cmd\r";
	if( $cmd ne '' ){
		$ts = &timestamp;
		print "$ts send: $cmd\n";
#		print "$ts send: $cmd\n";
	}
}

# send a command and retry until a proper reply is received

sub send_command
{
	my( $cmd ) = @_;
	my( $maxRetries, $res, $ts, $bypass );

	$maxRetries = 6;
	$bypass = 0;

	while( $maxRetries-- > 0 ){

		# send the command

		tty_send( $cmd ) if( !$bypass );
		$bypass = 0;

		# check the response

		$res = &tty_get;

		if( $res eq '' ){
			$bypass = 1;
			next;
		}

		$ts = &timestamp;
		print "$ts recv: $res";

		if( substr( $res, 0, 1 )  eq "?" ){
			print " -- ERROR returned from X10\n";
			return;
		}

		if( $res eq ( "!" . $cmd ) || $res eq ( ">" . $cmd )){
			print "\n";
			return;
		}

		print " -- unexpected result ( ", ord( $res ), " )\n";
	}

	print "\nRetry count exceeded\n";
}

# tty parameters

$tty = "/dev/ttyS1";
$stty_flags = "2400 cs8 cstopb -echo -echoctl -ignbrk -ignpar icrnl -isig -icanon -tostop";

# wait for tty input

sub wait_tty
{
	local( $nfound, $rin, $rout, $tleft );
	local( $replyTimeout ) = 1.5;

	$rin = '';
	vec( $rin, fileno( TTYI ), 1 ) = 1;
	$rout = $rin;

	( $nfound, $tleft ) = select( $rout=$rin, undef, undef, $replyTimeout );

	$ts = &timestamp;
	
#	print "$ts select: succeeded2 \n" 	if( vec( $rout, fileno( TTYI ), 1 ) == 1 );
#	print "$ts select: succeeded1 \n" 	if( $nfound > 0 );
#	print "$ts select: failed \n" 		if( $nfound < 0 );
#	print "$ts select: timed-out \n" 	if( $nfound == 0 );

	return $nfound > 0 ; ## || vec( $rout, fileno( TTYI ), 1 ) == 1 ;
}

sub tty_get
{
	local( $res, $ch );
	$res = "";

	while(1){
		if( wait_tty()){
			if( sysread( TTYI, $ch, 1 ) > 0 ){
				# next if( ord( $ch ) == 0 );
				last if( $ch eq "\r" || $ch eq "\n" );
				$res = $res . $ch;
			}
		} else {
			return $res . " [ select timed out ]";
		}
	}

	return $res;
}


sub open_ttys
{
	# set proper speed, etc.

	if( 0 ){
		my( $rv );
		$rv = system( "stty <" . $tty . " " . $stty_flags );
		if(( $rv >> 8 ) != 0 ){
			print "warning: unable to stty $tty\n";
		}
	}

	# actually open the device

	open TTYI, ( "<" . $tty ) || die "cannot open $tty for input";
	open TTYO, ( ">" . $tty ) || die "cannot open $tty for output";

	# turn off buffering ...

	select( TTYO );	$| = 1; 
	select( TTYI );	$| = 1; 
	select( STDOUT );

	# not sure but I think we need this to power the X10 unit
	# before sending it some 'real' commands.
	tty_send( "" );
	tty_get();
}

sub timestamp
{
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime;

	return sprintf( "%02d:%02d:%02d", $hour, $min, $sec );
}

# main program

{
	&load_address_aliases;

	$command = &normalize_command( shift @ARGV ); 

	&open_ttys;

	process_arg_list( @ARGV );
}


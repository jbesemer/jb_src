// www.lsleditor.org  by Alphons van der Heijden (SL: Alphons Jano)

string body = "asdf,asdf,asdf,asdf\nasdfasdf,asdf,asfd,adsf\nafdsasdfdfsa\nasdfasdf,daasf";
list zzz;

default
{
	state_entry()
	{
		llSay(0, "Hello, Avatar!");
		zzz = llParseString2List( body, ["\n"], [] );
	}
	touch_start(integer total_number)
	{
		integer N = llGetListLength( zzz );
		integer i;

		for( i=0; i<N; i++ ){
			list m = llParseString2List( llList2String( zzz, i ), [","], []);
			llSay( 0, "Count = " + (string)llGetListLength( m ));
		}
	}
}
string NAME  = "shazuka tigerpaw";           // name to look up
string URL   = "http://w-hat.com/name2key"; // name2key url
key    reqid;                               // http request id

default {
	state_entry() {
		reqid = llHTTPRequest( URL + "?terse=1&name=" +
			llEscapeURL(NAME), [], "" );
	}

	http_response(key id, integer status, list meta, string body) {
		if ( id != reqid )
			return;
		if ( status == 499 )
			llOwnerSay("name2key request timed out");
		else if ( status != 200 )
			llOwnerSay("the internet exploded!!");
		else if ( (key)body == NULL_KEY )
			llOwnerSay("No key found for " + NAME);
		else
			llOwnerSay(NAME + "'s key is: " + body );
	}
}
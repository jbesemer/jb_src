
// constants //////////////////////////////////////////////////

string VERSION = "2.2";

integer FROM_CHAN = -1723;    // channel on which we listen for commands

integer RADIO_CHAN      = 2112;            // channel radio listens for commands
string RADIO_SUSPEND_CMD   = "suspend";

string    GET_PLAYTIME_URL   = "http://cascade-sys.com/~jb/GetPlaytime.cgi";
string    MUSIC_BASE = "http://cascade-sys.com/~jb/Media/";
string    LOCAL_PREFIX = "//cascade";
string    MEDIA_KEYWORD = "/media/";
string    MP3_SUFFIX = ".mp3";

vector    TextColor       = <1,1,0>;
float     TextAlpha       = 1.0;

// commands

integer    GO_RESET = -1;
integer    GO_SAMESTATE = 0;
integer    GO_INITIALIZE = 1;
integer    GO_READY = 2;
integer    GO_NEXT = 3;
integer    GO_PREV = 4;
integer    GO_PAUSE = 5;
integer    GO_SUSPEND = 6;
integer    GO_RESUME = 7;
integer    GO_PLAY_LIST = 8;
integer    GO_PLAY_SINGLE = 9;

list Buttons = [
    "Pause",
    "Stop",
    "Reset",
    "Play",
    "Prev",
    "Next"
    ];

// parameters /////////////////////////////////////////////////

integer    TRACE = 1;
integer    SAMPLE_MODE = 0;
integer    REPEAT_MODE = 1;

// variables ////////////////////////////////////////////////////

string  PlayListName;        // base path for current play list
integer Total;                // total number of seletions in play list
integer PreviousTotal;     // total number of seletions in play list before current addition
integer Index;                // index of current selection
list    MusicURL;            // list of selection names
list    Duration;            // duration of corresponding selection

integer PlaybackListMode;        // whether we're playing a list or a single
integer PauseMode;              // whether we're paused or not

integer AppendMode;            // whether we're adding to a play list or starting a new one

key        RequestId;

integer	BURST_MAX = 15;
integer	BurstCount;

// outputs ////////////////////////////////////////////////////////

Say( string message ){
    llOwnerSay( "Sequencer " + message );
}

Error( string message ){
    Say( "Error: " + message );
}

Trace( string message ){
    if( TRACE )
        Say( message );
}

Trace2( string message ){
    if( TRACE >= 2 )
        Say( message );
}

ShowSelection( string s ){
    string title;
    string name = "";
    string path = "";

    if( llStringLength( s ) == 0 ){
        title = "[ Off ]";

    } else if( llGetSubString( s, 0, 1 ) == "[" ){
        title = s;

    } else {
        list p = llParseString2List( s, [ "/", "\\" ], [] );
        integer N = llGetListLength( p );

        if( N == 1 ){
            path = "";
        } else {
            path = Join( p, N-1, "/" ) +"\n";
        }

        name = llList2String( p, N-1 );

        if( PauseMode )
            title += " [ Paused ]";
        else if( PlaybackListMode )
            title = "Now Playing #" + (string)Index;
        else
            title = "Now Playing";

        title +=":\n";
    }

    SetText(
        title
            + path
            + name,
        TextColor,
        TextAlpha );
}

SetText( string msg, vector color, float alpha ){
    llMessageLinked(
        LINK_ALL_OTHERS,
        0,
        llList2CSV([ color, alpha, msg ]),
        NULL_KEY );
}


ShowDialog( key recipient ){
    llDialog( recipient, "Select Player Function", Buttons, FROM_CHAN );
}

// fundamental functions ///////////////////////////////////////

SetTimer( integer duration ){
    Trace2( "SetTimer " + (string)duration );
    llSetTimerEvent( duration );
}

PlayURL( string url ){
    llRegionSay( RADIO_CHAN, RADIO_SUSPEND_CMD );    // suspend radio

    url = str_replace( url, " ", "%20" );
    url = str_replace( url, "#", "%23" );

    //Trace( "Playing: " + url );
    llSetParcelMusicURL( url );
}

//    NotifyPlayer( string url )
//    {
//        llRegionSay( TO_CHAN, url );
//        llMessageLinked( LINK_THIS, 0, url, NULL_KEY);
//    }

PlaySelection( string musicURL, integer duration ){
    Trace( "Playing: "
        + (string)Index + ": "
//        + (string)Total + ", "
        + (string)duration + ", "
        + musicURL );

    ShowSelection( musicURL );

    if( duration > 0 )
        if( SAMPLE_MODE )
            SetTimer( SAMPLE_MODE );
        else
            SetTimer( duration );
    else
            SetTimer( 0 );

    if( llSubStringIndex(musicURL, "http://" ) < 0 )
        musicURL = MUSIC_BASE + musicURL;

    PlayURL( musicURL );
}

PlayIndexedSelection( integer index ){
    Index = index % llGetListLength( MusicURL );
    PlaySelection(
        llList2String( MusicURL, Index ),
        llList2Integer( Duration, Index ));
}

PlayFirstSelection(){
    PlayIndexedSelection( 0 );
}

PlayCurrentSelection(){        // i.e. "Resume"
    PlayIndexedSelection( Index );
}

PlayNextSelection(){
    PlayIndexedSelection( Index + 1 );
}

PlayPrevSelection(){
    PlayIndexedSelection( Index - 1 );
}

PlaySilence(){
    PlaySelection( "", -1 );
}

// general string handling fns ////////////////////////////////////////////

string str_replace(string src, string from, string to){    //replaces all occurrences of 'from' with 'to' in 'src'.
    integer len = (~-(llStringLength(from)));
    if(~len)
    {
        string  buffer = src;
        integer b_pos = -1;
        integer to_len = (~-(llStringLength(to)));
        @loop;//instead of a while loop, saves 5 bytes (and run faster).
        integer to_pos = ~llSubStringIndex(buffer, from);
        if(to_pos)
        {
//            b_pos -= to_pos;
//            src = llInsertString(llDeleteSubString(src, b_pos, b_pos + len), b_pos, to);
//            b_pos += to_len;
//            buffer = llGetSubString(src, (-~(b_pos)), 0x8000);
            buffer = llGetSubString(src = llInsertString(llDeleteSubString(src, b_pos -= to_pos, b_pos + len), b_pos, to), (-~(b_pos += to_len)), 0x8000);
            jump loop;
        }
    }
    return src;
}

string remove_quotes( string message ){
    string s1 = llGetSubString( message, 0, 0 );
    string s2 = llGetSubString( message, -1, -1 );

    if( s1 == "\"" && s2 == "\"" )
        return llGetSubString( message, 1, -2 );
    else
        return message;
}

string Join( list l, integer count, string sep ){
    string s = llList2String( l, 0 );
    integer i;

    for( i=1; i < count; i++)
        s += sep + llList2String( l, i );

    return s;
}

integer GetValue( string text ){
    integer k = llSubStringIndex( text, "=" );

    if( k < 0 ){
        Error( "Missing '=' in: " + text );
        return 0;
    }

    return (integer)llGetSubString( text, k+1, -1 );
}

string NormalizeName( string message ){
    message = llStringTrim( message, STRING_TRIM );
    message = remove_quotes( message );
    message = str_replace( message, "\\", "/" );
    return message;
}

integer ClasifyURL( string message ){
    string msg = llToLower( message );
    integer j = llSubStringIndex( msg, LOCAL_PREFIX );
    integer k = llSubStringIndex( msg, MEDIA_KEYWORD );

    if( j == 0 && k >= 0 ){
        // is a local path
        message = llGetSubString( message, k + 6, -1 );    // trim prefix thru /media/ component, leaving leading "/"
        j = llSubStringIndex( msg, MP3_SUFFIX );
        if( j < 0 || j != llStringLength( msg ) - llStringLength( MP3_SUFFIX )){
            // is some kind of play-list
            PlayListName = message;
            if( AppendMode ){
                PreviousTotal = Total++;    // update PrevTotal and ensure Index < Total
                return GO_PLAY_LIST;
            } else {
                PreviousTotal = 0;
                return GO_INITIALIZE;
            }
        } else {
            // is a single play Mp3
            //message = MUSIC_BASE + message;
        }
    } else {
        // is some kind of generic URL
    }

    PlaySelection( message, 0 );
    return GO_PLAY_SINGLE;
}

// process an incoming message/command ////////////////////////////////////////

integer ProcessMessage( string message ){
    Trace( "Hearing: " + message );

    message = NormalizeName( message );
    string m2 = llToLower( message );

    if( message == "reset" )
        llResetScript();

    else if( m2 == "stop" || m2 == "end" ){
        Say( "Stopping...");
        PlaySilence();
        return GO_READY;

    } else if( m2 == "next" ){
        Say( "Skipping forw...");
        return GO_NEXT;

    } else if( m2 == "prev" ){
        Say( "Skipping back...");
        return GO_PREV;

    } else if( m2 == "pause" ){
        Say( "Pausing...");
        return GO_PAUSE;

    } else if( m2 == "play" || m2 == "resume" ){
        Say( "Resuming...");
        return PauseMode;

    } else if( m2 == "suspend" ){
        Say( "Suspending...");
        return GO_SUSPEND;

    } else if( llGetSubString( m2, 0, 4 ) == "trace" ){
        integer TRACE = GetValue( m2 );

    } else if( llGetSubString( m2, 0, 5 ) == "repeat" ){
        REPEAT_MODE = GetValue( m2 );

    } else if( llGetSubString( m2, 0, 5 ) == "sample" ){
        SAMPLE_MODE = GetValue( m2 );
        if( SAMPLE_MODE > 0 )
            SetTimer( SAMPLE_MODE );

    } else {
        AppendMode = 0;
        if( llGetSubString( message, 0, 0 ) == "+" ){
            AppendMode = 1;
            message = llStringTrim( llGetSubString( message, 1, -1 ), STRING_TRIM );
        }

        return ClasifyURL( message );
    }

    return GO_SAMESTATE;
}

// Playlist Info HTTP request/response ///////////////////////////////////////////

AddItemToPlaylist( list row )
{
	integer N = llGetListLength( row );
	integer i;

	integer index = 1 + (integer)llList2String( row, 0 );
	Total =  PreviousTotal + (integer)llList2String( row, 1 );
	integer duration = (integer)llList2String( row, 2 );
	string musicURL = llList2String( row, 3 );
	for( i = 4; i<N; i++ )
		MusicURL += "," + llList2String( row, i );

	Duration += [ duration ];
	MusicURL += [ musicURL ];

	Trace( "Received: "
		+ (string)index + " / "
		+ (string)Total + ", "
		+ (string)duration + ", "
		+ musicURL );
}

integer AddItemsToPlaylist( string body )
{
    list lines = llParseString2List( body, ["\n"], [] );
    integer N = llGetListLength( lines );
	integer errors = 0;
    integer i;

    for( i=0; i<N; i++ ){
        string line = llList2String( lines, i );
        list fields = llParseString2List( line, [","], []);
        if( llGetListLength( fields ) >= 4 )
            AddItemToPlaylist( fields );
		else
			errors += 1;
	}

	return errors;
}

integer HandleHTTPResponse( key id, integer status, string body ){
    if ( id == RequestId )
    {
        if ( status == 499 )
            Error("GetPlaytime request timed out");

        else if ( status != 200 )
            Error("the internet exploded!!");

        else if( llGetSubString( body, 0, 5 ) == "Error:" ){
            Say( "Server " + body );    // "Server Error:"

        } else {
			if( AddItemsToPlaylist( body ) == 0 )
                return 1;

            Error( "Bad HTTP response: " + body );
        }
    }

    return 0;
}

SubmitRequest( integer index ){ //, string name )
    Trace2( "Requesting: " + (string)index + ", " + PlayListName );

	BurstCount++;

    RequestId
        = llHTTPRequest(
            GET_PLAYTIME_URL
                + "?index="
                + (string)index
                + "&name="
                + llEscapeURL( PlayListName ),
            [],
            "" );
}


SubmitFirstRequest(){
    MusicURL = [];
    Duration = [];

    Index = 0;
	PreviousTotal = 0;

    SubmitRequest( 0 );    // request first one
}

SubmitNextRequestIfAny(){
	integer N = llGetListLength( MusicURL );

	if( N < Total )
		SubmitRequest( N - PreviousTotal );
}

// default state -- one-time initialization ///////////////////////////////////////

default {
    state_entry(){
        llSetText( "", <0,0,0>, 0 );
        Trace( "Listening on " + (string)FROM_CHAN );
        state Ready;
    }

    on_rez( integer param ){
        llResetScript();
    }
}

// Ready -- waiting for a command /////////////////////////////////////////////////

state Ready {
    state_entry(){
        Trace( "Ready..." );
        //PlaySilence();
        llListen( FROM_CHAN, "", NULL_KEY, "" );
    }

    listen( integer channel, string name, key id, string message ){
        integer action = ProcessMessage( message );
        ShowDialog( id );

        if( action == GO_INITIALIZE )
            state Initialize;

        else if( action == GO_PLAY_SINGLE )
            state PlayingSingle;
    }

    touch_end( integer num ){
        ShowDialog( llDetectedKey( 0 ));
    }

    on_rez( integer param ){
        llResetScript();
    }
}

// Initialize -- fetching first item in play list /////////////////////////////////////

state Initialize {
    state_entry() {
        Trace( "Initializing..." );
        llListen( FROM_CHAN, "", NULL_KEY, "" );
        SubmitFirstRequest();
    }

    http_response(key id, integer status, list meta, string body){
        if( HandleHTTPResponse( id, status, body )){
            state PlayingList;
        } else
            state Ready;
    }

    listen( integer channel, string name, key id, string message ){
        integer action = ProcessMessage( message );
        ShowDialog( id );

        if( action == GO_READY )
            state default;

        else if( action == GO_INITIALIZE )
            state Initialize;

        else if( action == GO_PLAY_SINGLE )
            state PlayingSingle;

        else if( action == GO_PAUSE )
            state Pausing;
    }

    touch_end( integer num ){
        ShowDialog( llDetectedKey( 0 ));
    }

   on_rez( integer param ){
        llResetScript();
    }
}

// playing a list of at least one track ////////////////////////////////////////////////
// also fetches all remaining items

state PlayingList {
    state_entry() {
        Trace( "Playing List..." );
        PlaybackListMode = 1;
        llListen( FROM_CHAN, "", NULL_KEY, "" );
        PlayCurrentSelection();
        SubmitNextRequestIfAny();
    }

    state_exit(){
        SetTimer( 0 );
    }

    http_response(key id, integer status, list meta, string body){
        if( HandleHTTPResponse( id, status, body )){
            SubmitNextRequestIfAny();

        } else {
            // if there's an HTTP error, then there's no recovery --
            // we continue playing the list such as it is (at least 1 song)
        }
    }

    timer(){
        Trace2( "Timer Expired..." );
        PlayNextSelection();
		SubmitNextRequestBurstIfAny();
		}

    listen( integer channel, string name, key id, string message ){
        integer action = ProcessMessage( message );
        ShowDialog( id );

        if( action == GO_READY )
            state Ready;

        else if( action == GO_INITIALIZE )
            state Initialize;

        else if( action == GO_PLAY_SINGLE )
            state PlayingSingle;

        else if( action == GO_PLAY_LIST )
            SubmitNextRequestIfAny();

        else if( action == GO_PAUSE ) {
            PauseMode = GO_PLAY_LIST;
            PlaySilence();
            state Pausing;

        } else if( action == GO_SUSPEND ){
            PauseMode = GO_PLAY_LIST;
            state Pausing;

        } else if( action == GO_NEXT )
            PlayNextSelection();

        else if( action == GO_PREV )
            PlayPrevSelection();
    }

    touch_end( integer num ){
        ShowDialog( llDetectedKey( 0 ));
    }

    on_rez( integer param ){
        llResetScript();
    }
}

state Pausing {
    state_entry() {
        Trace( "Pausing..." );
        llListen( FROM_CHAN, "", NULL_KEY, "" );
        // PlaySilence();
        //ShowSelection( "[ Paused ]" );
    }

    state_exit(){
        PauseMode = 0;
    }

    http_response(key id, integer status, list meta, string body){
		HandleHTTPResponse( id, status, body );
    }

    listen( integer channel, string name, key id, string message ){
        integer action = ProcessMessage( message );
        ShowDialog( id );

        if( action == GO_READY )
            state Ready;

        else if( action == GO_INITIALIZE )
            state Initialize;

        else if( action == GO_PLAY_LIST )
            state PlayingList;

        else if( action == GO_PLAY_SINGLE )
            state PlayingSingle;
    }

    touch_end( integer num ){
        ShowDialog( llDetectedKey( 0 ));
    }

    on_rez( integer param ){
        llResetScript();
    }
}

state PlayingSingle {
    state_entry() {
        Trace( "Playing Single..." );
        PlaybackListMode = 0;
        llListen( FROM_CHAN, "", NULL_KEY, "" );
    }

    listen( integer channel, string name, key id, string message ){
        integer action = ProcessMessage( message );
        ShowDialog( id );

        if( action == GO_READY )
            state Ready;

        else if( action == GO_INITIALIZE )
            state Initialize;

        else if( action == GO_PAUSE ) {
            PauseMode = GO_PLAY_SINGLE;
            PlaySilence();
            state Pausing;

        } else if( action == GO_SUSPEND ){
            PauseMode = GO_PLAY_SINGLE;
            state Pausing;

        } else if( action == GO_PLAY_LIST )
            state PlayingList;
    }

    touch_end( integer num ){
        ShowDialog( llDetectedKey( 0 ));
    }

    on_rez( integer param ){
        llResetScript();
    }
}

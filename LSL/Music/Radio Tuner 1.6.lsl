////////////////////////////////////////////////////////////////////
// Configuration Settings
////////////////////////////////////////////////////////////////////

string VERSION          = "1.6";

float PLAYING_DELAY     = 0.25;
integer TRACE           = 0;
integer FACE            = 4;

string SILENCE 			= "";

integer RADIO_CHAN      = 2112;            // manual chat command channel

integer CD_CHAN         = -1723;        // channel on which cd player listens for commands
string CD_SUSPEND_CMD   = "suspend";
//string CD_STOP_CMD    = "stop";

integer DLG_CHAN        = -2432432;    // channel for dialog

integer DO_NOTHING		= 0;
integer DO_PLAY			= 1;
integer DO_STOP			= 2;
integer DO_SUSPEND		= 3;

integer MENU_PAGE		= 9;

// Config Variables

vector  TextColor       = <1,1,1>;
integer TextureIndex    = 0;

list    AccessList      = [];
integer IfGroupShared   = 0;
integer IfShared        = 1;
integer IfVisible       = 0;        // TBD

vector  ErrorColor      = <1,0,0>;
vector  GreenColor      = <0,1,0>;
float   TextAlpha       = 1.0;


//////////////////////////////////////////////////////////////////////////////////////////////////
// Self Upgrading Script by Cron Stardust based upon work by Markov Brodsky and Jippen Faddoul.
// If this code is used, this header line MUST be kept.
//////////////////////////////////////////////////////////////////////////////////////////////////

upgrade() {
    string self = llGetScriptName();
    string basename = self;

    // If there is a space in the name, find out if it's a copy number and correct the basename.

    if (llSubStringIndex(self, " ") >= 0) {
        // Get the section of the string that would match this RegEx: /[ ][0-9]+$/
        integer start = 2; // If there IS a version tail it will have a minimum of 2 characters.
        string tail = llGetSubString(self, llStringLength(self) - start, -1);
        while (llGetSubString(tail, 0, 0) != " ") {
            start++;
            tail = llGetSubString(self, llStringLength(self) - start, -1);
        }

        // If the tail is a positive, non-zero number then it's a version code to be removed from the basename.

        if ((integer)tail > 0) {
            basename = llGetSubString(self, 0, -llStringLength(tail) - 1);
        }
    }

    // Remove all other like named scripts.

    integer n = llGetInventoryNumber(INVENTORY_SCRIPT);
    while (n-- > 0) {
        string item = llGetInventoryName(INVENTORY_SCRIPT, n);

        // Remove scripts with same name (except myself, of course)

        if (item != self && 0 == llSubStringIndex(item, basename)) {
            llRemoveInventory(item);
        }
    }
}

///////////////////////////////////////////////////////////////////
// App State and helper functions
///////////////////////////////////////////////////////////////////

// RADIO_CHAN Presets Database

list    PresetsNames;
list    PresetsURLs;

integer CurrentIndex;
string  CurrentName;
string  CurrentURL;

indicate_music_playing(){
    llSetPrimitiveParams([ PRIM_FULLBRIGHT, FACE, 1 ]);

    if( CurrentURL != "" )
        llSetText(
            "Now Playing:\n"
                + CurrentName
                + "\n[ "
                + CurrentURL
                + " ]",
            TextColor,
            TextAlpha );
    else
        llSetText( "[ No Url Selected to Play ]", ErrorColor, TextAlpha );
}

indicate_music_stopped(){
    llSetPrimitiveParams([ PRIM_FULLBRIGHT, FACE, 0 ]);
    llSetText( "[ Off ]", GreenColor, TextAlpha );
}

play_music(){
    llRegionSay( CD_CHAN, CD_SUSPEND_CMD );   // suspend CD player

    if( TRACE )
        llSay( 0, "Playing: '" + CurrentURL + "'" );

    indicate_music_playing();
    llSetParcelMusicURL( CurrentURL );
}

stop_music(){
    if( TRACE )
        llSay( 0, "Stopped" );

    indicate_music_stopped();
    llSetParcelMusicURL( SILENCE );
}

set_channel_index( integer index ){
    integer N = llGetListLength( PresetsNames );

    if( index >= N )        index = 0;
    else if( index < 0 )    index = N - 1;

    CurrentIndex = index;
    CurrentName = llList2String( PresetsNames, CurrentIndex );
    CurrentURL = llList2String( PresetsURLs, CurrentIndex );

//  llRegionSay( RADIO_CHAN, CurrentKey );
}

set_channel( string channel ){
    if( TRACE )
        llSay( 0, "set_channel: " + channel );

    integer index = llListFindList( PresetsNames, [ channel ]);
    if( index >= 0 ){
        set_channel_index( index );
    } else {
        CurrentURL = channel;
        CurrentName = "[ manual entry ]";
    }

    if( TRACE )
        llSay( 0, "set_channel: " + (string)CurrentIndex + "  '" + CurrentURL + "'");
}

next_channel(){
    set_channel_index( CurrentIndex + 1 );
}

prev_channel(){
    set_channel_index( CurrentIndex - 1 );
}

add_access_list( string value ){
    if( value != "" )
        AccessList = AccessList + (list)value;
}

integer add_presets( string data ){
    list temp = llParseStringKeepNulls( data, [","], []);
    if( llGetListLength( temp ) == 3 ){
        string Key = llStringTrim( llList2String( temp, 0 ), STRING_TRIM );
        string Name = llStringTrim( llList2String( temp, 1 ), STRING_TRIM );
        string Url = llStringTrim( llList2String( temp, 2 ), STRING_TRIM );

        llSetText( "Processing Presets\n" + Name, ErrorColor, TextAlpha );

        PresetsNames = (PresetsNames=[]) + PresetsNames + Name;
        PresetsURLs = (PresetsURLs=[]) + PresetsURLs + Url;
        return 0;

     } else if( llGetListLength( temp ) == 2 ){
        string Name = llStringTrim( llList2String( temp, 0 ), STRING_TRIM );
        string Url = llStringTrim( llList2String( temp, 1 ), STRING_TRIM );

        llSetText( "Processing Presets\n" + Name, ErrorColor, TextAlpha );

        PresetsNames = (PresetsNames=[]) + PresetsNames + Name;
        PresetsURLs = (PresetsURLs=[]) + PresetsURLs + Url;
        return 0;

    } else
        return 1;
}


set_front_panel( integer index ){
    integer N = llGetInventoryNumber( INVENTORY_TEXTURE );

    if( index < 0 )         index = N - 1;
    else if( index >= N )   index = 0;
    TextureIndex = index;

    string name = llGetInventoryName( INVENTORY_TEXTURE, index );
    if( name == "" )
        name = llGetInventoryName( INVENTORY_TEXTURE, 0 );

    llSetTexture( name, FACE );
}

next_front_panel(){
    set_front_panel( TextureIndex + 1 );
}

prev_front_panel(){
    set_front_panel( TextureIndex - 1 );
}

show_channels(){
    integer N = llGetListLength( PresetsNames );
    integer i;

    for( i=0; i<N; i++ ){
        llSay( 0, "Url: "
            + (string)i
            + " "
            + llList2String( PresetsNames, i )
            + " --> "
            + llList2String( PresetsURLs, i ));
    }
}

show_settings(){
    llSay( 0, "Settings...." );
    llSay( 0, "RADIO_CHAN: " + (string)RADIO_CHAN );
    llSay( 0, "Shared:  " + (string)IfShared );
    llSay( 0, "Access:  " + (string)AccessList );
    llSay( 0, "Visible: " + (string)IfVisible );
    llSay( 0, "Color:   " + (string)TextColor );
    llSay( 0, "" );
}

show_help(){
    llSay( 0, "Commands...." );
    llSay( 0, "xxx -- switch to stream named 'xxx'" );
    llSay( 0, "on -- turn player on" );
    llSay( 0, "off -- turn player off" );
    llSay( 0, "next -- switch to next channel" );
    llSay( 0, "prev -- switch to previous channel" );
    llSay( 0, "nextfp -- switch to next front panel texture" );
    llSay( 0, "prevfp -- switch to previous front panel texture" );
    llSay( 0, "add abbr,name,url -- add a new stream to the list of presets" );
    llSay( 0, "play name -- switch to stream name and play it" );
    llSay( 0, "presets -- show preset channels" );
    llSay( 0, "settings -- show config settings" );
    llSay( 0, "help -- print this list of commands" );
    llSay( 0, "" );
}

show_buttons( string label, list buttons )
{
    integer N = llGetListLength( buttons );
    integer i;

    llSay( 0, ">>> " + label + " " + (string)N );

    for( i=0; i<N; i++ )
        llSay( 0,
            (string)i
            + ": "
            + llList2String( buttons, i ));

    llSay( 0, "<><><>" );
}

// dialog display state

integer DialogIndex = 0;
list Buttons;

string BUTTON_NEXT = ">> Next";
string BUTTON_PREV = "<< Prev";
string BUTTON_EXIT = "[X] Power Off";
string BUTTON_BLANK = "  ";

string ButtonIfEnabled( string button, integer condition){
    if( condition )
        return button;
    else
        return BUTTON_BLANK;
}

list permutations = [ 6,7,8, 3,4,5, 0,1,2 ];

show_dialog( key who ){
    integer N = llGetListLength( PresetsNames );
    integer M = DialogIndex + MENU_PAGE;
    integer i;

    Buttons = [
        ButtonIfEnabled( BUTTON_PREV, DialogIndex > 0 ),
        ButtonIfEnabled( BUTTON_NEXT, DialogIndex < N - MENU_PAGE ),
        BUTTON_EXIT ];

    if( M > N )
        M = N;

    llSay( 0, "" );

    for( i=DialogIndex; i < M; i++ ){
        integer j = DialogIndex + llList2Integer( permutations, i % MENU_PAGE );
        string s = llList2String( PresetsNames, j );

        if( llStringLength( s ) > 24 )
            s = llGetSubString( s, 0, 23 );

        if( llStringLength( s ) <= 0 )
            s = " ";

        Buttons = (Buttons=[]) + Buttons + [ s ];
    }

    llDialog( who, "Select RADIO_CHAN", Buttons, DLG_CHAN );
}

integer handle_dialog_message( integer chan, string name, key sender, string message ){

    if( message == BUTTON_EXIT )
        return DO_STOP;

    integer N = llGetListLength( PresetsNames );

    if( message == BUTTON_NEXT ){
        DialogIndex = DialogIndex + MENU_PAGE;
        if( DialogIndex >= N )
            DialogIndex = N - 1;
        show_dialog( sender );

    }  else if( message == BUTTON_PREV ){
        DialogIndex = DialogIndex - MENU_PAGE;
        if( DialogIndex < 0 )
            DialogIndex = 0;
        show_dialog( sender );

    } else if( message == BUTTON_BLANK ){
        return DO_NOTHING;

    } else {
        integer index = llListFindList( Buttons, [ message ]);
//      llSay( 0, "DialogIndex: " + (string)DialogIndex );
//      llSay( 0, "Index: " + (string)index + " Msg: " + message );
        if( index >= 0 )
            set_channel_index( DialogIndex + llList2Integer( permutations, index - 3 ));
        else
            llOwnerSay( "Bad dialog message: " + message );
    }

    return DO_NOTHING;
}

integer handle_message( integer chan, string name, key sender, string message ){

    if( chan == DLG_CHAN )
        return handle_dialog_message( chan, name, sender, message );

    if( !IfShared && sender != llGetOwner()){
        llSay( 0, "Ignoring command from non-owner" );
        return DO_NOTHING;
    }

    if( IfGroupShared && !llSameGroup( sender )){
        llSay( 0, "Ignoring command from non-group member" );
        return DO_NOTHING;
    }

    if( llGetListLength( AccessList ) > 0 && llListFindList( AccessList, [ name ]) < 0 ){
        llSay( 0, "Ignoring command from unauthorized source" );
        return DO_NOTHING;
    }

    if( message == "on" )               return DO_PLAY;
    else if( message == "resume" )      return DO_PLAY;
    else if( message == "off" )         return DO_STOP;
    else if( message == "suspend" )     return DO_SUSPEND;

    else if( message == "next" )        next_channel();
    else if( message == "prev" )        prev_channel();
    else if( message == "nextfp" )      next_front_panel();
    else if( message == "prevfp" )      prev_front_panel();
    else if( message == "presets" )     show_channels();
    else if( message == "settings" )    show_settings();
    else if( message == "help" )        show_help();
    else {
        set_channel( message );
    }

    return DO_NOTHING;
}


/////////////////////////////////////////////////////////////////
// Process Configuration File
/////////////////////////////////////////////////////////////////

// config reader state vars

string  ConfigNotecardName = "Configuration";
string  SettingsNotecardName = "Music URLs";

key     QueryIdConfig;
key     QueryIdSettings;
integer QueryIndex;

default {
    state_entry(){
        llSay( 0, "JB Internet Player Version " + VERSION );

        // remove any previous versions of this script
        llSetText( "Upgrading", ErrorColor, TextAlpha );
        upgrade();

        // general init
        PresetsNames = [];
        PresetsURLs = [];
        DialogIndex = 0;

        // start reading the config file
        QueryIndex = 0;
        QueryIdConfig = llGetNotecardLine( ConfigNotecardName, QueryIndex );
        llSetText( "Processing Config", ErrorColor, TextAlpha );
    }

    state_exit(){
        float k = 1024;
        float max = 64;
        float free = llGetFreeMemory() / k;
        float pct = 100.0 * free / max ;

        llOwnerSay( "Ready" );
        llOwnerSay( "Memory: "
            + (string)free
            + "K Free, "
            + (string)pct
            + " %" );
    }

    dataserver( key queryId, string Data ){
        string data = Data;

        if( queryId == QueryIdConfig ){
            if( data != EOF ){
                integer pos = llSubStringIndex( data, "#" );
                if( pos >= 0 )
                    data = llDeleteSubString( data, pos, -1 );
                data = llStringTrim( data, STRING_TRIM );

                if( data != "" && llSubStringIndex( data, ":" ) >= 0 ){
                    list tmp = llParseString2List( data, [":"], []);
                    string setting = llToUpper( llStringTrim( llList2String( tmp, 0 ), STRING_TRIM ));
                    string value = llToUpper( llStringTrim( llList2String( tmp, 1 ), STRING_TRIM ));

                    if( setting == "CHANNEL" )      RADIO_CHAN = (integer)value;
                    else if( setting == "SHARED" )  IfShared = (integer)value;
                    else if( setting == "ACCESS" )  add_access_list( value );
                    else if( setting == "VISIBLE" ) IfVisible = (integer)value;
                    else if( setting == "COLOR" )   TextColor = (vector)value;
                    else if( setting == "PANEL" )   set_front_panel( (integer)value );
                    else if( setting == "COLOR" )   PLAYING_DELAY = (float)value;
                    else if( setting == "TRACE" )   TRACE = (integer)value;
                    else
                        llSay( 0, "Ignoring: " + Data );
                }

                QueryIdConfig = llGetNotecardLine( ConfigNotecardName, ++QueryIndex );

            } else {
                QueryIndex = 0;
                QueryIdSettings = llGetNotecardLine( SettingsNotecardName, QueryIndex );
                llSetText( "Processing Presets", ErrorColor, TextAlpha );
            }

        } else if( queryId == QueryIdSettings ){
            if( data != EOF ){
                integer pos = llSubStringIndex( data, "#" );
                if( pos >= 0 )
                    data = llDeleteSubString( data, pos, -1 );
                data = llStringTrim( data, STRING_TRIM );

                if( data != "" ){
                    if( add_presets( data )){
                        llSay( 0, " Bad Preset: " + Data );
                    }
                }

                QueryIdSettings = llGetNotecardLine( SettingsNotecardName, ++QueryIndex );

            } else {

                // done processing settings
                // pad Names to an even multiple of MENU_PAGE

                integer n = MENU_PAGE - 1 - llGetListLength( PresetsNames ) % MENU_PAGE;
                integer i;

                for( i=0; i<n; i++ )
                    PresetsNames = (PresetsNames=[]) + PresetsNames + " ";

                if( TRACE )
                    show_channels();
                set_channel_index( 0 );
                indicate_music_stopped();
                state Stopped;
            }
        }
    }

    timer(){
        llSetTimerEvent( 0 );
    }

    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }

    on_rez( integer param ){
        llResetScript();
    }
}

///////////////////////////////////////////////////////////////
// Primary App Operational States
///////////////////////////////////////////////////////////////

state Stopped {

    state_entry(){
        llListen( RADIO_CHAN, "", NULL_KEY, "" );
    }

    touch_start( integer num ){
        state Playing;
    }

    timer(){
        if( TRACE )
            llSay( 0, "Stopped.timer" );
        llSetTimerEvent( 0 );
        llSetParcelMusicURL( "" );
    }

    listen( integer chan, string name, key sender, string message ){
        if( handle_message( chan, name, sender, message ) == DO_PLAY )
            state Playing;
    }

    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }

    on_rez( integer param ){
        llResetScript();
    }
}


state Playing {

    state_entry(){
        llListen( RADIO_CHAN, "", NULL_KEY, "" );
        llListen( DLG_CHAN, "", NULL_KEY, "" );
        play_music();
    }

    state_exit(){
    }

    touch_start( integer num ){
        show_dialog( llDetectedKey( 0 ));
    }

    listen( integer chan, string name, key sender, string message ){
        integer code = handle_message( chan, name, sender, message );

		if( code == DO_STOP ){
			stop_music();
            state Stopped;

		} else if( code	== DO_SUSPEND ){
            state Stopped;

		} else
			play_music();
    }

    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }

    on_rez( integer param ){
        llResetScript();
    }
}


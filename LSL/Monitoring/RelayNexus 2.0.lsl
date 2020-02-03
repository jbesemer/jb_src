/////////////////////////////////////////////////////////////////
// Relay Nexus -- listen to security sensor and relay commands at state changes
/////////////////////////////////////////////////////////////////

// constants

string VERSION = "1.1";

// commands from sensors

string RELAY_OWNER_HERE = "here";
string RELAY_OWNER_GONE = "gone";

// section names

string SECTION_OWNER_HERE = "owner.here";
string SECTION_OWNER_GONE = "owner.gone";

// encoding of commands for communications

string SAY_REGION   = "regionsay";
string SAY_OWNER    = "ownersay";
string SAY_SAY      = "say";
string SAY_SHOUT    = "shout";
string SAY_WHISPER  = "whisper";

list COMM_CMDS = [ SAY_OWNER, SAY_REGION, SAY_SAY, SAY_SHOUT, SAY_WHISPER ];



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



/////////////////////////////////////////////////////////////////
// reading config files
/////////////////////////////////////////////////////////////////

// Config vars

integer RELAY_CHAN = -50012;

float GRACE_PERIOD = 5.0;   // number of sec. to wait before arming system

integer TRACE = 0;      // issue trace messages for each actual outgoing message

// strip comments and extraneous whitespace

string strip_comments( string data ){
    integer pos = llSubStringIndex( data, "#" );
    if( pos >= 0 )
        data = llDeleteSubString( data, pos, -1 );
    return llStringTrim( data, STRING_TRIM );
}

// parse a line of config file

parse_config_line( string data ){
    string Data = data;     // keep copy for err messages

    // strip comments, leading and trailing whitespace, and ignore blank lines
    data = strip_comments( data );
    if( data == "" )
        return;
    
    // parse individual config settings

    if( llSubStringIndex( data, ":" ) >= 0 ){
        list tmp = llParseString2List( data, [":"], []);
        string setting = llToUpper( llStringTrim( llList2String( tmp, 0 ), STRING_TRIM ));
        string value = llToUpper( llStringTrim( llList2String( tmp, 1 ), STRING_TRIM ));

        if( setting == "RELAY_CHAN" )           RELAY_CHAN = (integer)value;
        else if( setting == "GRACE_PERIOD" )    GRACE_PERIOD = (float)value;
        else if( setting == "TRACE" )           TRACE = (integer)value;
        else
            llSay( 0, "Ignoring: " + Data );
    } else
        llSay( 0, "Missing ':' in: " + Data );
}

show_config(){
    llSay( 0, "RelayNexus Config..." );
    llSay( 0, "RELAY_CHAN: " + (string)RELAY_CHAN );
    llSay( 0, "GRACE_PERIOD: " + (string)GRACE_PERIOD );
    llSay( 0, "...END" );
}


// stored commands

// parse a line of command file
//
// format is...
//
//  name = value        # remember a symbolic name for a channel or message
//  [who.what]          # start a section to be acted upon when 'who' does 'what'
//  how, channel, message    # how and where to send message when 'who' does 'what'

string CurrentSectionName = "";     // name of current section

list Commands = [];             // acumulated list of commands

// mapping of name,value pairs

list Names = [];
list Values = [];

// remember a name,value pair

define_name( name, value ){
    // new names go on front of list, thus (innefficiently and sliently) overriding previous defs
    Names = (( Names = []) + [ llStringTrim( name, STRING_TRIM )] + Names );
    Values = (( Values = []) + [ llStringTrim( value, STRING_TRIM )] + Values );
}

// map name to value if possible, else return name

string substitute_value( string name ){
    integer index = llListFindList( Names, [ name ]);
    
    if( index >= 0 )
        return llList2String( Values, index );
    else
        return name;
}

parse_command_line( string data ){
    string Data = data;     // keep copy for err messages

    // strip comments, leading and trailing whitespace, and ignore blank lines
    data = strip_comments( data );
    if( data == "" )
        return;
    
    // parse individual commands: three cases:
    
    // definitions
    
    if( llSubStringIndex( data, "=" ) >= 0 ){
        list tmp = llParseString2List( data, ["="], []);
        define_name( llList2String( tmp, 0 ), llList2String( tmp, 1 ));
    }
    
    // section names
    
    else
    if( llSubStringIndex( data, "[" ) == 1 && llSubStringIndex( data, "]" ) == llStringLength( data ) - 1 ){
        CurrentSectionName = llGetSubString( 1, -2 );
    }
    
    // messages to send
    
    else
    if( llSubStringIndex( data, "," ) >= 0 ){
        if( CurrentSectionName != "" ){
            list tmp = llParseString2List( data, [","], []);
            string how = llToLower( llStringTrim( llList2String( tmp, 0 ), STRING_TRIM ));
            integer whom;
            string what;

            int pos = llListFindList( COMM_CMDS, [ how ]);
            
            if( pos < 0 )
                llSay( 0, "Bad Command: " + how " -- in: " + Data );
            else if( how == SAY_OWNER ){
                what = substitute_value( llStringTrim( llList2String( tmp, 1 ), STRING_TRIM ));
                Commands = ((Commands=[]) + Commands + llList2CSV([ CurrentSectionName, how, what ]));
            } else {
                whom = (integer)substitute_value( llStringTrim( llList2String( tmp, 1 ), STRING_TRIM ));
                what = substitute_value( llStringTrim( llList2String( tmp, 2 ), STRING_TRIM ));
                Commands = ((Commands=[]) + Commands + llList2CSV([ CurrentSectionName, how, what, whom ]));    // note order change
            }

        } else
            llSay( 0, "Missing Section Name for command: " + Data );
    }
    
    // [error]
    else
        llSay( 0, "Bad Command: " + Data );

}

show_commands(){
    integer i, N;
    
    llSay( 0, "RelayNexus Definitions..." );

    N = llGetListLength( Names );
    for( i=0; i<N; i++ )
        llSay(0, Names[i] + " = " + Values[i]);
    
    llSay( 0, "RelayNexus Commands..." );

    string sect = "";
    N = llGetListLength( Commands );
    for( i=0; i<N; i++ ){
        list cmd = llCSV2List( llList2String( Commands, i ));
        string s = llList2String( cmd, 0 );
        if( sect != s ){
            sect = s;
            llSay( 0, "[" + sect + "]" );
        }
        llSay( 0, llList2SCV( llList2List( cmd, 1, -1 )));
    }
    
    llSay( 0, "...END" );
}


execute_commands( string section ){
    integer i, N = llGetListLength( Commands );
    
    for( i=0; i<N; i++ ){
        list command = llCSV2List( llList2String( Commands, i ));
        
        if( section == llList2String( command, 0 )){
            string how = llList2String( command, 1 );
            string what = llList2String( command, 2 );
            integer whom;
            
            if( TRACE )
                llSay( 0, "Executing: " + llList2CSV( command ));

            if( how != SAY_OWNER )
                whom = (integer)llList2String( command, 3 );

            if( how == SAY_OWNER )          llOwnerSay( what );
            else if( how == SAY_REGION )    llRegionSay( whom, what );
            else if( how == SAY_SAY )       llSay( whom, what );
            else if( how == SAY_SHOUT )     llShout( whom, what );
            else if( how == SAY_WHISPER )   llWhisper( whom, what );
            else
                llOwnerSay( "Cannot execute: " + how );
        }
    }
}



/////////////////////////////////////////////////////////////////
// principal actions
/////////////////////////////////////////////////////////////////

// schedule a set-secure event when grace period expires

prepare_to_set_secure(){
    llSetTimerEvent( GRACE_PERIOD );
}

// send set_secure messages

set_secure(){
    llSetTimerEvent( 0 );   // cancel any pending set_secure() events
    execute_commands( SECTION_OWNER_GONE );
}

// stand down from set secure

stand_down(){
    llSetTimerEvent( 0 );   // cancel any pending set_secure() events
    execute_commands( SECTION_OWNER_HERE );
}

//////////////////////////////////////////////////////////////////////
// init & read configs
//////////////////////////////////////////////////////////////////////

string  ConfigNotecardName = "Configuration";
string  CommandNotecardName = "Commands";

key     QueryId;
integer QueryIndex;

vector  ErrorColor      = <1,0,0>;
vector  GreenColor      = <0,1,0>;
float   TextAlpha       = 1.0;

default {
    state_entry(){
        llOwnerSay( "RelayNexus " + VERSION );
        llListen( RELAY_CHAN, "", NULL_KEY, "" );

        // remove any previous versions of this script
        llSetText( "Upgrading", ErrorColor, TextAlpha );
        upgrade();
      
        state ReadConfig;
    }

    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }
    
    on_rez( integer param ){
        llResetScript();
    }
}

state ReadConfig {
    state_entry(){
        llSetText( "Processing Config", ErrorColor, TextAlpha );
        // start reading the config file
        QueryIndex = 0;
        QueryId = llGetNotecardLine( ConfigNotecardName, QueryIndex ); 
    }
    
    dataserver( key queryId, string data ){
        if( queryId != QueryId )
            return;

        if( data == EOF ){
            show_config();
            state ReadCommands;
        }

        parse_config_line( data );

        QueryId = llGetNotecardLine( ConfigNotecardName, ++QueryIndex );
    }

    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }
    
    on_rez( integer param ){
        llResetScript();
    }
}

state ReadCommands {
    state_entry(){
        llSetText( "Processing Commands", ErrorColor, TextAlpha );

        // start reading the config file
        QueryIndex = 0;
        QueryId = llGetNotecardLine( CommandNotecardName, QueryIndex ); 
    }
    
    dataserver( key queryId, string data ){
        if( queryId != QueryId )
            return;

        if( data == EOF ){
            show_commands();
            state Running;
        }

        parse_command_line( data );

        QueryId = llGetNotecardLine( CommandNotecardName, ++QueryIndex );
    }

    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }
    
    on_rez( integer param ){
        llResetScript();
    }
}

//////////////////////////////////////////////////////////////////////
// normal running mode
//////////////////////////////////////////////////////////////////////

state Running
{
    state_entry(){
        llSetText( "", ErrorColor, TextAlpha );
        llOwnerSay( "RelayNexus " + VERSION + " Running..." );
    }
    
    touch_start(integer total_number){
        llOwnerSay( "RelayNexus " + VERSION + " Running..." );
    }

   listen( integer chan, string name, key id, string message ){
        if( chan != RELAY_CHAN )
            return;
        
        if( message == RELAY_OWNER_HERE ){
            stand_down();
            
        } else if( message == RELAY_OWNER_GONE ){
            prepare_to_set_secure();

        } else
            llOwnerSay( "Ignoring: " + message );
    }
    
    timer(){
        set_secure();
    }
    
    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }
    
    on_rez( integer param ){
        llResetScript();
    }
}

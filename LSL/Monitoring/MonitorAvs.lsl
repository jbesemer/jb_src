// colors for status info

vector  ErrorColor      = <1., 0., 0.>;
vector  YellowColor     = <1., 1., 0.2>;    // light hard yellow
vector  RedColor        = <1., 0., 0.>;
vector  GreenColor      = <0., 1., 0.>;
float   TextAlpha       = 1.0;

// separator between name and value in config files

string CONFIG_SEP       = "=";    

integer TRACE = 1;
integer TESTING = 1;
integer RETRY_COUNT_MAX = 3;
integer REPEAT_INTERVAL = 360;


list Names = [];    // list of names to scan for
list Keys = [];     // list of keys corresponding to the names
list Online = [];   // online/offline status of corresponding name
list QID = [];      // current outstanding QuereyID for corresponding name
list Times = [];

integer NameCount = 0;
integer KeyIndex;
integer RetryCount;

string  QueryNotecardName = "Configuration";
integer QueryIndex;
key     QueryId;

// functions

AddKey( string k )
{
    // 00000000-0000-0000-0000-000000000000
    llOwnerSay( k + " is " + llList2String( Names, KeyIndex ));
    Keys += [ (key)k ];
    Online += [ -1 ];
    QID += [ NULL_KEY ];
    Times += [ "" ];
}

AddName( string name )
{
    Names += [ llStringTrim( name, STRING_TRIM )];
    NameCount = llGetListLength( Names );
}

AddNames( list names )
{
    integer N = llGetListLength( names );
    integer i;
    
    for( i=0; i<N; i++ )
        AddName( llList2String( names, i ));
}

string strip_comments( string data ){
    integer pos = llSubStringIndex( data, "#" );
    
    if( pos >= 0 )
        data = llDeleteSubString( data, pos, -1 );
        
    return llStringTrim( data, STRING_TRIM );
}

string NAME2KEY_URL = "http://w-hat.com/name2key";
key reqid;

lookup_key( string name )
{
    reqid = llHTTPRequest( 
        NAME2KEY_URL
            + "?terse=1&name=" 
            + llEscapeURL( name ), 
        [], 
        "" );
}

lookup_key_index( integer index )
{
    KeyIndex = index;
    RetryCount = 0;
    lookup_key( llList2String( Names, index ));
}

retry_lookup_key()
{
    lookup_key( llList2String( Names, KeyIndex ));
}

updateOnline( key qid, integer data)
{
    integer N = llListFindList( QID, [ qid ]);
    
    if( N >= 0 ){
        string ts = llGetTimestamp();
        // integer WasOnline = llList2Integer( Online, N );
        Online = llListReplaceList( Online, [ data ], N, N );
        Times = llListReplaceList( Times, [ ts ], N, N );
    }
}

queueRequests()
{
    integer i;
    
    // llOwnerSay( "Making Requests" );
    for( i=0; i < NameCount; i++ ){
        string uuid = llList2String( Keys, i );
        key qid = llRequestAgentData((key)uuid, DATA_ONLINE ); // 0.1 sec delay
        QID = llListReplaceList( QID, [ qid ], i, i );
    }
    // llOwnerSay( "Requests Made" );
}

key http_request_id;
string UPDATE_URL = "http://cascade-sys.com/cgi-bin/avatar.cgi";

SubmitUpdate()
{
    integer i;
    string body = "";
    
    for( i=0; i < NameCount; i++ )
    {
        string varname = llList2String(Names,i);
        string varvalue = (string)llList2Integer(Online,i) + "," + llList2String( Times, i );
        
        Trace( varvalue + " " + varname  );
        
        if( i > 0 ) 
            body+="&";
        body += llEscapeURL( varname ) + "=" + llEscapeURL( varvalue );
    }

    // Trace( body );

    if( !TESTING )
        http_request_id 
            = llHTTPRequest(
                UPDATE_URL, 
                [ HTTP_METHOD, "POST", 
                    HTTP_MIMETYPE, "application/x-www-form-urlencoded" ],
                body);
}

Say( string msg )
{
    llOwnerSay( msg );
}

Trace( string msg )
{
    if( TRACE )
        Say( msg );
}


// default/startup state ////////////////////////////////////////

default 
{
    state_entry()
    {
        state ReadConfig;
    }
    
    state_exit(){
        Say( "Initial Free Memory: " + (string)llGetFreeMemory());
    }
}

// ReadConfig state //////////////////////////////////////////

state ReadConfig {
    state_entry(){
        Say( "ReadConfig" );
        llSetText( "Processing Config", YellowColor, TextAlpha );

        // start reading the config file

        QueryIndex = 0;
        QueryId = llGetNotecardLine( QueryNotecardName, QueryIndex );
        
    }
    
    dataserver( key queryId, string data ){
        if( queryId != QueryId )
            return;

        if( data == EOF )
            state LookupKeys;
        
        string Data = data;     // keep copy for err messages

        // strip comments, leading and trailing whitespace, and ignore blank lines
        data = strip_comments( data );
        if( data != "" ){
        
            // parse individual config settings

            if( llSubStringIndex( data, CONFIG_SEP ) >= 0 ){
                list tmp = llParseString2List( data, [CONFIG_SEP], []);
                string setting = llToUpper( llStringTrim( llList2String( tmp, 0 ), STRING_TRIM ));
                string value = llList2String( tmp, 1 );
                
                Trace( setting + " -> " + value );

                    if( "TRACE" == setting )    
                        TRACE = (integer)value;
                
                else if( "TESTING" == setting )    
                        TESTING = (integer)value;
                
                else if( "RETRY_COUNT_MAX" == setting )    
                        RETRY_COUNT_MAX = (integer)value;
                
                else if( "REPEAT_INTERVAL" == setting )    
                        REPEAT_INTERVAL = (integer)value;
                
                else if( "NAME" == setting || "NAMES" == setting )
                    AddNames( llCSV2List( value ));

                else
                    Say( "Config:Ignoring: " + Data );
            } else
                Say( "Config:Missing '" + CONFIG_SEP + "' in: " + Data );
        }

        // fetch next config file line
        
        QueryId = llGetNotecardLine( QueryNotecardName, ++QueryIndex );
    }

    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }

    on_rez( integer param ){
        llResetScript();
    }
}

// LookupKeys state //////////////////////////////////////////

state LookupKeys {
    state_entry() {
        Say( "LookupKeys" );
        llSetText( "Looking Up Keys", YellowColor, TextAlpha );
        lookup_key_index( 0 );
    }

    http_response(key id, integer status, list meta, string body) {
        if ( id != reqid )
            return;
        
        if ( status == 200 ){
            AddKey( body );
        
        } else if( RetryCount++ < RETRY_COUNT_MAX ){
            retry_lookup_key();
            return;
        }
        
        if( KeyIndex < NameCount - 1 )
            lookup_key_index( KeyIndex + 1 );
        else
            state Running;
    }

    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }

    on_rez( integer param ){
        llResetScript();
    }
}
  
// Running State //////////////////////////////////////////////

state Running 
{
    state_entry()
    {
        llSetText( "Running", GreenColor, TextAlpha );
        Say( "Running Free Memory: " + (string)llGetFreeMemory());

        llSetTimerEvent( REPEAT_INTERVAL );
        queueRequests();
    }
    
    timer()
    {
        SubmitUpdate();
        queueRequests();
    }
    
    dataserver(key queryid, string data)
    {
        updateOnline( queryid, (integer)data );
    }
    
    touch_end( integer num )
    {
//         showAllStatus();
    }

    changed( integer change ){
        if( change&CHANGED_INVENTORY )
            llResetScript();
    }

    on_rez( integer param ){
        llResetScript();
    }
}

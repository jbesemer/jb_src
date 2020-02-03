string namekey = "634cd054-0a52-4e46-85f1-bf97162ee9c8"; //Hiroshi Sakai

// http://w-hat.com/name2key

list Data = [ // name, key
    "Annamaria Ansar", "c725b4af-2dad-4430-840f-c921bd93cee3",
    "Bluebell March", "eb96f339-9a5d-4768-8ceb-0f26784a8ba7",
    "Callipygian Christensen", "11faf113-6003-424a-8d0f-4ce83d49e251",
    "Cellandra Zon", "cf9dea89-62af-4acc-b816-884509b31634",
    "Doreen Halley", "a889b0c7-5b46-4cc3-bc70-902ec38d7823",
    "Glory Aristocrat", "318b21a1-b115-4ca3-be7a-6542d16ba6c1",
    "Lash Xevious", "b2e09408-541f-42b2-8def-03686f21f0da",
    "Mariposa Rayna", "820aef01-0a2a-4d5f-8316-d9ea191516bc",
    "Noma Falta", "79707e47-3848-4a43-b4cf-01a76b6d1662",
    "Petal Sands", "74ba2480-a454-49e9-8936-e68e47d96c8f",
    "Phacelia Furse", "7b4d75d3-5412-4e84-8cfa-60c69bd113a5",
    "Shazuka Tigerpaw", "feca8c03-d9bf-4e99-bbc1-8588a31b8fc7",
    "Skyler Barrymore", "9c4675e2-b108-486f-b8b6-1ee80221deb2",
    "Sundra Petrov", "47ff8727-f020-4551-889e-957a7853976a"
    ];

integer DataLen;
integer DataCount;
list Online;
list QID;

vector  TextColor       = <1,1,1>;
vector  ErrorColor      = <1,0,0>;
vector  GreenColor      = <0,1,0>;
float   TextAlpha       = 1.0;

showAllOnlineFriends()
{
    string friends = "";
    string sep = "";
    integer i;
    
    for( i=0; i < DataCount; i++ ){
        integer isOnline = llList2Integer( Online, i );
        if( isOnline ){
            string name = llList2String( Data, i*2 );
            friends += sep + name;
            sep = "\n";
        }
    }

    llSetText( 
        friends,
        TextColor, 
        TextAlpha );
}

showStatus( integer index, integer isOnline )
{
    string name = llList2String( Data, index*2 );
    if( isOnline )
        llOwnerSay( "ONline:" + name  );
    else
        llOwnerSay( "OFFline:      " + name );
}

showAllStatus()
{
    integer i;
    
    for( i=0; i < DataCount; i++ ){
        showStatus( i, llList2Integer( Online, i ));
    }
    //         llSetText( "Now Playing:\n" 
}

updateOnline( key qid, integer data)
{
    integer N = llListFindList( QID, [ qid ]);
    
    if( N >= 0 ){
        integer WasOnline = llList2Integer( Online, N );
        Online = llListReplaceList(Online, [data], N, N );
        if( WasOnline != data ){
            showStatus( N, data );
            showAllOnlineFriends();
        }
    }
}

queueRequests()
{
    integer i;
    
    // llOwnerSay( "Making Requests" );
    for( i=0; i < DataCount; i++ ){
        integer j = i*2;
        string uuid = llList2String( Data, j+1 );
        key qid = llRequestAgentData((key)uuid, DATA_ONLINE); // 0.1 sec delay
        QID = llListReplaceList( QID, [ qid ], i, i );
    }
    // llOwnerSay( "Requests Made" );
}

default 
{
    state_entry()
    {
        DataLen = llGetListLength( Data );
        DataCount= DataLen / 2;
        integer i;
        
        Online = [];
        QID = [];
        for( i=0; i < DataCount; i++ ){
            Online += [ 0 ];
            QID += [ 0 ];
        }
        
        llSetTimerEvent(5);
    }
    
    timer()
    {
        queueRequests();
    }
    
    dataserver(key queryid, string data)
    {
        updateOnline( queryid, (integer)data );
    }
    
    touch_end( integer num )
    {
        showAllStatus();
    }
}

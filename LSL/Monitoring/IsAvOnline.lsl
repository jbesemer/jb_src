string namekey = "b2e09408-541f-42b2-8def-03686f21f0da"; //Lash Xevious

default 
{
    state_entry()
    {
        llSetTimerEvent(5);  //check for online status every 5 seconds
    }
    timer()
    {
        llRequestAgentData((key)namekey, DATA_ONLINE); // request whether agent is online
    }
    
    dataserver(key queryid, string data)   //when data from RequestAgentData is available, do this
    {
        vector colour;
        if((integer)data==1){
            if (llGetAgentInfo((key)namekey) & AGENT_AWAY){
                colour = <0.5, 0.5, 0.0>;  //yellow colour if agent is offline
            }
            else if (llGetAgentInfo((key)namekey) & AGENT_BUSY){
                colour = <0.0, 0.0, 0.5>;  //blue colour if agent is offline
            }
            else{
                colour = <0.0, 0.5, 0.0>;  //green colour if agent is offline
            }
        }else{
            colour = <0.5, 0.0, 0.0>;  //red colour if agent is offline
        }
        llMessageLinked(LINK_ALL_CHILDREN, 0, (string)colour, NULL_KEY); //send colour to each of the two heart
    }
}
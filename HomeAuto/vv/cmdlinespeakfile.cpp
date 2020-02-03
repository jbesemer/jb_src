/****************************************************************************/
/*                                                                          */
/* IBM Confidential                                                         */
/* OCO Source Materials                                                     */
/* 11K6192  V2.1                                                            */
/* Copyright IBM Corp.  1998, 2000                                          */
/*                                                                          */
/* The source code for this program is not published or otherwise           */
/* divested of its trade secrets, irrespective of what has been deposited   */
/* with the U.S. Copyright Office.                                          */
/*                                                                          */
/****************************************************************************/

/****************************************************************************/
/*                                                                          */
/* IBM Confidential                                                         */
/* OCO Source Materials                                                     */
/* 11K6192  V2.1                                                            */
/* Copyright IBM Corp.  1998, 2000                                          */
/*                                                                          */
/* The source code for this program is not published or otherwise           */
/* divested of its trade secrets, irrespective of what has been deposited   */
/* with the U.S. Copyright Office.                                          */
/*                                                                          */
/****************************************************************************/


// Sample application to read in a filename from the command line, open it and synthesize
// the text.
//
// Included in this directory is a file containing sample text: american-voices-eci.txt

#include <stdio.h>
#include <iostream.h>
#include <fstream.h>
#include <string.h>
#include <memory.h>
#include <eci.h>


int main (int argc, char * argv[])
{
  ECIHand hECI;
  char buff[200];
  int ret;
  FILE* fin;

  if( argc < 2 ){
      cout << "Usage: " << argv[0] << " <filename to output>" << endl;
      return 1;
  } 

  // open file
  if( strcmp( argv[ 1 ], "-" ) == 0 ){
    fin = stdin;

  } else {
    fin = fopen( argv[ 1 ], "r" );

    // check to see if file opened properly
    if( !fin ){
        // output error message and die
        cerr << "Couldn't open " << argv[1] << endl;
        return 1;
    }
  }

  // Create the ECI Instance
  hECI = eciNew();

  // You may define FILEOUTPUT in the Makefile to output sound to a file
#ifdef FILEOUTPUT
  // set Output to file - and set filename to "temp.au"
  ret=eciSetOutputFilename(hECI,"temp.au");
  if( ret != 1 )
  	cout << "ret=" << ret << " from eciSetOutputFilename" << endl;
#else
  // This section produces output to the default sound device
  ret=eciSetOutputDevice(hECI, 0);
  if( ret != 1 )
  	cout << "ret=" << ret <<" from eciSetOutputDevice" << endl;
#endif

  // Set engine to parse annotated text
  ret=eciSetParam(hECI,eciInputType,1);

  // Loop to end of file
  while( fgets( buff, sizeof( buff ), fin )){
      // echo line to screen
      cout << buff << endl;

      // add the text to the Synthesis Engine
      ret=eciAddText(hECI,buff);
      if( ret != 1 )
      	cout << "ret=" << ret << " from eciAddText" << endl;
    }

  // Synthesize the text
  ret=eciSynthesize(hECI);
  if( ret != 1 )
  	cout << "ret=" << ret << " from eciSynthesize" << endl;

  // Synchronize. This will wait until synthesis completes
  ret=eciSynchronize(hECI);
  if( ret != 1 )
  	cout << "ret=" << ret << "from eciSynchronize" << endl;


  // Delete the instance
  eciDelete(hECI);

  return 0;

}






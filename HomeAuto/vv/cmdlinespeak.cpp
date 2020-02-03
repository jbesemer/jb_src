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


// Application to Output text from the command line

#include <stdio.h>
#include <string.h>
#include <memory.h>
#include "eci.h"


int main (int argc, char * argv[])
{
  int ret;
  char *ptr;
  ECIHand hECI;

  // if no arguments output usage instructions
  if(argc<2)
    {
      printf("Usage: %s <Text to speak>\n",argv[0]);
      return 0;
    }

  // create a new ECI instance
  hECI = eciNew();
  if ( NULL_ECI_HAND == hECI )
  {
	printf( "Could not create ECI handle. Check installation.\n" );
	printf( "Possible causes:\n" );
	printf( "\tIBM ViaVoice TTS RTK has not been installed on this machine.\n" );
	printf( "\tno exported ECIINI variable in /etc/profile.\n" );
	printf( "\teci.ini file not in path referenced by ECIINI, nor in current directory.\n" );
	printf( "\teci.ini corrupted.\n" );
	printf( "\tlibrary /usr/lib/libibmeci50.so corrupted or missing.\n" );
	printf( "\tlanguage files referenced in eci.ini file corrupted or missing.\n" );
	printf( "Re-install IBM ViaVoice TTS RTK.\n" );
	return -1;
  }

#ifdef FILEOUTPUT
  // output to file - set name to temp.au
  ret=eciSetOutputFilename(hECI,"temp.au");
  if( ret != 1 )
  	printf ("ret=%d  from eciSetOutputFilename\n",ret);
#else
  // output to device - default device is 0
  ret=eciSetOutputDevice(hECI, 0);
  if( ret != 1 )
  	printf ("ret=%d  from eciSetOutputDevice\n",ret);
#endif

  // set engine to parse annotated text
  ret=eciSetParam(hECI,eciInputType,1);

  int i=0;

  // loop through arguments
  for(i=1;i<argc;i++)
    {

      // ignore any empty arguments
      if(strlen(argv[i])<=0)
        continue;

      // echo arguments to command line
      printf("i=%d,%s\n",i,argv[i]);
      ptr=argv[i];

      // Add text to engine
      ret=eciAddText(hECI,ptr);
      if( ret != 1 )
      	printf ("ret=%d  from eciAddText\n",ret);
    }

  // Begin synthesis of Text
  ret=eciSynthesize(hECI);
  if( ret != 1 )
  	printf ("ret=%d  from eciSynthesize\n",ret);

  // Synchronize. This will wait until all text is processed.
  ret=eciSynchronize(hECI);
  if( ret != 1 )
  	printf ("ret=%d  from eciSynchronize\n",ret);

  // Delete the instance
  eciDelete(hECI);

  return 0;
}




//	Filename:	usbcode.cpp
//	Birth:		7/16/99
//	Author:		Doug Lovett
//	Delcom Engineering  - Copyright 2000
//	


// Includes
#include <afxwin.h>
#include <afxcmn.h>
#include <iostream.h>
#include <afxtempl.h>
#include <objbase.h>
#include <setupapi.h>		// You must Manually add the setupapi.lib to the project library link tab!
#include "devioctl.h"		// This header file is proved by MS, with the DDK

#include <initguid.h>
#include "UsbCode.h"




// {59BD73A6-822E-4684-9530-0754FE897113}	// DELCOM
DEFINE_GUID(USBDELVI_GUID, 0x59bd73a6, 0x822e, 0x4684, 0x95, 0x30, 0x7, 0x54, 0xfe, 0x89, 0x71, 0x13);

// {CEF084F3-4591-4995-AE59-A4258007E043}	// LINDWALL
//DEFINE_GUID(USBDELVI_GUID, 0xcef084f3, 0x4591, 0x4995, 0xae, 0x59, 0xa4, 0x25, 0x80, 0x7, 0xe0, 0x43);

// ECI-alerter GUID
//DEFINE_GUID(USBDELVI_GUID, 
//0x314DA3F1, 0xFA86, 0x4830, 0xB0, 0x2A, 0xB2, 0x12, 0x06, 0xC8, 0xBD, 0x01);



#define USBIO_IOCTL_VENDOR_INDEX		0x0800	

#define IOCTL_USBIO_SEND_PACKET    CTL_CODE(FILE_DEVICE_UNKNOWN,  \
										   USBIO_IOCTL_VENDOR_INDEX+10,\
		                                   METHOD_BUFFERED,  \
										   FILE_ANY_ACCESS)




// CUsbCode Object Functions

CUsbCode::CUsbCode()		// Constructor
{
	hUsb = NULL;		// handle to the main usb pipe
}

	
// Scans for all the device that match the GUID passed.
// returns an array of cStrings, containing the device names found, 
// and returns the number of device names found. Returns zero if no
// devices found.
int	CUsbCode::Scan(CString * Devices)	
{
	
	// Get handle to the devices manager
	HDEVINFO  hInfo = SetupDiGetClassDevs((LPGUID)&USBDELVI_GUID, NULL, NULL,
	                                     DIGCF_PRESENT |  DIGCF_INTERFACEDEVICE);

    if (hInfo == INVALID_HANDLE_VALUE)		// check for error
		return(0);
	

	for (DWORD i=0; ; ++i)					// loop till all devices are found
		{
		SP_INTERFACE_DEVICE_DATA Interface_Info;			// declare structure
		Interface_Info.cbSize = sizeof(Interface_Info);		// Enumerate device
		if (!SetupDiEnumInterfaceDevice(hInfo, NULL, (LPGUID) &USBDELVI_GUID,i, &Interface_Info))
			{
			SetupDiDestroyDeviceInfoList(hInfo);
			return(i);
			}
	
		DWORD needed;										// get the required lenght
		SetupDiGetInterfaceDeviceDetail(hInfo, &Interface_Info, NULL, 0, &needed, NULL);
		PSP_INTERFACE_DEVICE_DETAIL_DATA detail = (PSP_INTERFACE_DEVICE_DETAIL_DATA) malloc(needed);
		if (!detail)
			{  
			SetupDiDestroyDeviceInfoList(hInfo);
			return(i);
			}
															// fill the device details
		detail->cbSize = sizeof(SP_INTERFACE_DEVICE_DETAIL_DATA);
		if (!SetupDiGetInterfaceDeviceDetail(hInfo, &Interface_Info, detail, needed,NULL, NULL))
			{
			free((PVOID) detail);
			SetupDiDestroyDeviceInfoList(hInfo);
			return(i);
			}

		char name[MAX_PATH];
		strncpy(name, detail->DevicePath, sizeof(name));	// copy the device name
		free((PVOID) detail);								// free the mem
		Devices[i] = name;									// save device name
			
	}  // end of for loop
}

// Open the device with the given device name
bool CUsbCode::Open(CString DeviceName)
{
	// Create the handle to our device
	hUsb = CreateFile(DeviceName,
			GENERIC_READ | GENERIC_WRITE, 0, NULL, OPEN_EXISTING, 0, NULL);

    if( hUsb == INVALID_HANDLE_VALUE )	// process error 
		{
		hUsb = 0;
		LPVOID lpMsgBuf;
		FormatMessage(
			FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
			NULL, GetLastError(),
			MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), // Default language
		    (LPTSTR) &lpMsgBuf, 0, NULL );
		// Display the string.
		MessageBox(NULL,(LPTSTR)lpMsgBuf,"Failed to open Device",MB_ICONHAND);		
		LocalFree( lpMsgBuf );  // Free the buffer.
		return(FALSE);
		}
	
	return(TRUE);		// returns True on success
		
}


// Close the device,
int CUsbCode::Close()
{	

	if( hUsb )	{
		if( CloseHandle( hUsb) )			// close the handle to our device
			{
			hUsb=0;
			return(1);
			}
		else
			{
			LPVOID lpMsgBuf;
			FormatMessage(
				FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
				NULL, GetLastError(),
				MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), // Default language
				(LPTSTR) &lpMsgBuf, 0, NULL );
			// Display the string.
			MessageBox(NULL,(LPTSTR)lpMsgBuf,"Failed to close Device",MB_ICONHAND);		
			LocalFree( lpMsgBuf );  // Free the buffer.
			hUsb=0;
			}
		}
	return 0;
}

// Send the USBIODS packet to the USB Device & returns data if available.
int CUsbCode::SendPacket( pPacketStruct pPacket )
{
	unsigned long nBytes;	
	BOOLEAN success;	

	if(!hUsb)	{
		MessageBox(NULL,"Device not open!","SendPacket Failed!",MB_ICONHAND);
		return(0);
		}

	pPacket->Recipient	= 8;		// Always 8 for the USBIODS device
	pPacket->DeviceModel= 18;		// Always 18 for the USBIODS device
	
	success = DeviceIoControl(hUsb,			// call the send packet function
              IOCTL_USBIO_SEND_PACKET,
              pPacket, 8+pPacket->Length, pPacket, 8, &nBytes, NULL );
 
	if( !success )	
		{
		LPVOID lpMsgBuf;
		FormatMessage(
			FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
			NULL, GetLastError(),
			MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), // Default language
		    (LPTSTR) &lpMsgBuf, 0, NULL );
		Close();		// Close before displaying message otherwise the timer will try another command
		// Display the string.
		MessageBox(NULL,(LPTSTR)lpMsgBuf,"Failed to send USBIODS packet!",MB_ICONHAND);		
		LocalFree( lpMsgBuf );  // Free the buffer.
		return(0);
		}

	return(1);
}



void CUsbCode::LED(int Color, int Mode)
{
		
	if(IsOpen())
	{
		if( Mode == 1)	// Is mode equals ON
		{	
			// first turn off flash mode
			Packet.Recipient = 8;
			Packet.DeviceModel = 18;
			Packet.Length = 0;
			Packet.MajorCmd = 10;
			Packet.MinorCmd = 20;
			switch(Color) {
				case GREENLED	: Packet.DataLSB = 1; break;
				case REDLED		: Packet.DataLSB = 2; break;
				case BLUELED	: Packet.DataLSB = 4; break;
			}
			Packet.DataMSB = 0;
			SendPacket(&Packet);

			// Then turn the LED on
			Packet.Recipient = 8;
			Packet.DeviceModel = 18;
			Packet.Length = 0;
			Packet.MajorCmd = 10;
			Packet.MinorCmd = 12;
			switch(Color) {
				case GREENLED	: Packet.DataLSB = 1; break;
				case REDLED		: Packet.DataLSB = 2; break;
				case BLUELED	: Packet.DataLSB = 4; break;
			}
			Packet.DataMSB = 0;
			SendPacket(&Packet);
		}

		else			// Mode is OFF or flash. Either way turn off the led and the flash.
		{
			// first turn off flash mode
			Packet.Recipient = 8;
			Packet.DeviceModel = 18;
			Packet.Length = 0;
			Packet.MajorCmd = 10;
			Packet.MinorCmd = 20;
			switch(Color) {
				case GREENLED	: Packet.DataLSB = 1; break;
				case REDLED		: Packet.DataLSB = 2; break;
				case BLUELED	: Packet.DataLSB = 4; break;
			}
			Packet.DataMSB = 0;
			SendPacket(&Packet);

			// Then turn the LED off
			Packet.Recipient = 8;
			Packet.DeviceModel = 18;
			Packet.Length = 0;
			Packet.MajorCmd = 10;
			Packet.MinorCmd = 12;
			Packet.DataLSB = 0;
			switch(Color) {
				case GREENLED	: Packet.DataMSB = 1; break;
				case REDLED		: Packet.DataMSB = 2; break;
				case BLUELED	: Packet.DataMSB = 4; break;
			}
			SendPacket(&Packet);


		}

		
		if( Mode == 2 )	// Flash mode.
		{
			// Then turn the LED off
			Packet.Recipient = 8;
			Packet.DeviceModel = 18;
			Packet.Length = 0;
			Packet.MajorCmd = 10;
			Packet.MinorCmd = 20;
			Packet.DataLSB = 0;
			switch(Color) {
				case GREENLED	: Packet.DataMSB = 1; break;
				case REDLED		: Packet.DataMSB = 2; break;
				case BLUELED	: Packet.DataMSB = 4; break;
			}
			SendPacket(&Packet);
		}
	}
}

int CUsbCode::ReadSerialNumber()
{
	if(IsOpen() )
	{
		Packet.Recipient = 8;
		Packet.DeviceModel = 18;
		Packet.Length = 0;
		Packet.MajorCmd = 11;
		Packet.MinorCmd = 10;
		Packet.DataLSB = 0;
		Packet.DataMSB = 0;
		SendPacket(&Packet);
	}
	return((*(unsigned int*)&Packet));
	

}

int CUsbCode::ReadVersionNumber()
{	
	if(IsOpen() )
	{
		Packet.Recipient = 8;
		Packet.DeviceModel = 18;
		Packet.Length = 0;
		Packet.MajorCmd = 11;
		Packet.MinorCmd = 10;
		Packet.DataLSB = 0;
		Packet.DataMSB = 0;
		SendPacket(&Packet);
	}
	return((unsigned int)Packet.DataLSB);
	
}



int CUsbCode::GetButtonStatus()
{
	if(IsOpen() )
	{
		Packet.Recipient = 8;
		Packet.DeviceModel = 18;
		Packet.Length = 0;
		Packet.MajorCmd = 11;
		Packet.MinorCmd = 0;
		Packet.DataLSB = 0;
		Packet.DataMSB = 0;
		SendPacket(&Packet);
		if(Packet.Recipient & 0x01)
			return(0);
		else
			return(1);
	}
	return(0);

}

void CUsbCode::LoadLedFreqDuty(char Color, char High, char Low)
{
	if(IsOpen() )
	{
			Packet.Recipient = 8;
		Packet.DeviceModel = 18;
		Packet.Length = 0;
		Packet.MajorCmd = 10;
		Packet.MinorCmd = 21+Color;
		Packet.DataLSB = Low;
		Packet.DataMSB = High;
		SendPacket(&Packet);
	}
}

void CUsbCode::LoadPreScalar(char PreScalar)
{
	if(IsOpen() )
	{
		Packet.Recipient = 8;
		Packet.DeviceModel = 18;
		Packet.Length = 0;
		Packet.MajorCmd = 10;
		Packet.MinorCmd = 19;
		Packet.DataLSB = PreScalar;
		Packet.DataMSB = 0;
		SendPacket(&Packet);
	}
}

void CUsbCode::SyncLeds()
{
	if(IsOpen() )
	{
		Packet.Recipient = 8;
		Packet.DeviceModel = 18;
		Packet.Length = 0;
		Packet.MajorCmd = 10;
		Packet.MinorCmd = 25;
		Packet.DataLSB = 0x07;	// sync all three leds 
		Packet.DataMSB = 0x00;	// preload to off
		SendPacket(&Packet);
	}
}

void CUsbCode::LoadInitialPhaseDelay(char Color, char Delay)
{
	if(IsOpen() )
	{
		Packet.Recipient = 8;
		Packet.DeviceModel = 18;
		Packet.Length = 0;
		Packet.MajorCmd = 10;
		Packet.MinorCmd = 26+Color;
		Packet.DataLSB = Delay;
		Packet.DataMSB = 0;
		SendPacket(&Packet);
	}
}





int CUsbCode::IsOpen()
{
	if(hUsb) return(1);
	else	 return(0);
}


void CUsbCode::Buzzer(uchar Mode, uchar Freq, uchar Repeat, uchar OnTime, uchar OffTime)
{
	if(IsOpen() )
	{
		Packet.Recipient = 8;
		Packet.DeviceModel = 18;
		Packet.Length = 8;
		Packet.MajorCmd = 10;
		Packet.MinorCmd = 70;
		Packet.DataLSB = Mode;
		Packet.DataMSB = Freq;
		Packet.ExtData[0] = Repeat;
		Packet.ExtData[1] = OnTime;
		Packet.ExtData[2] = OffTime;
		SendPacket(&Packet);
	}
}

void CUsbCode::EnableAutoClear(int Mode)
{
	if(IsOpen() )
	{

		// first make sure the button pin interrupt is enabled
		Packet.Recipient = 8;
		Packet.DeviceModel = 18;
		Packet.Length = 0;
		Packet.MajorCmd = 10;
		Packet.MinorCmd = 38;
		Packet.DataLSB = 0x01;		// enabled on pin P0.0
		Packet.DataMSB = 0x00;
		SendPacket(&Packet);


		Packet.Recipient = 8;
		Packet.DeviceModel = 18;
		Packet.Length = 0;
		Packet.MajorCmd = 10;
		Packet.MinorCmd = 72;
		if(Mode) {
			Packet.DataLSB = 0x00;
			Packet.DataMSB = 0x40;
		}
		else {
			Packet.DataLSB = 0x40;
			Packet.DataMSB = 0x00;
		}

		SendPacket(&Packet);
	}
}

void CUsbCode::EnableAutoConfirm(int Mode)
{
	if(IsOpen() )
	{
		// first make sure the button pin interrupt is enabled
		Packet.Recipient = 8;
		Packet.DeviceModel = 18;
		Packet.Length = 0;
		Packet.MajorCmd = 10;
		Packet.MinorCmd = 38;
		Packet.DataLSB = 0x01;		// enabled on pin P0.0
		Packet.DataMSB = 0x00;
		SendPacket(&Packet);

		Packet.Recipient = 8;
		Packet.DeviceModel = 18;
		Packet.Length = 0;
		Packet.MajorCmd = 10;
		Packet.MinorCmd = 72;
		if(Mode) {
			Packet.DataLSB = 0x00;
			Packet.DataMSB = 0x80;
		}
		else {
			Packet.DataLSB = 0x80;
			Packet.DataMSB = 0x00;
		}

		SendPacket(&Packet);
	}

}

void CUsbCode::LoadPower(char Color, char Power)
{
if(IsOpen() )
	{
		Packet.Recipient = 8;
		Packet.DeviceModel = 18;
		Packet.Length = 0;
		Packet.MajorCmd = 10;
		Packet.MinorCmd = 34;
		Packet.DataLSB = Color;
		Packet.DataMSB = Power;
		SendPacket(&Packet);
	}
}

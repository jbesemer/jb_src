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
#include "devioctl.h"		// This header file is proved by MS, with the DDK, also available on the web.

#include <initguid.h>
#include "UsbCode.h"


DEFINE_GUID(USBIODS_GUID, 0xb5157d69, 0x75f8, 0x11d3, 0x8c, 0xe0, 0x0, 0x20, 0x78, 0x15, 0xe6, 0x11);


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
	HDEVINFO  hInfo = SetupDiGetClassDevs((LPGUID)&USBIODS_GUID, NULL, NULL,
	                                     DIGCF_PRESENT |  DIGCF_INTERFACEDEVICE);

    if (hInfo == INVALID_HANDLE_VALUE)		// check for error
		return(0);
	

	for (DWORD i=0; ; ++i)					// loop till all devices are found
		{
		SP_INTERFACE_DEVICE_DATA Interface_Info;			// declare structure
		Interface_Info.cbSize = sizeof(Interface_Info);		// Enumerate device
		if (!SetupDiEnumInterfaceDevice(hInfo, NULL, (LPGUID) &USBIODS_GUID,i, &Interface_Info))
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
              pPacket, sizeof(PacketStruct), pPacket, sizeof(PacketStruct), &nBytes, NULL );
 
	if( !success )	
		{
		//App.m_pMainWnd->KillTimer(ID_Timer);		
		LPVOID lpMsgBuf;
		FormatMessage(
			FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
			NULL, GetLastError(),
			MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), // Default language
		    (LPTSTR) &lpMsgBuf, 0, NULL );
		// Display the string.
		MessageBox(NULL,(LPTSTR)lpMsgBuf,"Failed to send USBIODS packet!",MB_ICONHAND);		
		LocalFree( lpMsgBuf );  // Free the buffer.
		Close();
		return(0);
		}

	return(1);
}



void CUsbCode::SetupSerial(int Mode)
// Setup Serial port function 0=OFF,1=2400
{
	
	Packet.Recipient	= 8;		// Always 8 for the USBIODS device
	Packet.DeviceModel= 18;		// Always 18 for the USBIODS device
	Packet.MajorCmd = 10;
	Packet.MinorCmd = 40;
	Packet.DataLSB = 0;		
	Packet.DataMSB = 0;
	Packet.Length = 0;

	if(Mode) {			// TODO should read the control byte b4 to set the blink led
		Packet.DataLSB = 0x03;		// Turn on the serial port
		SendPacket(&Packet);
	}
	else {
		Packet.DataLSB = 0x01;		// Turn on the serial port
		SendPacket(&Packet);
	}

}

void CUsbCode::SendSerial(int Count, char *pData)
// Sends upto 7 bytes for data to the serial port
{
	int timeout,RxCount,TxCount,Send, Sent=0;
	do{
		timeout=0x1FFF;
		while(GetSerialStatus(&RxCount,&TxCount) && timeout--);  // wait till tx buffer empty
		if(!timeout)	AfxMessageBox("Error: Timeout on serial TX!");

		Packet.Recipient	= 8;		// Always 8 for the USBIODS device
		Packet.DeviceModel= 18;		// Always 18 for the USBIODS device
		Packet.MajorCmd = 10;
		Packet.MinorCmd = 50;
		Packet.DataLSB = 0;		
		Packet.DataMSB = 0;
		Packet.Length = 8;
		Send = Count-Sent;
		if(Send>7) Send = 7;
		memcpy(&Packet.ExtData[1],&(pData[Sent]),Send);
		Packet.ExtData[0] = (unsigned char)Send;
		SendPacket(&Packet);
		Sent += Send;	

	}while(Sent < Count);

}

int CUsbCode::GetSerialStatus(int* RxCount, int* TxCount)
{
	// reads the serial buffer counts and status
	Packet.Recipient	= 8;		// Always 8 for the USBIODS device
	Packet.DeviceModel= 18;		// Always 18 for the USBIODS device
	Packet.MajorCmd = 11;
	Packet.MinorCmd = 9;
	Packet.DataLSB = 0;		
	Packet.DataMSB = 0;
	Packet.Length = 0;
	SendPacket(&Packet);
	*RxCount = (int)((char*)&Packet)[5];
	*TxCount = (int)((char*)&Packet)[6];

	return(*TxCount & 0x0F);
}

int CUsbCode::ReadSerial(char *str)
{
	// reads the RX serial buffer 
	Packet.Recipient	= 8;		// Always 8 for the USBIODS device
	Packet.DeviceModel= 18;		// Always 18 for the USBIODS device
	Packet.MajorCmd = 11;
	Packet.MinorCmd = 50;
	Packet.DataLSB = 0;		
	Packet.DataMSB = 0;
	Packet.Length = 0;
	SendPacket(&Packet);
	int Count  = (int)Packet.Recipient;
	memcpy(str,&((char*)&Packet)[1],Count);	
	str[Count] = NULL;	// add the string terminator NULL
	return(Count);
}

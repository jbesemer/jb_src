// FileName: UsbCode.h	
// Delcom Engineering - Copyright 2000
// Defines the UsbCode Class

typedef unsigned char uchar;         

typedef struct {
		uchar Recipient;
		uchar DeviceModel;
		uchar MajorCmd;
		uchar MinorCmd;
		uchar DataLSB;
		uchar DataMSB;
		SHORT Length;
		uchar ExtData[8];
	} PacketStruct,*pPacketStruct;


class CUsbCode
{
	char	msg[512];
	HANDLE	hUsb;
	
public:
	int ReadSerial(char* str);
	int GetSerialStatus(int* RxCount, int* TxCount);
	void SendSerial(int Count, char* Data);
	void SetupSerial(int Mode);
	PacketStruct Packet;
	CUsbCode();
	int		Scan(CString *);
	bool	Open(CString );
	int		Close();
	int		SendPacket( pPacketStruct ); 
};

 
//  - - - - - - - e o f - - - - - - - - //
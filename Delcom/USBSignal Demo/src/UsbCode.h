// FileName: UsbCode.h	
// Delcom Engineering - Copyright 2000
// Defines the UsbCode Class

#define GREENLED	0
#define	REDLED		1
#define BLUELED		2

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
	void LoadPower(char Color, char Power);
	void EnableAutoConfirm(int Mode);
	void EnableAutoClear(int Mode);
	void Buzzer(uchar Mode, uchar Freq, uchar Repeat, uchar OnTime, uchar OffTime);
	int IsOpen(void);
	void LoadInitialPhaseDelay(char Color, char Delay);
	void SyncLeds(void);
	void LoadPreScalar(char PreScalar);
	void LoadLedFreqDuty(char Color, char Low, char High);
	int GetButtonStatus();
	int ReadVersionNumber();
	int ReadSerialNumber();
	void LED(int Color, int Mode );
	PacketStruct Packet;
	CUsbCode();
	int		Scan(CString *);
	bool	Open(CString );
	int		Close();
	int		SendPacket( pPacketStruct ); 
};

 
//  - - - - - - - e o f - - - - - - - - //
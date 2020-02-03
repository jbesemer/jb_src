// USB_HID_FSDlg.cpp : implementation file
//



#include "stdafx.h"
#include "USB_HID_FS.h"
#include "USB_HID_FSDlg.h"

//#include <initguid.h>
extern "C" {
#include "hidsdi.h"
#include <setupapi.h>	
	// note must add hid.lib setupapi.lib to the project
}


#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif


#define TimerPollRate 20	// in ms

//Application global variables 
	//HANDLE			DeviceHandle;
	GUID			HidGuid;
	ULONG			Length;
	PSP_DEVICE_INTERFACE_DETAIL_DATA	detailData;
	ULONG			Required;
	DWORD			ActualBytesRead;
	DWORD			BytesRead;
	HIDP_CAPS		Capabilities;
	DWORD			cbBytesRead;
	DWORD			dwError;
	HANDLE			hEventObject;
	HANDLE			hDevInfo;
	OVERLAPPED		HIDOverlapped;
	char			InputReport[8];
	LPOVERLAPPED	lpOverLap;
	DWORD			NumberOfBytesRead;
	//HANDLE			ReadHandle;
	CString			ValueToDisplay;


/////////////////////////////////////////////////////////////////////////////
// CAboutDlg dialog used for App About

class CAboutDlg : public CDialog
{
public:
	CAboutDlg();

// Dialog Data
	//{{AFX_DATA(CAboutDlg)
	enum { IDD = IDD_ABOUTBOX };
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CAboutDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	//{{AFX_MSG(CAboutDlg)
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialog(CAboutDlg::IDD)
{
	//{{AFX_DATA_INIT(CAboutDlg)
	//}}AFX_DATA_INIT
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CAboutDlg)
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialog)
	//{{AFX_MSG_MAP(CAboutDlg)
		// No message handlers
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CUSB_HID_FSDlg dialog

CUSB_HID_FSDlg::CUSB_HID_FSDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CUSB_HID_FSDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CUSB_HID_FSDlg)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CUSB_HID_FSDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CUSB_HID_FSDlg)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CUSB_HID_FSDlg, CDialog)
	//{{AFX_MSG_MAP(CUSB_HID_FSDlg)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_WM_TIMER()
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CUSB_HID_FSDlg message handlers

BOOL CUSB_HID_FSDlg::OnInitDialog()
{
	CDialog::OnInitDialog();

	// Add "About..." menu item to system menu.

	// IDM_ABOUTBOX must be in the system command range.
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != NULL)
	{
		CString strAboutMenu;
		strAboutMenu.LoadString(IDS_ABOUTBOX);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon
	
	// Initialize
	if(	DeviceFound = ScanForHidDevice())		// scan & open the device
		{
		GetReport();					// get the first report values, also clears the foot switch count
		GetFirmwareVersion();			// display the version info
		SetTimer(ID_TIMER,TimerPollRate,NULL);	// enable the timer
		}
	
	return TRUE;  // return TRUE  unless you set the focus to a control
}

void CUSB_HID_FSDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialog::OnSysCommand(nID, lParam);
	}
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void CUSB_HID_FSDlg::OnPaint() 
{
	if (IsIconic())
	{
		CPaintDC dc(this); // device context for painting

		SendMessage(WM_ICONERASEBKGND, (WPARAM) dc.GetSafeHdc(), 0);

		// Center icon in client rectangle
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// Draw the icon
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialog::OnPaint();
	}
}

HCURSOR CUSB_HID_FSDlg::OnQueryDragIcon()
{
	return (HCURSOR) m_hIcon;
}

bool CUSB_HID_FSDlg::ScanForHidDevice()
{
	//Use a series of API calls to find a HID with a matching Vendor and Product ID.

	HIDD_ATTRIBUTES						Attributes;
	SP_DEVICE_INTERFACE_DATA			devInfoData;
	bool								LastDevice = FALSE;
	int									MemberIndex = 0;
	bool								MyDeviceDetected = FALSE; 
	LONG								Result;


	//These are the vendor and product IDs to look for.
	//Uses Lakeview Research's Vendor ID.
	const unsigned int VendorID = 0x0FC5;
	const unsigned int ProductID = 0xB010;

	Length = 0;
	detailData = NULL;
	DeviceHandle=NULL;

	//PromptMessage("Searching for USB HID device...");

	/*
	API function: HidD_GetHidGuid
	Get the GUID for all system HIDs.
	Returns: the GUID in HidGuid.
	*/

	HidD_GetHidGuid(&HidGuid);	
	
	/*
	API function: SetupDiGetClassDevs
	Returns: a handle to a device information set for all installed devices.
	Requires: the GUID returned by GetHidGuid.
	*/
	
	hDevInfo=SetupDiGetClassDevs 
		(&HidGuid, 
		NULL, 
		NULL, 
		DIGCF_PRESENT|DIGCF_INTERFACEDEVICE);
		
	devInfoData.cbSize = sizeof(devInfoData);

	//Step through the available devices looking for the one we want. 
	//Quit on detecting the desired device or checking all available devices without success.
	MemberIndex = 0;
	LastDevice = FALSE;



	do
	{
		MyDeviceDetected=FALSE;
		
		/*
		API function: SetupDiEnumDeviceInterfaces
		On return, MyDeviceInterfaceData contains the handle to a
		SP_DEVICE_INTERFACE_DATA structure for a detected device.
		Requires:
		The DeviceInfoSet returned in SetupDiGetClassDevs.
		The HidGuid returned in GetHidGuid.
		An index to specify a device.
		*/

		Result=SetupDiEnumDeviceInterfaces 
			(hDevInfo, 
			0, 
			&HidGuid, 
			MemberIndex, 
			&devInfoData);

		if (Result != 0)
		{
			//A device has been detected, so get more information about it.

			/*
			API function: SetupDiGetDeviceInterfaceDetail
			Returns: an SP_DEVICE_INTERFACE_DETAIL_DATA structure
			containing information about a device.
			To retrieve the information, call this function twice.
			The first time returns the size of the structure in Length.
			The second time returns a pointer to the data in DeviceInfoSet.
			Requires:
			A DeviceInfoSet returned by SetupDiGetClassDevs
			The SP_DEVICE_INTERFACE_DATA structure returned by SetupDiEnumDeviceInterfaces.
			
			The final parameter is an optional pointer to an SP_DEV_INFO_DATA structure.
			This application doesn't retrieve or use the structure.			
			If retrieving the structure, set 
			MyDeviceInfoData.cbSize = length of MyDeviceInfoData.
			and pass the structure's address.
			*/
			
			//Get the Length value.
			//The call will return with a "buffer too small" error which can be ignored.
			Result = SetupDiGetDeviceInterfaceDetail 
				(hDevInfo, 
				&devInfoData, 
				NULL, 
				0, 
				&Length, 
				NULL);

			//Allocate memory for the hDevInfo structure, using the returned Length.
			detailData = (PSP_DEVICE_INTERFACE_DETAIL_DATA)malloc(Length);
			
			//Set cbSize in the detailData structure.
			detailData -> cbSize = sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA);

			//Call the function again, this time passing it the returned buffer size.
			Result = SetupDiGetDeviceInterfaceDetail 
				(hDevInfo, 
				&devInfoData, 
				detailData, 
				Length, 
				&Required, 
				NULL);

			//Open a handle to the device.

			/*
			API function: CreateFile
			Returns: a handle that enables reading and writing to the device.
			Requires:
			The DevicePath in the detailData structure
			returned by SetupDiGetDeviceInterfaceDetail.
			*/

			DeviceHandle=CreateFile 
				(detailData->DevicePath, 
				GENERIC_READ|GENERIC_WRITE, 
				FILE_SHARE_READ|FILE_SHARE_WRITE, 
				(LPSECURITY_ATTRIBUTES)NULL,
				OPEN_EXISTING, 
				0, 
				NULL);

			//DisplayLastError("CreateFile: ");

						/*
			API function: HidD_GetAttributes
			Requests information from the device.
			Requires: the handle returned by CreateFile.
			Returns: a HIDD_ATTRIBUTES structure containing
			the Vendor ID, Product ID, and Product Version Number.
			Use this information to decide if the detected device is
			the one we're looking for.
			*/

			//Set the Size to the number of bytes in the structure.
			Attributes.Size = sizeof(Attributes);

			Result = HidD_GetAttributes 
				(DeviceHandle, 
				&Attributes);
			
			//DisplayLastError("HidD_GetAttributes: ");
			
			//Is it the desired device?
			MyDeviceDetected = FALSE;
			

			if (Attributes.VendorID == VendorID)
			{
				if (Attributes.ProductID == ProductID)
				{
					//Both the Product and Vendor IDs match.
					MyDeviceDetected = TRUE;
					//PromptMessage("Device detected.");
					//Get the device's capablities.
					//GetDeviceCapabilities();
					PrepareForOverlappedTransfer();
				} //if (Attributes.ProductID == ProductID)

				else
					//The Product ID doesn't match.
					CloseHandle(DeviceHandle);
			} //if (Attributes.VendorID == VendorID)

			else	//The Vendor ID doesn't match.
			{
				CString cstr;
				//cstr.Format("Hid device found. VID=%X, PID=%X.",Attributes.VendorID,Attributes.ProductID);
				//PromptMessage(cstr);
				CloseHandle(DeviceHandle);
			}

		//Free the memory used by the detailData structure (no longer needed).
		free(detailData);
		}  //if (Result != 0)

		else	{
			//SetupDiEnumDeviceInterfaces returned 0, so there are no more devices to check.
			LastDevice=TRUE;
			//PromptMessage("No HID devices detected!");
		}

		//If we haven't found the device yet, and haven't tried every available device,
		//try the next one.
		MemberIndex = MemberIndex + 1;

	} //do
	while ((LastDevice == FALSE) && (MyDeviceDetected == FALSE));

	if(MyDeviceDetected)
		{
		//AfxMessageBox("Device detected!");
		HidD_SetNumInputBuffers(DeviceHandle,1);
		}

	//Free the memory reserved for hDevInfo by SetupDiClassDevs.
	SetupDiDestroyDeviceInfoList(hDevInfo);
	//DisplayLastError("SetupDiDestroyDeviceInfoList");

	return MyDeviceDetected;
}

void CUSB_HID_FSDlg::OnCancel() 
{
	KillTimer(ID_TIMER);
	CloseHandle(DeviceHandle);
	CloseHandle(ReadHandle);
	CDialog::OnCancel();
}

void CUSB_HID_FSDlg::OnTimer(UINT nIDEvent) 
{
	GetReport();	// update switches
	CDialog::OnTimer(nIDEvent);
}

void CUSB_HID_FSDlg::PrepareForOverlappedTransfer()
{
	//Get another handle to the device for the overlapped ReadFiles.
	ReadHandle=CreateFile 
		(detailData->DevicePath, 
		GENERIC_READ|GENERIC_WRITE, 
		FILE_SHARE_READ|FILE_SHARE_WRITE,
		(LPSECURITY_ATTRIBUTES)NULL, 
		OPEN_EXISTING, 
		FILE_FLAG_OVERLAPPED, 
		NULL);
	//DisplayLastError("CreateFile (ReadHandle): ");

	//Get an event object for the overlapped structure.

	/*API function: CreateEvent
	Requires:
	  Security attributes or Null
	  Manual reset (true). Use ResetEvent to set the event object's state to non-signaled.
	  Initial state (true = signaled) 
	  Event object name (optional)
	Returns: a handle to the event object
	*/

	if (hEventObject == 0)
	{
		hEventObject = CreateEvent 
			(NULL, 
			TRUE, 
			TRUE, 
			"");
	//DisplayLastError("CreateEvent: ") ;

	//Set the members of the overlapped structure.
	HIDOverlapped.hEvent = hEventObject;
	HIDOverlapped.Offset = 0;
	HIDOverlapped.OffsetHigh = 0;
	}
}


// Get the report and display the firmware version info
void CUSB_HID_FSDlg::GetFirmwareVersion()
{

	CString VersionString;

	VersionString.Format("HID Foot Switch Found.   Firmware Version=%d",FirmwareVersion);
	CStatic *pVersion = (CStatic *)GetDlgItem(IDC_Version);
	pVersion->SetWindowText(VersionString);
}

void CUSB_HID_FSDlg::GetReport()
{

	CString	ByteToDisplay = "";
	CString	MessageToDisplay = "";
	DWORD	Result;
	
	//Read a report from the device.
 	
	/*API call:ReadFile
	'Returns: the report in InputReport.
	'Requires: a device handle returned by CreateFile
	'(for overlapped I/O, CreateFile must be called with FILE_FLAG_OVERLAPPED),
	'the Input report length in bytes returned by HidP_GetCaps,
	'and an overlapped structure whose hEvent member is set to an event object.
	*/

	Result = ReadFile 
		(ReadHandle, 
		InputReport, 
		8+1,
		&NumberOfBytesRead,
		(LPOVERLAPPED) &HIDOverlapped); 
 
	//DisplayLastError("ReadFile: ") ;

	/*API call:WaitForSingleObject
	'Used with overlapped ReadFile.
	'Returns when ReadFile has received the requested amount of data or on timeout.
	'Requires an event object created with CreateEvent
	'and a timeout value in milliseconds.
	*/

	Result = WaitForSingleObject 
		(hEventObject, 
		6000);
	//DisplayLastError("WaitForSingleObject: ") ;
 
	switch (Result)
	{
	case WAIT_OBJECT_0:
		{
		ValueToDisplay.Format("%s", "ReadFile Completed");
		//PromptMessage(ValueToDisplay);
		break;
		}
	case WAIT_TIMEOUT:
		{
		ValueToDisplay.Format("%s", "ReadFile timeout");
		//PromptMessage(ValueToDisplay);
		//Cancel the Read operation.

		/*API call: CancelIo
		Cancels the ReadFile
        Requires the device handle.
        Returns non-zero on success.
		*/
		
		Result = CancelIo(ReadHandle);
		
		//A timeout may mean that the device has been removed. 
		//Close the device handles and set DeviceDetected = False 
		//so the next access attempt will search for the device.
		KillTimer(ID_TIMER);		// kill the timer on error
		CloseHandle(ReadHandle);
		CloseHandle(DeviceHandle);
		//PromptMessage("Can't read from device");
		DeviceFound = FALSE;
		break;
	default:
		KillTimer(ID_TIMER);		// kill the timer on error
		ValueToDisplay.Format("%s", "Undefined error");
		break;
		}
	}

	/*
	API call: ResetEvent
	Sets the event object to non-signaled.
	Requires a handle to the event object.
	Returns non-zero on success.
	*/

	ResetEvent(hEventObject);

	FirmwareVersion = (UINT)InputReport[1];

	// switch 0
	CButton *pSW0 = (CButton *) GetDlgItem(IDC_CHECK0);
	if(!(InputReport[2] & 0x01))	pSW0->SetCheck(1);
	else							pSW0->SetCheck(0);
	// switch 1
	CButton *pSW1 = (CButton *) GetDlgItem(IDC_CHECK1);
	if(!(InputReport[2] & 0x02))	pSW1->SetCheck(1);
	else							pSW1->SetCheck(0);



	

}
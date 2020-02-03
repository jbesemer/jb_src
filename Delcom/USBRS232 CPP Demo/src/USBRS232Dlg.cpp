// USBRS232Dlg.cpp : implementation file
//

#include "stdafx.h"
#include "USBRS232.h"
#include "USBRS232Dlg.h"
#include "UsbCode.h"


#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif


#define  USBIODS_GUID_STR "{B5157D69-75F8-11d3-8CE0-00207815E611}"
CUsbCode CUsb;		// The usb class

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
// CUSBRS232Dlg dialog

CUSBRS232Dlg::CUSBRS232Dlg(CWnd* pParent /*=NULL*/)
	: CDialog(CUSBRS232Dlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CUSBRS232Dlg)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CUSBRS232Dlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CUSBRS232Dlg)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CUSBRS232Dlg, CDialog)
	//{{AFX_MSG_MAP(CUSBRS232Dlg)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_CBN_SELCHANGE(IDC_BAUDRATE, OnSelchangeBaudrate)
	ON_WM_TIMER()
	ON_BN_CLICKED(IDC_MODE, OnMode)
	ON_BN_CLICKED(IDC_SEND, OnSend)
	ON_BN_CLICKED(IDC_RXOVER, OnClearFlags)
	ON_EN_CHANGE(IDC_POLLRATE, OnChangePollrate)
	ON_BN_CLICKED(IDC_RXFRAME, OnClearFlags)
	ON_BN_CLICKED(IDC_TXOVER, OnClearFlags)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CUSBRS232Dlg message handlers

BOOL CUSBRS232Dlg::OnInitDialog()
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

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon
	
	// Scan for USB Devices and fill the list box
	CString Devices[127];
	Devices[0] = USBIODS_GUID_STR;		// get the guid
	CComboBox* pComboBox = (CComboBox*) GetDlgItem(IDC_DEVICELIST);

	// Default dialog properties
	CEdit* pEdit = (CEdit*) GetDlgItem(IDC_POLLRATE);
	pEdit->SetWindowText("100");	// default the pollrate to 100ms
	DisplayMode = 0;

	int i;
	int found = CUsb.Scan( Devices );	// scans for all the device matching the guid
	if( !found)	{
		MessageBox("Unable to enumerate the Usb device", "Enumeration Error");
		pComboBox->AddString("USB Device Not Found!");
		}
	else{
		i=0;
		while(i<found)
			pComboBox->AddString(Devices[i++]);		// add all the device to the list box
	
		}
	pComboBox->SetCurSel(0);							// default to the first entry.

	// If a USBIODS device exists try to open the first device found.
	if(found)
		ConfigDevice(Devices[0]);
	
	pComboBox = (CComboBox*) GetDlgItem(IDC_BAUDRATE);
	pComboBox->SetCurSel(0);						

	return TRUE;  // return TRUE  unless you set the focus to a control
}

void CUSBRS232Dlg::OnSysCommand(UINT nID, LPARAM lParam)
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

void CUSBRS232Dlg::OnPaint() 
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

// The system calls this to obtain the cursor to display while the user drags
//  the minimized window.
HCURSOR CUSBRS232Dlg::OnQueryDragIcon()
{
	return (HCURSOR) m_hIcon;
}

bool CUSBRS232Dlg::ConfigDevice(CString DeviceName)
{

		if( CUsb.Open( DeviceName  )) // try to open the device
		{	// if device opened sucessfully, then check versions
			CUsb.Packet.Recipient = 8;
			CUsb.Packet.DeviceModel = 18;
			CUsb.Packet.MajorCmd = 11;
			CUsb.Packet.MinorCmd = 10;
			CUsb.Packet.Length = 0;
			CUsb.SendPacket(&CUsb.Packet);
			if( CUsb.Packet.DataLSB < 5 )
				MessageBox("Your USBIODS chip firmware does not support RS232 functions","Incompatable Frimware!");

		}
		// should check driver version too
	return(1);
}

void CUSBRS232Dlg::OnCancel() 
{
	CUsb.Close();	
	CDialog::OnCancel();
}

void CUSBRS232Dlg::OnSelchangeBaudrate() 
{
	char str[16];
	int pollrate;
	CComboBox* pComboBox = (CComboBox*) GetDlgItem(IDC_BAUDRATE);
	
	int Mode = pComboBox->GetCurSel();
	
	
	if(Mode)
		{		
		CUsb.SetupSerial(Mode);	
		CEdit* pEdit = (CEdit*) GetDlgItem(IDC_POLLRATE);
		pEdit->GetWindowText(str,sizeof(str));
		pollrate = atoi(str);
		if( !SetTimer(ID_TIMER,pollrate,NULL))
			AfxMessageBox("Unable to setup timer resource",MB_OK);
		}
	else
		{
		// TODO Timer Off
		CUsb.SetupSerial(Mode);	
		KillTimer(ID_TIMER);
				
		}
	

	
}

void CUSBRS232Dlg::OnTimer(UINT nIDEvent) 
{
	// Check if any data needs to be read from the USB chip
	int RxCount, TxCount;
	CUsb.GetSerialStatus(&RxCount,&TxCount);
	CButton *pButton;
	if( 0x80 & RxCount)	{
		pButton	= (CButton*) GetDlgItem( IDC_RXOVER );
		pButton->SetCheck(1);
		}		
	if( 0x40 & RxCount)	{
		pButton	= (CButton*) GetDlgItem( IDC_RXFRAME );
		pButton->SetCheck(1);
		}
	if( 0x80 & TxCount)	{
		pButton	= (CButton*) GetDlgItem( IDC_TXOVER );
		pButton->SetCheck(1);
		}

	if ( RxCount & 0x0F )	// if there's any rx data get it and display it.
	{
		char str[16],hstr[64],tmp[16];
		RxCount = CUsb.ReadSerial(str);	// get the rx data	
		CEdit* pEdit = (CEdit*) GetDlgItem(IDC_EDIT_RX);
		if(!DisplayMode)	// if ascii mode
			pEdit->ReplaceSel(str);
		else	{	// else hex mode
			hstr[0]=NULL;
			for(TxCount=0; TxCount<RxCount; TxCount++) {
				sprintf(tmp,"0x%2X ",str[TxCount]);
				strcat(hstr,tmp);
			}
		pEdit->ReplaceSel(hstr);
		}
	}


	CDialog::OnTimer(nIDEvent);
}

void CUSBRS232Dlg::OnMode() 
{
	CButton *pButton = (CButton*) GetDlgItem(IDC_MODE);
	if(pButton->GetCheck())
	{
		DisplayMode = 1;
		pButton->SetWindowText("Hex");
	}
	else
	{
		DisplayMode = 0;
		pButton->SetWindowText("Ascii");
	}

	
}

void CUSBRS232Dlg::OnSend() 
{
	int Count;
	char Tx[512];
	CEdit* SendBox = (CEdit*)	GetDlgItem(IDC_EDIT_TX);
	SendBox->GetWindowText(Tx, sizeof(Tx));
	Count = strlen(Tx);
	if(DisplayMode)  Count=Hex2Str(Tx);
	CUsb.SendSerial(Count,Tx);

}

void CUSBRS232Dlg::OnClearFlags() 
{
	CButton *pButton;
	if ( IDYES == AfxMessageBox("Do you want toclear the serial status flags?",MB_YESNO))
		{
		pButton	= (CButton*) GetDlgItem( IDC_RXOVER );
		pButton->SetCheck(0);
		pButton	= (CButton*) GetDlgItem( IDC_RXFRAME );
		pButton->SetCheck(0);
		pButton	= (CButton*) GetDlgItem( IDC_TXOVER );
		pButton->SetCheck(0);
		}

	
}

void CUSBRS232Dlg::OnChangePollrate() 
{
	//Update the pollrate timer only do if running (baudrate selected)
	char str[16];
	int pollrate;
	CComboBox* pComboBox = (CComboBox*) GetDlgItem(IDC_BAUDRATE);
	int Mode = pComboBox->GetCurSel();
		
	if(Mode && Mode != -1)
		{		
		CEdit* pEdit = (CEdit*) GetDlgItem(IDC_POLLRATE);
		pEdit->GetWindowText(str,sizeof(str));
		pollrate = atoi(str);
		if( !SetTimer(ID_TIMER,pollrate,NULL))
			AfxMessageBox("Unable to setup timer resource",MB_OK);
		}
	
	
}

void CUSBRS232Dlg::OnOK() 
{
	// This code just captures the enter key and does not pass it down
	//	CDialog::OnOK();
}

int CUSBRS232Dlg::Hex2Str(char *Buffer)
// This function convert a ascii hex string to pure hex
{
	char num[16],str[256];
	unsigned int x,len,hex,i,index=0;
	len = strlen(Buffer);
	for(i=0;i<len;)
	{
		if(Buffer[i] == '0' && (Buffer[i+1] =='x' || Buffer[i+1] =='X'))
			i+=2;	// strip out '0x' prefix if any
		else	{
			x = Buffer[i];
			if(isxdigit((int)Buffer[i])){
				num[1] = NULL; 
				num[2] = NULL;
				num[0]=Buffer[i++];
				x = Buffer[i];
				if(isxdigit((int)Buffer[i]) )
					num[1]=Buffer[i++];
				sscanf(num,"%X",&hex);
				str[index]=hex;
				index++;
			}
			else
				i++;
		}
	}
	Buffer[0] = NULL; // in case the routine failed
	memcpy(Buffer,str,index);
	return(index);
}

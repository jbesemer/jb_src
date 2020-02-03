// USBSignalDlg.cpp : implementation file
//

#include "stdafx.h"
#include "USBSignal.h"
#include "USBSignalDlg.h"
#include <math.h>


#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif


#include "UsbCode.h"



#define  USBDELVI_GUID_STR "{59BD73A6-822E-4684-9530-0754FE897113}"

// --- Globals Variables ---
CUsbCode CUsb;	
extern CUSBSignalApp theApp;	


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
// CUSBSignalDlg dialog

CUSBSignalDlg::CUSBSignalDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CUSBSignalDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CUSBSignalDlg)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CUSBSignalDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CUSBSignalDlg)
		// NOTE: the ClassWizard will add DDX and DDV calls here
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CUSBSignalDlg, CDialog)
	//{{AFX_MSG_MAP(CUSBSignalDlg)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_WM_DESTROY()
	ON_WM_TIMER()
	ON_BN_CLICKED(IDC_RADIO_GOFF, OnRadioGoff)
	ON_BN_CLICKED(IDC_RADIO_GON, OnRadioGon)
	ON_BN_CLICKED(IDC_RADIO_RFLASH, OnRadioRflash)
	ON_BN_CLICKED(IDC_RADIO_GFLASH, OnRadioGflash)
	ON_BN_CLICKED(IDC_RADIO_ROFF, OnRadioRoff)
	ON_BN_CLICKED(IDC_RADIO_RON, OnRadioRon)
	ON_BN_CLICKED(IDC_RADIO_BON, OnRadioBon)
	ON_BN_CLICKED(IDC_RADIO_BOFF, OnRadioBoff)
	ON_BN_CLICKED(IDC_RADIO_BFLASH, OnRadioBflash)
	ON_EN_CHANGE(IDC_EDIT_GFREQ, OnChangeGreen)
	ON_EN_CHANGE(IDC_EDIT_PRESCALAR, OnChangeEditPrescalar)
	ON_EN_CHANGE(IDC_EDIT_RONTIME, OnChangeRed)
	ON_EN_CHANGE(IDC_EDIT_BOFFTIME, OnChangeBlue)
	ON_EN_CHANGE(IDC_EDIT_GOFFSET, OnChangeEditGoffset)
	ON_EN_CHANGE(IDC_EDIT_ROFFSET, OnChangeEditRoffset)
	ON_EN_CHANGE(IDC_EDIT_BOFFSET, OnChangeEditBoffset)
	ON_BN_CLICKED(IDC_BUTTON_SYNC, OnButtonSync)
	ON_CBN_SELCHANGE(IDC_COMBO_DEVICE, OnSelchangeComboDevice)
	ON_BN_CLICKED(IDC_BUTTONASTART, OnButtonAStart)
	ON_BN_CLICKED(IDC_BUTTONASTOP, OnButtonAStop)
	ON_BN_CLICKED(IDC_CHECK_AUTOCLEAR, OnCheckAutoClear)
	ON_BN_CLICKED(IDC_CHECK_AUTOCONFIRM, OnCheckAutoConfirm)
	ON_EN_CHANGE(IDC_EDIT_AREPEAT, OnChangeEditARepeat)
	ON_EN_CHANGE(IDC_EDIT_AOFFTIME, OnChangeEditAOffTime)
	ON_EN_CHANGE(IDC_EDIT_AONTIME, OnChangeEditAOnTime)
	ON_WM_HELPINFO()
	ON_WM_CONTEXTMENU()
	ON_EN_CHANGE(IDC_EDIT_GPOWER, OnChangeEditGpower)
	ON_EN_CHANGE(IDC_EDIT_RPOWER, OnChangeEditRpower)
	ON_EN_CHANGE(IDC_EDIT_GDUTY, OnChangeGreen)
	ON_EN_CHANGE(IDC_EDIT_GONTIME, OnChangeGreen)
	ON_EN_CHANGE(IDC_EDIT_GOFFTIME, OnChangeGreen)
	ON_EN_CHANGE(IDC_EDIT_ROFFTIME, OnChangeRed)
	ON_EN_CHANGE(IDC_EDIT_BONTIME, OnChangeBlue)
	ON_EN_CHANGE(IDC_EDIT_BPOWER, OnChangeEditBpower)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()


/////////////////////////////////////////////////////////////////////////////
// HELP MAP - used for context sentive help
DWORD HelpMap[] = {
		IDC_RADIO_GOFF,IDH_VOFF,
		IDC_RADIO_ROFF,IDH_VOFF,                  
		IDC_RADIO_BOFF,IDH_VOFF,
		IDC_RADIO_GON,IDH_VON,                   
		IDC_RADIO_RON,IDH_VON,          
		IDC_RADIO_BON,IDH_VON,                   
		IDC_RADIO_GFLASH,IDH_VFLASH,
		IDC_RADIO_RFLASH,IDH_VFLASH,    
		IDC_RADIO_BFLASH,IDH_VFLASH,                
		IDC_EDIT_GFREQ,IDH_VFREQ,
		IDC_EDIT_RFREQ,IDH_VFREQ,       
		IDC_EDIT_BFREQ,IDH_VFREQ,       
		IDC_EDIT_GDUTY,IDH_VDUTY,
		IDC_EDIT_RDUTY,IDH_VDUTY,       
		IDC_EDIT_BDUTY,IDH_VDUTY,       
		IDC_EDIT_GPERIOD,IDH_VPERIOD,
		IDC_EDIT_RPERIOD,IDH_VPERIOD, 
		IDC_EDIT_BPERIOD,IDH_VPERIOD,   
		IDC_EDIT_GONTIME,IDH_VONTIME,
		IDC_EDIT_RONTIME,IDH_VONTIME,   
		IDC_EDIT_BONTIME,IDH_VONTIME,   
		IDC_EDIT_GOFFTIME,IDH_VOFFTIME,
		IDC_EDIT_ROFFTIME,IDH_VOFFTIME, 
		IDC_EDIT_BOFFTIME,IDH_VOFFTIME, 
		IDC_EDIT_GOFFSET,IDH_VOFFSET,
		IDC_EDIT_ROFFSET,IDH_VOFFSET,   
		IDC_EDIT_BOFFSET,IDH_VOFFSET,   
		IDC_BUTTON_SYNC,IDH_VSYNC,   
		IDC_COMBO_DEVICE,IDH_DEVICE,
		IDC_CHECK_AUTOCLEAR,IDH_AUTOCLEAR,             
		IDC_CHECK_BUTTON,IDH_BUTTON,
		IDC_EDIT_AFREQ,IDH_AFREQ,                  
		IDC_EDIT_AREPEAT,IDH_AREPEAT,
		IDC_EDIT_FREQMAX,IDH_VFREQMAX,   
		IDC_EDIT_FREQMIN,IDH_VFREQMIN,  
		IDC_EDIT_PRESCALAR,IDH_VPRESCALAR,  
		IDC_EDIT_AONTIME,IDH_AONTIME,
		IDC_EDIT_AOFFTIME,IDH_AOFFTIME,   
		IDC_CHECK_AUTOCONFIRM,IDH_AUTOCONFIRM, 
		IDC_BUTTONASTART,IDH_ASTART,
		IDC_BUTTONASTOP,IDH_ASTOP,    
		IDC_STATIC_VER,IDH_VERSION,      
		IDC_STATIC_SERIAL,IDH_SERIAL,
		0,0 };



/////////////////////////////////////////////////////////////////////////////
// CUSBSignalDlg message handlers

BOOL CUSBSignalDlg::OnInitDialog()
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
			pSysMenu->AppendMenu(MF_STRING, IDM_HELP, "&Help");
		}
	}

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon



	// Scan for USB Devices and fill the list box
	CString Devices[127];
	Devices[0] = USBDELVI_GUID_STR;		// get the guid
	CComboBox* pComboBox = (CComboBox*) GetDlgItem(IDC_COMBO_DEVICE);


	int found = CUsb.Scan( Devices );	// scans for all the device matching the guid
	if( !found)	{
		MessageBox("Unable to enumerate the Usb device", "Enumeration Error");
		pComboBox->AddString("USB Signal Device Not Found!");
		}
	else{
		int i=0;
		while(i<found)
			pComboBox->AddString(Devices[i++]);		// add all the device to the list box
	
		}
	pComboBox->SetCurSel(0);						// default to the first entry.
	
	

	// If a USBIODS device exists try to open the first device found.
	if(found)	OnSelchangeComboDevice();

	

	return TRUE;  // return TRUE  unless you set the focus to a control
}


void CUSBSignalDlg::OnSelchangeComboDevice() 
{
	CString DeviceName;
	KillTimer(ID_TIMER);	// Kill the timer if any
	CUsb.Close();			// Close the device if open

	CComboBox* pComboBox = (CComboBox*) GetDlgItem(IDC_COMBO_DEVICE);
	pComboBox->GetLBText(pComboBox->GetCurSel(),DeviceName);	// get the selected device name

	if( CUsb.Open( DeviceName ) )				// try to open the device
		{
		GetSerialNumber();						// Display the Serial# & Firmware info
		if( !SetTimer(ID_TIMER,100,NULL))		// Re-enble Timer
			AfxMessageBox("Unable to setup timer resource",MB_OK);
		}	
	else
		AfxMessageBox("Unable to open device",MB_OK);

	
	if( CUsb.IsOpen())
	{
		// Initilize the dialog box
		CButton* pRadio;

		pRadio = (CButton*) GetDlgItem(IDC_RADIO_GOFF);
		pRadio->SetCheck(1);
		pRadio = (CButton*) GetDlgItem(IDC_RADIO_GON);
		pRadio->SetCheck(0);
		pRadio = (CButton*) GetDlgItem(IDC_RADIO_GFLASH);
		pRadio->SetCheck(0);
		GreenState = 0;		// OFF
		CUsb.LED(GREENLED,0);

		pRadio = (CButton*) GetDlgItem(IDC_RADIO_ROFF);
		pRadio->SetCheck(1);
		pRadio = (CButton*) GetDlgItem(IDC_RADIO_RON);
		pRadio->SetCheck(0);
		pRadio = (CButton*) GetDlgItem(IDC_RADIO_RFLASH);
		pRadio->SetCheck(0);
		RedState = 0;		// OFF
		CUsb.LED(REDLED,0);

		pRadio = (CButton*) GetDlgItem(IDC_RADIO_BOFF);
		pRadio->SetCheck(1);
		pRadio = (CButton*) GetDlgItem(IDC_RADIO_BON);
		pRadio->SetCheck(0);
		pRadio = (CButton*) GetDlgItem(IDC_RADIO_BFLASH);
		pRadio->SetCheck(0);
		BlueState = 0;		// OFF
		CUsb.LED(BLUELED,0);

		CEdit* pEdit = (CEdit*) GetDlgItem(IDC_EDIT_PRESCALAR);
		pEdit->SetWindowText("10");
		
		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_GONTIME);
		pEdit->SetWindowText("100");

		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_GOFFTIME);
		pEdit->SetWindowText("100");

		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_RONTIME);
		pEdit->SetWindowText("100");

		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_ROFFTIME);
		pEdit->SetWindowText("100");

		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_BONTIME);
		pEdit->SetWindowText("100");

		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_BOFFTIME);
		pEdit->SetWindowText("100");

		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_GOFFSET);
		pEdit->SetWindowText("0");

		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_ROFFSET);
		pEdit->SetWindowText("0");

		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_BOFFSET);
		pEdit->SetWindowText("0");

		// default power level to 80%
		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_GPOWER);
		pEdit->SetWindowText("80");

		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_RPOWER);
		pEdit->SetWindowText("80");

		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_BPOWER);
		pEdit->SetWindowText("80");


		// Auditory Stuff
		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_AFREQ);
		pEdit->SetWindowText("651.0");

		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_AREPEAT);
		pEdit->SetWindowText("2");

		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_AONTIME);
		pEdit->SetWindowText("1");

		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_AOFFTIME);
		pEdit->SetWindowText("1");

	}	
}



void CUSBSignalDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
		if ((nID & 0xFFF0) == IDM_HELP)
		{	
			::WinHelp(m_hWnd, theApp.m_pszHelpFilePath, HELP_CONTENTS, 0);
		}
		else
		{
			CDialog::OnSysCommand(nID, lParam);
		}
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void CUSBSignalDlg::OnPaint() 
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
HCURSOR CUSBSignalDlg::OnQueryDragIcon()
{
	return (HCURSOR) m_hIcon;
}

void CUSBSignalDlg::OnDestroy() 
{
	CDialog::OnDestroy();
	KillTimer(ID_TIMER);
	CUsb.Close();
	
}

void CUSBSignalDlg::OnTimer(UINT nIDEvent) 
{
	if( CUsb.IsOpen() ) {	
		CButton* pButton = (CButton*) GetDlgItem(IDC_CHECK_BUTTON);
		pButton->SetCheck(CUsb.GetButtonStatus());
		CDialog::OnTimer(ID_TIMER);
	}
	else	{
		KillTimer(ID_TIMER);	// kill timer b4 displaying message!
		AfxMessageBox("Error: USB device not open. Terminating Timer!");
	}

}

void CUSBSignalDlg::OnRadioGoff() 
{
	GreenState = 0;
	CUsb.LED(GREENLED,GreenState);
	CButton* pRadio;
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_GOFF);
	pRadio->SetCheck(1);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_GON);
	pRadio->SetCheck(0);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_GFLASH);
	pRadio->SetCheck(0);
}

void CUSBSignalDlg::OnRadioGon() 
{
	GreenState = 1;
	CUsb.LED(GREENLED,GreenState);	
	CButton* pRadio;
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_GOFF);
	pRadio->SetCheck(0);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_GON);
	pRadio->SetCheck(1);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_GFLASH);
	pRadio->SetCheck(0);
}


void CUSBSignalDlg::OnRadioGflash() 
{
	GreenState = 2;
	CUsb.LED(GREENLED,GreenState);	
	CButton* pRadio;
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_GOFF);
	pRadio->SetCheck(0);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_GON);
	pRadio->SetCheck(0);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_GFLASH);
	pRadio->SetCheck(1);
	
}



void CUSBSignalDlg::OnRadioRoff() 
{
	RedState = 0;
	CUsb.LED(REDLED,RedState);
	CButton* pRadio;
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_ROFF);
	pRadio->SetCheck(1);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_RON);
	pRadio->SetCheck(0);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_RFLASH);
	pRadio->SetCheck(0);
}

void CUSBSignalDlg::OnRadioRon() 
{
	RedState = 1;
	CUsb.LED(REDLED,RedState);	
	CButton* pRadio;
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_ROFF);
	pRadio->SetCheck(0);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_RON);
	pRadio->SetCheck(1);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_RFLASH);
	pRadio->SetCheck(0);
}


void CUSBSignalDlg::OnRadioRflash() 
{
	RedState = 2;
	CUsb.LED(REDLED,RedState);
	CButton* pRadio;
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_ROFF);
	pRadio->SetCheck(0);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_RON);
	pRadio->SetCheck(0);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_RFLASH);
	pRadio->SetCheck(1);	
}



void CUSBSignalDlg::OnRadioBoff() 
{
	BlueState = 0;
	CUsb.LED(BLUELED,BlueState);
	CButton* pRadio;
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_BOFF);
	pRadio->SetCheck(1);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_BON);
	pRadio->SetCheck(0);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_BFLASH);
	pRadio->SetCheck(0);
}

void CUSBSignalDlg::OnRadioBon() 
{
	BlueState = 1;
	CUsb.LED(BLUELED,BlueState);	
	CButton* pRadio;
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_BOFF);
	pRadio->SetCheck(0);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_BON);
	pRadio->SetCheck(1);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_BFLASH);
	pRadio->SetCheck(0);
}


void CUSBSignalDlg::OnRadioBflash() 
{
	BlueState = 2;
	CUsb.LED(BLUELED,BlueState);
	CButton* pRadio;
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_BOFF);
	pRadio->SetCheck(0);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_BON);
	pRadio->SetCheck(0);
	pRadio = (CButton*) GetDlgItem(IDC_RADIO_BFLASH);
	pRadio->SetCheck(1);	
}

void CUSBSignalDlg::GetSerialNumber()
{
	char str[64];
	sprintf(str,"SN: %i.",CUsb.ReadSerialNumber());
	CStatic* pText = (CStatic*) GetDlgItem(IDC_STATIC_SERIAL);
	pText->SetWindowText(str);
	sprintf(str,"VER: %i.",CUsb.ReadVersionNumber());
	pText = (CStatic*) GetDlgItem(IDC_STATIC_VER);
	pText->SetWindowText(str);

}






void CUSBSignalDlg::OnChangeEditPrescalar() 
{
	static int Skip = 0;
	if (Skip) return;	// skip if this code called it self.
	Skip = 1;
	int ps;
	char str[128];
	CEdit* pEdit = (CEdit*) GetDlgItem(IDC_EDIT_PRESCALAR);
	pEdit->GetWindowText(str, sizeof(str));
	if( strlen(str) == 0 ) {Skip=0; return;}
	ps = atoi(str);
	if (ps < 1 || ps > 255)	{
		AfxMessageBox("Range Error. PreScalar range can only be 1 to 255.");
		itoa(PreScalar,str,10);
		pEdit->SetWindowText(str);
	}
	else
	{
		PreScalar = ps;
		PeriodMax = (double)PreScalar * 0.001 * 2.0 * 256.0;
		sprintf(str,"%f",PeriodMax);
		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_FREQMAX);
		pEdit->SetWindowText(str);
		PeriodMin = (double)PreScalar * 0.001 * 2.0 * 2.0;
		sprintf(str,"%f",PeriodMin);
		pEdit = (CEdit*) GetDlgItem(IDC_EDIT_FREQMIN);
		pEdit->SetWindowText(str);
		CUsb.LoadPreScalar(PreScalar);
		Recalculate(GREENLED,1);
		Recalculate(REDLED,1);
		Recalculate(BLUELED,1);
	}	

	Skip =0;
	
	
}

void CUSBSignalDlg::OnOK() 
{
	// Default button used to capture the enter key. Does nothing!
	//CDialog::OnOK();
}

void CUSBSignalDlg::Recalculate(int Color, int Mode)
{

	char str[128];
	int	OnTime,OffTime;
	double d;
	CEdit* pPeriod;
	CEdit* pFreq;
	CEdit* pDuty;
	CEdit* pOnTime;
	CEdit* pOffTime;

	switch(Color) {
		case GREENLED :	pPeriod = (CEdit*) GetDlgItem(IDC_EDIT_GPERIOD);
						pFreq = (CEdit*) GetDlgItem(IDC_EDIT_GFREQ);
						pDuty = (CEdit*) GetDlgItem(IDC_EDIT_GDUTY);
						pOnTime = (CEdit*) GetDlgItem(IDC_EDIT_GONTIME);
						pOffTime = (CEdit*) GetDlgItem(IDC_EDIT_GOFFTIME);
						break;
		case REDLED :	pPeriod = (CEdit*) GetDlgItem(IDC_EDIT_RPERIOD);
						pFreq = (CEdit*) GetDlgItem(IDC_EDIT_RFREQ);
						pDuty = (CEdit*) GetDlgItem(IDC_EDIT_RDUTY);
						pOnTime = (CEdit*) GetDlgItem(IDC_EDIT_RONTIME);
						pOffTime = (CEdit*) GetDlgItem(IDC_EDIT_ROFFTIME);
						break;
		case BLUELED :	pPeriod = (CEdit*) GetDlgItem(IDC_EDIT_BPERIOD);
						pFreq = (CEdit*) GetDlgItem(IDC_EDIT_BFREQ);
						pDuty = (CEdit*) GetDlgItem(IDC_EDIT_BDUTY);
						pOnTime = (CEdit*) GetDlgItem(IDC_EDIT_BONTIME);
						pOffTime = (CEdit*) GetDlgItem(IDC_EDIT_BOFFTIME);
						break;
	}


	if( Mode ) {	// ranges good, calculate values and display
		pOnTime->GetWindowText(str,sizeof(str));
		OnTime = atoi(str);
		pOffTime->GetWindowText(str,sizeof(str));
		OffTime = atoi(str);
		d = (double)(OnTime + OffTime)*PreScalar*0.001;
		sprintf(str,"%.3f",d);
		pPeriod->SetWindowText(str);
		d = 1/d;
		sprintf(str,"%.3f",d);
		pFreq->SetWindowText(str);
		d = ((double)OnTime/(double)(OnTime+OffTime))*100.0;
		sprintf(str,"%.2f",d);
		pDuty->SetWindowText(str);
	}

	else {	// invalid range, display nothing
		pPeriod->SetWindowText("");
		pFreq->SetWindowText("");
		pDuty->SetWindowText("");
	}


}

void CUSBSignalDlg::CheckOnOffTimeRange(int Color)
{
	int OnTime,OffTime;
	char str[128];
	CEdit* pOnTime;
	CEdit* pOffTime;
	switch(Color) {
	case GREENLED : pOnTime  = (CEdit*) GetDlgItem(IDC_EDIT_GONTIME);
					pOffTime = (CEdit*) GetDlgItem(IDC_EDIT_GOFFTIME);
					break;
	case REDLED	:	pOnTime  = (CEdit*) GetDlgItem(IDC_EDIT_RONTIME);
					pOffTime = (CEdit*) GetDlgItem(IDC_EDIT_ROFFTIME);
					break;
	case BLUELED :	pOnTime  = (CEdit*) GetDlgItem(IDC_EDIT_BONTIME);
					pOffTime = (CEdit*) GetDlgItem(IDC_EDIT_BOFFTIME);
					break;
	}

	// first check OnTime
	pOnTime->GetWindowText(str, sizeof(str));
	if( strlen(str) == 0 ) {
		Recalculate(Color,0);
		return;
	}
	OnTime = atoi(str);
	if (OnTime < 1 || OnTime > 255)	{
		AfxMessageBox("Range Error. OnTime range can only be 1 to 255.");
		Recalculate(Color,0);
		return;
	}

	pOffTime->GetWindowText(str, sizeof(str));
	if( strlen(str) == 0 ) {
		Recalculate(Color,0);
		return;
	}
	OffTime = atoi(str);
	if (OffTime < 1 || OffTime > 255)	{
		AfxMessageBox("Range Error. OffTime range can only be 1 to 255.");
		Recalculate(Color,0);
		return;
	}

	// if we get here all the values were numbers and in range,
	// now load the value & recalculate the freq, period and duty.
	CUsb.LoadLedFreqDuty(Color,(unsigned char)OnTime,(unsigned char)OffTime);
	Recalculate(Color,1);

}


void CUSBSignalDlg::OnChangeGreen() 
{
	static int Skip = 0;
	if (Skip) return;	// skip if this code called it self.
	Skip = 1;
	CheckOnOffTimeRange(GREENLED);
	Skip =0;
}

void CUSBSignalDlg::OnChangeRed()
{
	static int Skip = 0;
	if (Skip) return;	// skip if this code called it self.
	Skip = 1;
	CheckOnOffTimeRange(REDLED);
	Skip =0;
}

void CUSBSignalDlg::OnChangeBlue()
{
	static int Skip = 0;
	if (Skip) return;	// skip if this code called it self.
	Skip = 1;
	CheckOnOffTimeRange(BLUELED);
	Skip =0;
}


void CUSBSignalDlg::OnChangeEditGoffset() 
{
	static int Skip = 0;
	if (Skip) return;	// skip if this code called it self.
	Skip = 1;
	CheckOffsetRange(GREENLED);
	Skip =0;
}

void CUSBSignalDlg::OnChangeEditRoffset() 
{
	static int Skip = 0;
	if (Skip) return;	// skip if this code called it self.
	Skip = 1;
	CheckOffsetRange(REDLED);
	Skip =0;
}

void CUSBSignalDlg::OnChangeEditBoffset() 
{
	static int Skip = 0;
	if (Skip) return;	// skip if this code called it self.
	Skip = 1;
	CheckOffsetRange(BLUELED);
	Skip =0;
}

void CUSBSignalDlg::OnButtonSync() 
{
	CEdit* pOffSet;
	int OffSet;
	char str[128];

	// reload the offset each time
	pOffSet  = (CEdit*) GetDlgItem(IDC_EDIT_GOFFSET);
	pOffSet->GetWindowText(str, sizeof(str));
	OffSet = atoi(str);
	CUsb.LoadInitialPhaseDelay(GREENLED,(unsigned char)OffSet);
	
	pOffSet  = (CEdit*) GetDlgItem(IDC_EDIT_ROFFSET);
	pOffSet->GetWindowText(str, sizeof(str));
	OffSet = atoi(str);
	CUsb.LoadInitialPhaseDelay(REDLED,(unsigned char)OffSet);

	pOffSet  = (CEdit*) GetDlgItem(IDC_EDIT_BOFFSET);
	pOffSet->GetWindowText(str, sizeof(str));
	OffSet = atoi(str);
	CUsb.LoadInitialPhaseDelay(BLUELED,(unsigned char)OffSet);

	// then send the sync	
	CUsb.SyncLeds();
	
}

void CUSBSignalDlg::CheckOffsetRange(int Color)
{
	int OffSet;
	char str[128];
	CEdit* pOffSet;
	switch(Color) {
	case GREENLED : pOffSet  = (CEdit*) GetDlgItem(IDC_EDIT_GOFFSET);
					break;
	case REDLED	:	pOffSet  = (CEdit*) GetDlgItem(IDC_EDIT_ROFFSET);
					break;
	case BLUELED :	pOffSet  = (CEdit*) GetDlgItem(IDC_EDIT_BOFFSET);
					break;
	}

	// first check OnTime
	pOffSet->GetWindowText(str, sizeof(str));
	if( strlen(str) == 0 ) {
		return;
	}
	OffSet = atoi(str);
	if (OffSet < 0 || OffSet > 255)	{
		AfxMessageBox("Range Error. OffSet range can only be 0 to 255.");
		return;
	}


}




void CUSBSignalDlg::OnButtonAStop() 
{
	CUsb.Buzzer(0,0,0,0,0);
}


void CUSBSignalDlg::OnButtonAStart() 
{
	double d,e;
	char str[128];
	CEdit* pEdit;
	pEdit = (CEdit*) GetDlgItem(IDC_EDIT_AFREQ);
	pEdit->GetWindowText(str,sizeof(str));
	d = fabs(atof(str));
	d = (1.0/(d*256E-6));
	if( modf(d,&e) >= 0.5) d+=1;
	if(d>255)	d = 255;
	if(d<1)		d = 1;
	int Freq = (int)d;

	d = 1.0/((double)Freq*256E-6);
	sprintf(str,"%.1f",d);
	pEdit = (CEdit*) GetDlgItem(IDC_EDIT_AFREQ);
	pEdit->SetWindowText(str);
	
	pEdit = (CEdit*) GetDlgItem(IDC_EDIT_AREPEAT);
	pEdit->GetWindowText(str,sizeof(str));
	int Repeat = atoi(str);
	
	pEdit = (CEdit*) GetDlgItem(IDC_EDIT_AONTIME);
	pEdit->GetWindowText(str,sizeof(str));
	int OnTime = atoi(str);
	
	pEdit = (CEdit*) GetDlgItem(IDC_EDIT_AOFFTIME);
	pEdit->GetWindowText(str,sizeof(str));
	int OffTime = atoi(str);
	
	CUsb.Buzzer(1,(unsigned char)Freq,(unsigned char)Repeat,(unsigned char)OnTime,(unsigned char)OffTime);
}

void CUSBSignalDlg::OnCheckAutoClear() 
{
	CButton* pButton = (CButton*) GetDlgItem(IDC_CHECK_AUTOCLEAR);
	CUsb.EnableAutoClear( pButton->GetCheck() );
}

void CUSBSignalDlg::OnCheckAutoConfirm() 
{
	CButton* pButton = (CButton*) GetDlgItem(IDC_CHECK_AUTOCONFIRM);
	CUsb.EnableAutoConfirm( pButton->GetCheck() );
}

void CUSBSignalDlg::OnChangeEditARepeat() 
{
	static int Skip = 0;
	if (Skip) return;	// skip if this code called it self.
	Skip = 1;
	int repeat;
	char str[128];
	CEdit* pEdit = (CEdit*) GetDlgItem(IDC_EDIT_AREPEAT);
	pEdit->GetWindowText(str, sizeof(str));
	if( strlen(str) == 0 ) {Skip=0; return;}
	repeat = atoi(str);
	if (repeat < 0 || repeat > 255)	{
		AfxMessageBox("Range Error. Repeat value range can only be 0 to 255.\nZero = Continuous tone, 255 = Continuous Cylce Tone.");
	}
	Skip = 0;
}

void CUSBSignalDlg::OnChangeEditAOffTime() 
{
	static int Skip = 0;
	if (Skip) return;	// skip if this code called it self.
	Skip = 1;
	int time;
	char str[128];
	CEdit* pEdit = (CEdit*) GetDlgItem(IDC_EDIT_AOFFTIME);
	pEdit->GetWindowText(str, sizeof(str));
	if( strlen(str) == 0 ) {Skip=0; return;}
	time = atoi(str);
	if (time < 1 || time > 255)	{
		AfxMessageBox("Range Error. Off time range can only be 1 to 255.");
	}
	Skip = 0;
}

void CUSBSignalDlg::OnChangeEditAOnTime() 
{
	static int Skip = 0;
	if (Skip) return;	// skip if this code called it self.
	Skip = 1;
	int time;
	char str[128];
	CEdit* pEdit = (CEdit*) GetDlgItem(IDC_EDIT_AONTIME);
	pEdit->GetWindowText(str, sizeof(str));
	if( strlen(str) == 0 ) {Skip=0; return;}
	time = atoi(str);
	if (time < 1 || time > 255)	{
		AfxMessageBox("Range Error. On time range can only be 1 to 255.");
	}
	Skip = 0;
}

// Process a right click help request 
void CUSBSignalDlg::OnContextMenu(CWnd* pWnd, CPoint point) 
{
	::WinHelp(pWnd->m_hWnd, theApp.m_pszHelpFilePath, HELP_CONTEXTMENU, (DWORD)HelpMap);
	
}


// Process an F1 or ? button help request
BOOL CUSBSignalDlg::OnHelpInfo(HELPINFO* pHelpInfo) 
{
	int i=0;
	while(HelpMap[i+1] != 0)
		if( HelpMap[i] == (DWORD)pHelpInfo->iCtrlId) break;
		else i+=2;

	// if there is no context help, then display the help file.
	if( HelpMap[i+1] == 0)
		::WinHelp((HWND)pHelpInfo->hItemHandle, theApp.m_pszHelpFilePath, HELP_CONTENTS, 0);
	else
		::WinHelp((HWND)pHelpInfo->hItemHandle, theApp.m_pszHelpFilePath, HELP_WM_HELP, (DWORD)HelpMap);

	
	//return CDialog::OnHelpInfo(pHelpInfo);
	return(1);
}


// Green Power Level Changed
void CUSBSignalDlg::OnChangeEditGpower() 
{
	static int Skip = 0;
	if (Skip) return;	// skip if this code called it self.
	Skip = 1;
	int power;
	char str[128];
	CEdit* pEdit = (CEdit*) GetDlgItem(IDC_EDIT_GPOWER);
	pEdit->GetWindowText(str, sizeof(str));
	if( strlen(str) == 0 ) {Skip=0; return;}
	power = atoi(str);
	if (power < 0 || power > 100)	{
		AfxMessageBox("Range Error. Power range can only be 0 to 100.");
		itoa(PreScalar,str,10);
		pEdit->SetWindowText(str);
	}
	else
	{
		CUsb.LoadPower(GREENLED,power);
		
	}	

	Skip =0;
	
}

// red Power Level Changed
void CUSBSignalDlg::OnChangeEditRpower() 
{
		static int Skip = 0;
	if (Skip) return;	// skip if this code called it self.
	Skip = 1;
	int power;
	char str[128];
	CEdit* pEdit = (CEdit*) GetDlgItem(IDC_EDIT_RPOWER);
	pEdit->GetWindowText(str, sizeof(str));
	if( strlen(str) == 0 ) {Skip=0; return;}
	power = atoi(str);
	if (power < 0 || power > 100)	{
		AfxMessageBox("Range Error. Power range can only be 0 to 100.");
		itoa(PreScalar,str,10);
		pEdit->SetWindowText(str);
	}
	else
	{
		CUsb.LoadPower(REDLED,power);
		
	}	

	Skip =0;
}

// Blue Power Level Changed
void CUSBSignalDlg::OnChangeEditBpower() 
{
		static int Skip = 0;
	if (Skip) return;	// skip if this code called it self.
	Skip = 1;
	int power;
	char str[128];
	CEdit* pEdit = (CEdit*) GetDlgItem(IDC_EDIT_BPOWER);
	pEdit->GetWindowText(str, sizeof(str));
	if( strlen(str) == 0 ) {Skip=0; return;}
	power = atoi(str);
	if (power < 0 || power > 100)	{
		AfxMessageBox("Range Error. PreScalar range can only be 0 to 100.");
		itoa(PreScalar,str,10);
		pEdit->SetWindowText(str);
	}
	else
	{
		CUsb.LoadPower(BLUELED,power);
		
	}	

	Skip =0;
}

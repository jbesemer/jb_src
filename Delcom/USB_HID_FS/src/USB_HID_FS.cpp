// USB_HID_FS.cpp : Defines the class behaviors for the application.
//

#include "stdafx.h"
#include "USB_HID_FS.h"
#include "USB_HID_FSDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CUSB_HID_FSApp

BEGIN_MESSAGE_MAP(CUSB_HID_FSApp, CWinApp)
	//{{AFX_MSG_MAP(CUSB_HID_FSApp)
	//}}AFX_MSG
	ON_COMMAND(ID_HELP, CWinApp::OnHelp)
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CUSB_HID_FSApp construction

CUSB_HID_FSApp::CUSB_HID_FSApp()
{
}

/////////////////////////////////////////////////////////////////////////////
// The one and only CUSB_HID_FSApp object

CUSB_HID_FSApp theApp;

/////////////////////////////////////////////////////////////////////////////
// CUSB_HID_FSApp initialization

BOOL CUSB_HID_FSApp::InitInstance()
{
	AfxEnableControlContainer();

	// Standard initialization

#ifdef _AFXDLL
	Enable3dControls();			// Call this when using MFC in a shared DLL
#else
	Enable3dControlsStatic();	// Call this when linking to MFC statically
#endif

	CUSB_HID_FSDlg dlg;
	m_pMainWnd = &dlg;
	int nResponse = dlg.DoModal();
	if (nResponse == IDOK)
	{
	}
	else if (nResponse == IDCANCEL)
	{
	}

	// Since the dialog has been closed, return FALSE so that we exit the
	//  application, rather than start the application's message pump.
	return FALSE;
}

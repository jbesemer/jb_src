// USB_HID_FS.h : main header file for the USB_HID_FS application
//

#if !defined(AFX_USB_HID_FS_H__FA435EFD_90A2_4473_B9CE_EA53EBE42DCE__INCLUDED_)
#define AFX_USB_HID_FS_H__FA435EFD_90A2_4473_B9CE_EA53EBE42DCE__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CUSB_HID_FSApp:
// See USB_HID_FS.cpp for the implementation of this class
//

class CUSB_HID_FSApp : public CWinApp
{
public:
	CUSB_HID_FSApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CUSB_HID_FSApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CUSB_HID_FSApp)
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_USB_HID_FS_H__FA435EFD_90A2_4473_B9CE_EA53EBE42DCE__INCLUDED_)

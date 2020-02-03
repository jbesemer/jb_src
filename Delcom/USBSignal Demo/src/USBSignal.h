// USBSignal.h : main header file for the USBSIGNAL application
//

#if !defined(AFX_USBSIGNAL_H__8487148C_B2B0_4FC2_A5DA_3D7EC1B86C94__INCLUDED_)
#define AFX_USBSIGNAL_H__8487148C_B2B0_4FC2_A5DA_3D7EC1B86C94__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CUSBSignalApp:
// See USBSignal.cpp for the implementation of this class
//

class CUSBSignalApp : public CWinApp
{
public:
	CUSBSignalApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CUSBSignalApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CUSBSignalApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_USBSIGNAL_H__8487148C_B2B0_4FC2_A5DA_3D7EC1B86C94__INCLUDED_)

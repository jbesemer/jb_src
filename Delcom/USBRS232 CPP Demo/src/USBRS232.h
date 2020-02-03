// USBRS232.h : main header file for the USBRS232 application
//

#if !defined(AFX_USBRS232_H__6325CFA8_C66D_44B2_8C9B_6192DC9542F6__INCLUDED_)
#define AFX_USBRS232_H__6325CFA8_C66D_44B2_8C9B_6192DC9542F6__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CUSBRS232App:
// See USBRS232.cpp for the implementation of this class
//

class CUSBRS232App : public CWinApp
{
public:
	CUSBRS232App();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CUSBRS232App)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CUSBRS232App)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_USBRS232_H__6325CFA8_C66D_44B2_8C9B_6192DC9542F6__INCLUDED_)

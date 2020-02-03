// USBRS232Dlg.h : header file
//

#if !defined(AFX_USBRS232DLG_H__FD291D91_C3CB_4EF1_887F_1C3D6B022D53__INCLUDED_)
#define AFX_USBRS232DLG_H__FD291D91_C3CB_4EF1_887F_1C3D6B022D53__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

/////////////////////////////////////////////////////////////////////////////
// CUSBRS232Dlg dialog

class CUSBRS232Dlg : public CDialog
{
// Construction
public:
	int Hex2Str(char* Buffer);
	bool DisplayMode;
	bool ConfigDevice(CString);
	CUSBRS232Dlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CUSBRS232Dlg)
	enum { IDD = IDD_USBRS232_DIALOG };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CUSBRS232Dlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	//{{AFX_MSG(CUSBRS232Dlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	virtual void OnCancel();
	afx_msg void OnSelchangeBaudrate();
	afx_msg void OnTimer(UINT nIDEvent);
	afx_msg void OnMode();
	afx_msg void OnSend();
	afx_msg void OnClearFlags();
	afx_msg void OnOnClearFlags();
	afx_msg void OnChangePollrate();
	virtual void OnOK();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_USBRS232DLG_H__FD291D91_C3CB_4EF1_887F_1C3D6B022D53__INCLUDED_)

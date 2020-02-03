// USBSignalDlg.h : header file
//

#if !defined(AFX_USBSIGNALDLG_H__C3E3C2CA_1C4C_4BC8_997C_0218DC0D4A81__INCLUDED_)
#define AFX_USBSIGNALDLG_H__C3E3C2CA_1C4C_4BC8_997C_0218DC0D4A81__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

/////////////////////////////////////////////////////////////////////////////
// CUSBSignalDlg dialog

class CUSBSignalDlg : public CDialog
{
// Construction
public:
	void CheckOffsetRange(int Color);
	void CheckOnOffTimeRange(int Color);
	void Recalculate(int Color, int Mode);
	double PeriodMin;
	double PeriodMax;
	unsigned char PreScalar;
	void GetSerialNumber();
	int BlueState;
	int RedState;
	int GreenState;
	CUSBSignalDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CUSBSignalDlg)
	enum { IDD = IDD_USBSIGNAL_DIALOG };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CUSBSignalDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	//{{AFX_MSG(CUSBSignalDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	afx_msg void OnDestroy();
	afx_msg void OnTimer(UINT nIDEvent);
	afx_msg void OnRadioGoff();
	afx_msg void OnRadioGon();
	afx_msg void OnRadioRflash();
	afx_msg void OnRadioGflash();
	afx_msg void OnRadioRoff();
	afx_msg void OnRadioRon();
	afx_msg void OnRadioBon();
	afx_msg void OnRadioBoff();
	afx_msg void OnRadioBflash();
	afx_msg void OnChangeGreen();
	afx_msg void OnChangeEditPrescalar();
	virtual void OnOK();
	afx_msg void OnChangeRed();
	afx_msg void OnChangeBlue();
	afx_msg void OnChangeEditGoffset();
	afx_msg void OnChangeEditRoffset();
	afx_msg void OnChangeEditBoffset();
	afx_msg void OnButtonSync();
	afx_msg void OnSelchangeComboDevice();
	afx_msg void OnButtonAStart();
	afx_msg void OnButtonAStop();
	afx_msg void OnCheckAutoClear();
	afx_msg void OnCheckAutoConfirm();
	afx_msg void OnChangeEditARepeat();
	afx_msg void OnChangeEditAOffTime();
	afx_msg void OnChangeEditAOnTime();
	afx_msg BOOL OnHelpInfo(HELPINFO* pHelpInfo);
	afx_msg void OnContextMenu(CWnd* pWnd, CPoint point);
	afx_msg void OnChangeEditGpower();
	afx_msg void OnChangeEditRpower();
	afx_msg void OnChangeEditBpower();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_USBSIGNALDLG_H__C3E3C2CA_1C4C_4BC8_997C_0218DC0D4A81__INCLUDED_)

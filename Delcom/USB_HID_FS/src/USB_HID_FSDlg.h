// USB_HID_FSDlg.h : header file
//

#if !defined(AFX_USB_HID_FSDLG_H__0EDB9F8C_7B47_4E35_8DAC_B19FA8321009__INCLUDED_)
#define AFX_USB_HID_FSDLG_H__0EDB9F8C_7B47_4E35_8DAC_B19FA8321009__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

/////////////////////////////////////////////////////////////////////////////
// CUSB_HID_FSDlg dialog

class CUSB_HID_FSDlg : public CDialog
{
// Construction
public:
	void GetReport(void);
	UINT FirmwareVersion;
	void GetFirmwareVersion(void);
	void PrepareForOverlappedTransfer(void);
	HANDLE ReadHandle;
	HANDLE DeviceHandle;
	bool ScanForHidDevice(void);
	bool DeviceFound;
	CUSB_HID_FSDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CUSB_HID_FSDlg)
	enum { IDD = IDD_USB_HID_FS_DIALOG };
		// NOTE: the ClassWizard will add data members here
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CUSB_HID_FSDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	//{{AFX_MSG(CUSB_HID_FSDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	virtual void OnCancel();
	afx_msg void OnTimer(UINT nIDEvent);
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_USB_HID_FSDLG_H__0EDB9F8C_7B47_4E35_8DAC_B19FA8321009__INCLUDED_)

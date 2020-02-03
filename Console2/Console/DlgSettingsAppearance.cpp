#include "stdafx.h"
#include "resource.h"

#include "DlgSettingsAppearance.h"

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

DlgSettingsAppearance::DlgSettingsAppearance(CComPtr<IXMLDOMElement>& pOptionsRoot)
: DlgSettingsBase(pOptionsRoot)
{
	IDD = IDD_SETTINGS_APPEARANCE;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

LRESULT DlgSettingsAppearance::OnInitDialog(UINT /*uMsg*/, WPARAM /*wParam*/, LPARAM /*lParam*/, BOOL& /*bHandled*/)
{
	m_windowSettings.Load(m_pOptionsRoot);
	m_fontSettings.Load(m_pOptionsRoot);
	m_positionSettings.Load(m_pOptionsRoot);

	m_strWindowTitle	= m_windowSettings.strTitle.c_str();
	m_nUseTabTitle		= m_windowSettings.bUseTabTitles ? 1 : 0;
	m_strWindowIcon		= m_windowSettings.strIcon.c_str();
	m_nUseTabIcon		= m_windowSettings.bUseTabIcon ? 1 : 0;
	m_nUseConsoleTitle	= m_windowSettings.bUseConsoleTitle ? 1 : 0;
	m_nShowCommand		= m_windowSettings.bShowCommand ? 1 : 0;
	m_nShowCommandTabs	= m_windowSettings.bShowCommandInTabs ? 1 : 0;

	m_strFontName	= m_fontSettings.strName.c_str();
	m_nFontBold		= m_fontSettings.bBold ? 1 : 0;
	m_nFontItalic	= m_fontSettings.bItalic ? 1 : 0;
	m_nUseFontColor	= m_fontSettings.bUseColor ? 1 : 0;

	m_nUsePosition	= ((m_positionSettings.nX == -1) && (m_positionSettings.nY == -1)) ? 0 : 1;
	m_nX			= ((m_positionSettings.nX == -1) && (m_positionSettings.nY == -1)) ? 0 : m_positionSettings.nX;
	m_nY			= ((m_positionSettings.nX == -1) && (m_positionSettings.nY == -1)) ? 0 : m_positionSettings.nY;

	m_nSnapToEdges	= (m_positionSettings.nSnapDistance == -1) ? 0 : 1;
	if (m_nSnapToEdges == 0) m_positionSettings.nSnapDistance = 0;

	m_nDocking		= static_cast<int>(m_positionSettings.dockPosition) + 1;
	m_nZOrder		= static_cast<int>(m_positionSettings.zOrder);

	CUpDownCtrl	spin;
	UDACCEL udAccel;

	spin.Attach(GetDlgItem(IDC_SPIN_FONT_SIZE));
	spin.SetRange(5, 36);
	spin.Detach();

	spin.Attach(GetDlgItem(IDC_SPIN_X));
	spin.SetRange(-2048, 2048);
	udAccel.nSec = 0;
	udAccel.nInc = 5;
	spin.SetAccel(1, &udAccel);
	spin.Detach();

	spin.Attach(GetDlgItem(IDC_SPIN_Y));
	spin.SetRange(-2048, 2048);
	udAccel.nSec = 0;
	udAccel.nInc = 5;
	spin.SetAccel(1, &udAccel);
	spin.Detach();

	spin.Attach(GetDlgItem(IDC_SPIN_SNAP));
	spin.SetRange(0, 20);
	spin.Detach();

	EnableControls();

	DoDataExchange(DDX_LOAD);
	return TRUE;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

LRESULT DlgSettingsAppearance::OnCtlColorStatic(UINT /*uMsg*/, WPARAM wParam, LPARAM lParam, BOOL& bHandled)
{
	CWindow		staticCtl(reinterpret_cast<HWND>(lParam));
	CDCHandle	dc(reinterpret_cast<HDC>(wParam));

	if (staticCtl.m_hWnd == GetDlgItem(IDC_FONT_COLOR))
	{
		CBrush	brush(::CreateSolidBrush(m_fontSettings.crFontColor));
		CRect	rect;

		staticCtl.GetClientRect(&rect);
		dc.FillRect(&rect, brush);
		return 0;
	}

	bHandled = FALSE;
	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

LRESULT DlgSettingsAppearance::OnCloseCmd(WORD /*wNotifyCode*/, WORD wID, HWND /*hWndCtl*/, BOOL& /*bHandled*/)
{
	if (wID == IDOK)
	{
		DoDataExchange(DDX_SAVE);

		m_windowSettings.strTitle		= m_strWindowTitle;
		m_windowSettings.bUseTabTitles	= (m_nUseTabTitle > 0);
		m_windowSettings.strIcon		= m_strWindowIcon;
		m_windowSettings.bUseTabIcon	= (m_nUseTabIcon > 0);
		m_windowSettings.bUseConsoleTitle= (m_nUseConsoleTitle > 0);
		m_windowSettings.bShowCommand	= (m_nShowCommand > 0);
		m_windowSettings.bShowCommandInTabs	= (m_nShowCommandTabs > 0);

		if (m_fontSettings.dwSize > 36) m_fontSettings.dwSize = 36;

		m_fontSettings.strName			= m_strFontName;
		m_fontSettings.bBold			= (m_nFontBold > 0);
		m_fontSettings.bItalic			= (m_nFontItalic > 0);
		m_fontSettings.bUseColor		= (m_nUseFontColor > 0);

		if (m_nUsePosition > 0)
		{
			m_positionSettings.nX = m_nX;
			m_positionSettings.nY = m_nY;

			if (m_positionSettings.nX == -1) m_positionSettings.nX = 0;
			if (m_positionSettings.nY == -1) m_positionSettings.nY = 0;

		}
		else
		{
			m_positionSettings.nX = -1;
			m_positionSettings.nY = -1;
		}

		if (m_nSnapToEdges == 0)
		{
			m_positionSettings.nSnapDistance = -1;
		}

		m_positionSettings.dockPosition	= static_cast<DockPosition>(m_nDocking - 1);
		m_positionSettings.zOrder		= static_cast<ZOrder>(m_nZOrder);

		WindowSettings&		windowSettings	= g_settingsHandler->GetAppearanceSettings().windowSettings;
		FontSettings&		fontSettings	= g_settingsHandler->GetAppearanceSettings().fontSettings;
		PositionSettings&	positionSettings= g_settingsHandler->GetAppearanceSettings().positionSettings;

		windowSettings.strTitle		= m_windowSettings.strTitle;
		windowSettings.bUseTabTitles= m_windowSettings.bUseTabTitles;
		windowSettings.strIcon		= m_windowSettings.strIcon;
		windowSettings.bUseTabIcon	= m_windowSettings.bUseTabIcon;
		windowSettings.bUseConsoleTitle= m_windowSettings.bUseConsoleTitle;
		windowSettings.bShowCommand	= m_windowSettings.bShowCommand;
		windowSettings.bShowCommandInTabs= m_windowSettings.bShowCommandInTabs;

		fontSettings.strName	= m_fontSettings.strName;
		fontSettings.dwSize		= m_fontSettings.dwSize;
		fontSettings.bBold		= m_fontSettings.bBold;
		fontSettings.bItalic	= m_fontSettings.bItalic;
		fontSettings.bUseColor	= m_fontSettings.bUseColor;
		fontSettings.crFontColor= m_fontSettings.crFontColor;

		positionSettings.nX				= m_positionSettings.nX;
		positionSettings.nY				= m_positionSettings.nY;

		positionSettings.nSnapDistance	= m_positionSettings.nSnapDistance;
		positionSettings.dockPosition	= m_positionSettings.dockPosition;
		positionSettings.zOrder			= m_positionSettings.zOrder;

		m_windowSettings.Save(m_pOptionsRoot);
		m_fontSettings.Save(m_pOptionsRoot);
		m_positionSettings.Save(m_pOptionsRoot);
	}

	DestroyWindow();
	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

LRESULT DlgSettingsAppearance::OnClickedBtnBrowseIcon(WORD /*wNotifyCode*/, WORD /*wID*/, HWND /*hWndCtl*/, BOOL& /*bHandled*/)
{
	DoDataExchange(DDX_SAVE);

	CFileDialog fileDialog(
					TRUE, 
					NULL, 
					NULL, 
					OFN_FILEMUSTEXIST|OFN_HIDEREADONLY|OFN_NOCHANGEDIR|OFN_PATHMUSTEXIST, 
					L"Icon Files (*.ico)\0*.ico\0\0");

	if (fileDialog.DoModal() == IDOK)
	{
		m_strWindowIcon = fileDialog.m_szFileName;
		DoDataExchange(DDX_LOAD);
	}

	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

LRESULT DlgSettingsAppearance::OnClickedBtnBrowseFont(WORD /*wNotifyCode*/, WORD /*wID*/, HWND /*hWndCtl*/, BOOL& /*bHandled*/)
{
	DoDataExchange(DDX_SAVE);

	LOGFONT	lf;
	::ZeroMemory(&lf, sizeof(LOGFONT));

	wcsncpy(lf.lfFaceName, LPCTSTR(m_strFontName), 32);
	lf.lfHeight	= -MulDiv(m_fontSettings.dwSize, GetDeviceCaps(::GetDC(NULL), LOGPIXELSY), 72);
	lf.lfWeight	= (m_nFontBold > 0) ? FW_BOLD : FW_NORMAL;
	lf.lfItalic	= static_cast<BYTE>(m_nFontItalic);

	CFontDialog	fontDlg(&lf);


	if (fontDlg.DoModal() == IDOK)
	{
		m_strFontName							= fontDlg.GetFaceName();// fontDlg.m_lf.lfFaceName;
		m_fontSettings.dwSize= static_cast<DWORD>(static_cast<double>(-fontDlg.m_lf.lfHeight*72)/static_cast<double>(GetDeviceCaps(::GetDC(NULL), LOGPIXELSY)) + 0.5);
		m_nFontBold								= fontDlg.IsBold() ? 1 : 0; //(fontDlg.m_lf.lfWeight == FW_BOLD) ? 1 : 0;
		m_nFontItalic							= fontDlg.IsItalic() ? 1 : 0; // fontDlg.m_lf.lfItalic;

		DoDataExchange(DDX_LOAD);
	}

	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

LRESULT DlgSettingsAppearance::OnClickedCheckbox(WORD /*wNotifyCode*/, WORD /*wID*/, HWND /*hWndCtl*/, BOOL& /*bHandled*/)
{
	DoDataExchange(DDX_SAVE);
	EnableControls();
	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

LRESULT DlgSettingsAppearance::OnClickedFontColor(WORD /*wNotifyCode*/, WORD /*wID*/, HWND hWndCtl, BOOL& /*bHandled*/)
{
	CColorDialog	dlg(m_fontSettings.crFontColor, CC_FULLOPEN);

	if (dlg.DoModal() == IDOK)
	{
		// update color
		m_fontSettings.crFontColor = dlg.GetColor();
		CWindow(hWndCtl).Invalidate();
	}

	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

void DlgSettingsAppearance::EnableControls()
{
	::EnableWindow(GetDlgItem(IDC_WINDOW_TITLE), FALSE);
	::EnableWindow(GetDlgItem(IDC_WINDOW_ICON), FALSE);
	::EnableWindow(GetDlgItem(IDC_BTN_BROWSE_ICON), FALSE);
	::EnableWindow(GetDlgItem(IDC_CHECK_SHOW_COMMAND), FALSE);
	::EnableWindow(GetDlgItem(IDC_CHECK_SHOW_COMMAND_TABS), FALSE);
	::EnableWindow(GetDlgItem(IDC_FONT_COLOR), FALSE);
	::EnableWindow(GetDlgItem(IDC_POS_X), FALSE);
	::EnableWindow(GetDlgItem(IDC_POS_Y), FALSE);
	::EnableWindow(GetDlgItem(IDC_SPIN_X), FALSE);
	::EnableWindow(GetDlgItem(IDC_SPIN_Y), FALSE);
	::EnableWindow(GetDlgItem(IDC_SNAP), FALSE);
	::EnableWindow(GetDlgItem(IDC_SPIN_SNAP), FALSE);

	if (m_nUseTabTitle == 0) ::EnableWindow(GetDlgItem(IDC_WINDOW_TITLE), TRUE);

	if (m_nUseTabIcon == 0)
	{
		::EnableWindow(GetDlgItem(IDC_WINDOW_ICON), TRUE);
		::EnableWindow(GetDlgItem(IDC_BTN_BROWSE_ICON), TRUE);
	}

	if (m_nUseConsoleTitle == 0)
	{
		::EnableWindow(GetDlgItem(IDC_CHECK_SHOW_COMMAND), TRUE);
		::EnableWindow(GetDlgItem(IDC_CHECK_SHOW_COMMAND_TABS), TRUE);
	}
	
	if (m_nUseFontColor > 0)
	{
		::EnableWindow(GetDlgItem(IDC_FONT_COLOR), TRUE);
	}

	if (m_nUsePosition > 0)
	{
		::EnableWindow(GetDlgItem(IDC_POS_X), TRUE);
		::EnableWindow(GetDlgItem(IDC_POS_Y), TRUE);
		::EnableWindow(GetDlgItem(IDC_SPIN_X), TRUE);
		::EnableWindow(GetDlgItem(IDC_SPIN_Y), TRUE);
	}

	if (m_nSnapToEdges > 0)
	{
		::EnableWindow(GetDlgItem(IDC_SNAP), TRUE);
		::EnableWindow(GetDlgItem(IDC_SPIN_SNAP), TRUE);
	}
}

//////////////////////////////////////////////////////////////////////////////

#pragma once

//////////////////////////////////////////////////////////////////////////////

#include "resource.h"
#include "ConsoleView.h"

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
class ConsoleViewContainer : public CMessageMap
{
	public:
		ConsoleViewContainer();
		virtual ~ConsoleViewContainer() {}

	public:

		BEGIN_MSG_MAP(ConsoleViewContainer)
			MESSAGE_HANDLER(WM_CREATE, OnCreate)
			MESSAGE_HANDLER(WM_ERASEBKGND, OnEraseBkgnd)
			MESSAGE_HANDLER(WM_ACTIVATEAPP, OnActivateApp)
			MESSAGE_HANDLER(WM_SYSCOMMAND, OnSysCommand)
			MESSAGE_HANDLER(WM_GETMINMAXINFO, OnGetMinMaxInfo)
			MESSAGE_HANDLER(WM_SIZE, OnSize)
			MESSAGE_HANDLER(WM_WINDOWPOSCHANGING, OnWindowPosChanging)
			MESSAGE_HANDLER(WM_EXITSIZEMOVE, OnExitSizeMove)
			MESSAGE_HANDLER(UM_CONSOLE_RESIZED, OnConsoleResized)
			COMMAND_ID_HANDLER(ID_COPY, OnCopy)
			COMMAND_ID_HANDLER(ID_PASTE, OnPaste)
		END_MSG_MAP()

		LRESULT OnCreate(UINT /*uMsg*/, WPARAM /*wParam*/, LPARAM /*lParam*/, BOOL& /*bHandled*/);
		LRESULT OnEraseBkgnd(UINT /*uMsg*/, WPARAM /*wParam*/, LPARAM /*lParam*/, BOOL& /*bHandled*/);
		LRESULT OnActivateApp(UINT /*uMsg*/, WPARAM wParam, LPARAM /*lParam*/, BOOL& bHandled);

		LRESULT OnSysCommand(UINT /*uMsg*/, WPARAM wParam, LPARAM /*lParam*/, BOOL& bHandled);

		LRESULT OnGetMinMaxInfo(UINT /*uMsg*/, WPARAM /*wParam*/, LPARAM lParam, BOOL& bHandled);
		LRESULT OnSize(UINT /*uMsg*/, WPARAM wParam, LPARAM lParam, BOOL& bHandled);
		LRESULT OnWindowPosChanging(UINT /*uMsg*/, WPARAM /*wParam*/, LPARAM lParam, BOOL& bHandled);
		LRESULT OnExitSizeMove(UINT /*uMsg*/, WPARAM /*wParam*/, LPARAM /*lParam*/, BOOL& /* bHandled */);

		LRESULT OnConsoleResized(UINT /*uMsg*/, WPARAM /*wParam*/, LPARAM /*lParam*/, BOOL& /* bHandled */);

		LRESULT OnCopy(WORD /*wNotifyCode*/, WORD /*wID*/, HWND /*hWndCtl*/, BOOL& /*bHandled*/);
		LRESULT OnPaste(WORD /*wNotifyCode*/, WORD /*wID*/, HWND /*hWndCtl*/, BOOL& /*bHandled*/);

	protected:


	protected:

};

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
ConsoleViewContainer<T>::ConsoleViewContainer()
: m_dwWindowWidth(0)
, m_dwWindowHeight(0)
, m_bRestoringWindow(false)
{

}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////
// Message handlers

template <typename T>
LRESULT ConsoleViewContainer<T>::OnCreate(UINT /*uMsg*/, WPARAM /*wParam*/, LPARAM /*lParam*/, BOOL& /*bHandled*/)
{
	T* pT = static_cast<T*>(this);

	CreateAcceleratorTable();
	SetTransparency();
	AdjustWindowSize(false);

	CRect rectWindow;
	pT->GetWindowRect(&rectWindow);

	m_dwWindowWidth	= rectWindow.right - rectWindow.left;
	m_dwWindowHeight= rectWindow.bottom - rectWindow.top;
	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
LRESULT ConsoleViewContainer<T>::OnEraseBkgnd(UINT /*uMsg*/, WPARAM /*wParam*/, LPARAM /*lParam*/, BOOL& /*bHandled*/)
{
	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
LRESULT ConsoleViewContainer<T>::OnActivateApp(UINT /*uMsg*/, WPARAM wParam, LPARAM /*lParam*/, BOOL& bHandled)
{
	T* pT = static_cast<T*>(this);

	TransparencySettings& transparencySettings = g_settingsHandler->GetAppearanceSettings().transparencySettings;

	if ((transparencySettings.transType == transAlpha) && 
		((transparencySettings.byActiveAlpha != 255) || (transparencySettings.byInactiveAlpha != 255)))
	{
		if (static_cast<BOOL>(wParam))
		{
			::SetLayeredWindowAttributes(pT->m_hWnd, RGB(0, 0, 0), transparencySettings.byActiveAlpha, LWA_ALPHA);
		}
		else
		{
			::SetLayeredWindowAttributes(pT->m_hWnd, RGB(0, 0, 0), transparencySettings.byInactiveAlpha, LWA_ALPHA);
		}
		
	}

	bHandled = FALSE;
	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
LRESULT ConsoleViewContainer<T>::OnSysCommand(UINT /*uMsg*/, WPARAM wParam, LPARAM /*lParam*/, BOOL& bHandled)
{
	// OnSize needs to know this
	if (wParam == SC_RESTORE)
	{
		m_bRestoringWindow = true;
	}
	else if (wParam == SC_MAXIMIZE)
	{
		T* pT = static_cast<T*>(this);

		CRect rectWindow;
		pT->GetWindowRect(&rectWindow);

		DWORD dwWindowWidth	= rectWindow.right - rectWindow.left;
		DWORD dwWindowHeight= rectWindow.bottom - rectWindow.top;

		if ((dwWindowWidth != m_dwWindowWidth) ||
			(dwWindowHeight != m_dwWindowHeight))
		{

			AdjustWindowSize(true);
		}
	}

	bHandled = FALSE;
	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
LRESULT ConsoleViewContainer<T>::OnGetMinMaxInfo(UINT /*uMsg*/, WPARAM /*wParam*/, LPARAM lParam, BOOL& bHandled)
{
	T* pT = static_cast<T*>(this);

	MINMAXINFO* pMinMax = (MINMAXINFO*)lParam;

	CRect					maxClientRect;
	shared_ptr<ConsoleView>	consoleView(pT->GetActiveView());

	if ((consoleView.get() == NULL) || (!consoleView->GetMaxRect(maxClientRect)))
	{
		bHandled = false;
		return 1;
	}

//	TRACE(L"minmax: (%i, %i) - (%i, %i)\n", maxClientRect.left, maxClientRect.top, maxClientRect.right, maxClientRect.bottom);

	pT->AdjustWindowRect(maxClientRect);

	pMinMax->ptMaxSize.x = maxClientRect.right - maxClientRect.left;
	pMinMax->ptMaxSize.y = maxClientRect.bottom - maxClientRect.top + 4;

	pMinMax->ptMaxTrackSize.x = pMinMax->ptMaxSize.x;
	pMinMax->ptMaxTrackSize.y = pMinMax->ptMaxSize.y;

	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
LRESULT ConsoleViewContainer<T>::OnSize(UINT /*uMsg*/, WPARAM wParam, LPARAM lParam, BOOL& bHandled)
{
	if (m_bRestoringWindow || (wParam == SIZE_MAXIMIZED))
	{
		T* pT = static_cast<T*>(this);

		CRect rectWindow;
		pT->GetWindowRect(&rectWindow);

		DWORD dwWindowWidth	= (m_bRestoringWindow) ? rectWindow.right - rectWindow.left : LOWORD(lParam);
		DWORD dwWindowHeight= (m_bRestoringWindow) ? rectWindow.bottom - rectWindow.top : HIWORD(lParam);

		if ((dwWindowWidth != m_dwWindowWidth) ||
			(dwWindowHeight != m_dwWindowHeight))
		{

			AdjustWindowSize(true);
		}

		m_bRestoringWindow = false;
	}

	bHandled = FALSE;
	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
LRESULT ConsoleViewContainer<T>::OnWindowPosChanging(UINT /*uMsg*/, WPARAM /*wParam*/, LPARAM lParam, BOOL& bHandled)
{
	T* pT = static_cast<T*>(this);

	WINDOWPOS*		pWinPos			= reinterpret_cast<WINDOWPOS*>(lParam);
	WindowSettings&	windowSettings	= g_settingsHandler->GetAppearanceSettings().windowSettings;

	if (windowSettings.zOrder == zorderOnBottom) pWinPos->hwndInsertAfter = HWND_BOTTOM;

	if (!(pWinPos->flags & SWP_NOMOVE))
	{
		pT->m_dockPosition	= dockNone;
		int nSnapDistance	= windowSettings.nSnapDistance;

		if (nSnapDistance >= 0)
		{
			CRect	rectMonitor;
			CRect	rectDesktop;
			CRect	rectWindow;
			CPoint	pointCursor;

			// we'll snap Console window to the desktop edges
			::GetCursorPos(&pointCursor);
			pT->GetWindowRect(&rectWindow);
			Helpers::GetDesktopRect(pointCursor, rectDesktop);
			Helpers::GetMonitorRect(pT->m_hWnd, rectMonitor);

			if (!rectMonitor.PtInRect(pointCursor))
			{
				pWinPos->x = pointCursor.x;
				pWinPos->y = pointCursor.y;
			}

			int	nLR = -1;
			int	nTB = -1;

			// now, see if we're close to the edges
			if (pWinPos->x <= rectDesktop.left + nSnapDistance)
			{
				pWinPos->x = rectDesktop.left;
				nLR = 0;
			}
			
			if (pWinPos->x >= rectDesktop.right - pWinPos->cx - nSnapDistance)
			{
				pWinPos->x = rectDesktop.right - pWinPos->cx;
				nLR = 1;
			}
			
			if (pWinPos->y <= rectDesktop.top + nSnapDistance)
			{
				pWinPos->y = rectDesktop.top;
				nTB = 0;
			}
			
			if (pWinPos->y >= rectDesktop.bottom - pWinPos->cy - nSnapDistance)
			{
				pWinPos->y = rectDesktop.bottom - pWinPos->cy;
				nTB = 2;
			}

			if ((nLR != -1) && (nTB != -1))
			{
				pT->m_dockPosition = static_cast<DockPosition>(nTB | nLR);
			}
		}


		// TODO: only for relative backgrounds
		CRect rectClient;
		pT->GetClientRect(&rectClient);
		pT->InvalidateRect(&rectClient, FALSE);
		return 0;
	}

	bHandled = FALSE;
	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
LRESULT ConsoleViewContainer<T>::OnExitSizeMove(UINT /*uMsg*/, WPARAM /*wParam*/, LPARAM /*lParam*/, BOOL& /*bHandled*/)
{
	T* pT = static_cast<T*>(this);

	CRect rectWindow;
	pT->GetWindowRect(&rectWindow);

	DWORD dwWindowWidth	= rectWindow.right - rectWindow.left;
	DWORD dwWindowHeight= rectWindow.bottom - rectWindow.top;

	if ((dwWindowWidth != m_dwWindowWidth) ||
		(dwWindowHeight != m_dwWindowHeight))
	{

		AdjustWindowSize(true);
	}

	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
LRESULT ConsoleViewContainer<T>::OnConsoleResized(UINT /*uMsg*/, WPARAM /*wParam*/, LPARAM /*lParam*/, BOOL& /* bHandled */)
{
	AdjustWindowSize(false);
	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
LRESULT ConsoleViewContainer<T>::OnCopy(WORD /*wNotifyCode*/, WORD /*wID*/, HWND /*hWndCtl*/, BOOL& /*bHandled*/)
{
	T* pT = static_cast<T*>(this);

	shared_ptr<ConsoleView>	consoleView(pT->GetActiveView());
	if (consoleView.get() == NULL) return 0;

	consoleView->Copy();

	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
LRESULT ConsoleViewContainer<T>::OnPaste(WORD /*wNotifyCode*/, WORD /*wID*/, HWND /*hWndCtl*/, BOOL& /*bHandled*/)
{
	T* pT = static_cast<T*>(this);

	shared_ptr<ConsoleView>	consoleView(pT->GetActiveView());
	if (consoleView.get() == NULL) return 0;

	consoleView->Paste();

	return 0;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
void ConsoleViewContainer<T>::AdjustWindowSize(bool bResizeConsole)
{
	T* pT = static_cast<T*>(this);

	CRect clientRect;
	pT->GetClientRect(&clientRect);

	if (bResizeConsole)
	{
		pT->AdjustAndResizeConsoleView(clientRect);
	}
	else
	{
		shared_ptr<ConsoleView>	consoleView(pT->GetActiveView());
		if (consoleView.get() == NULL) return;

		consoleView->GetRect(clientRect);
	}

	pT->AdjustWindowRect(clientRect);


	pT->SetWindowPos(
			0, 
			0, 
			0, 
			clientRect.right - clientRect.left, 
			clientRect.bottom - clientRect.top + 4, 
			SWP_NOMOVE|SWP_NOZORDER|SWP_NOSENDCHANGING);

	// update window width and height
	CRect rectWindow;

	pT->GetWindowRect(&rectWindow);
	m_dwWindowWidth	= rectWindow.right - rectWindow.left;
	m_dwWindowHeight= rectWindow.bottom - rectWindow.top;
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
void ConsoleViewContainer<T>::SetTransparency()
{
	T* pT = static_cast<T*>(this);

	// set transparency
	TransparencySettings& transparencySettings = g_settingsHandler->GetAppearanceSettings().transparencySettings;
	switch (transparencySettings.transType)
	{
		case transAlpha : 

			if ((transparencySettings.byActiveAlpha == 255) &&
				(transparencySettings.byInactiveAlpha == 255))
			{
				break;
			}

			::SetWindowLong(
					pT->m_hWnd, 
					GWL_EXSTYLE, 
					::GetWindowLong(pT->m_hWnd, GWL_EXSTYLE) | WS_EX_LAYERED);

			::SetLayeredWindowAttributes(
					pT->m_hWnd,
					0, 
					transparencySettings.byActiveAlpha, 
					LWA_ALPHA);

			break;

		case transColorKey :
		{
			::SetWindowLong(
					pT->m_hWnd, 
					GWL_EXSTYLE, 
					::GetWindowLong(pT->m_hWnd, GWL_EXSTYLE) | WS_EX_LAYERED);

			::SetLayeredWindowAttributes(
					pT->m_hWnd,
					transparencySettings.crColorKey, 
					transparencySettings.byActiveAlpha, 
					LWA_COLORKEY);

			break;
		}

		default :
		{
			::SetWindowLong(
					pT->m_hWnd, 
					GWL_EXSTYLE, 
					::GetWindowLong(pT->m_hWnd, GWL_EXSTYLE) & ~WS_EX_LAYERED);
		}


	}
}

//////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////

template <typename T>
void ConsoleViewContainer<T>::CreateAcceleratorTable()
{
	HotKeys&						hotKeys	= g_settingsHandler->GetHotKeys();
	HotKeys::HotKeysMap::iterator	it		= hotKeys.mapHotKeys.begin();
	shared_array<ACCEL>				accelTable(new ACCEL[hotKeys.mapHotKeys.size()]);

	for (size_t i = 0; it != hotKeys.mapHotKeys.end(); ++i, ++it)
	{
		::CopyMemory(&(accelTable[i]), &(it->second->accelHotkey), sizeof(ACCEL));
	}

	if (!m_acceleratorTable.IsNull()) m_acceleratorTable.DestroyObject();
	m_acceleratorTable.CreateAcceleratorTable(accelTable.get(), static_cast<int>(hotKeys.mapHotKeys.size()));
}

//////////////////////////////////////////////////////////////////////////////

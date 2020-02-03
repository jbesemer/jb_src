#! env python

import wx
import wx.aui

ID_ABOUT = 101
ID_EXIT  = 102

sampleList = ['zero', 'one', 'two', 'three', 'four', 'five',
		'six', 'seven', 'eight', 'nine', 'ten', 'eleven',
		'twelve', 'thirteen', 'fourteen']

class MyFriendsPanel(wx.Panel):
	def __init__( self, parent ):
		wx.Panel.__init__( self, parent, -1)

		self.lc = wx.ListCtrl( self )
		for item in sampleList:
			self.lc.Append( item)
			
		sizer = wx.BoxSizer()
		sizer.Add(self.lc, 1, wx.EXPAND)
		self.SetSizer(sizer)

class MySetupPanel(wx.Panel):
	def __init__( self, parent ):
		wx.Panel.__init__( self, parent, -1)
		
		lb = wx.CheckListBox(self, -1, (80, 50), wx.DefaultSize, sampleList)
		lb.SetSelection(0)
		self.lb = lb

		sizer = wx.BoxSizer()
		sizer.Add(self.lb, 1, wx.EXPAND)
		self.SetSizer(sizer)

#		self.Bind(wx.EVT_LISTBOX, self.EvtListBox, lb)
#		self.Bind(wx.EVT_CHECKLISTBOX, self.EvtCheckListBox, lb)


class MyHistoryPanel(wx.Panel):
	def __init__( self, parent ):
		wx.Panel.__init__( self, parent, -1)
		
		tb = wx.TextCtrl(self, value="History...", style=wx.TE_READONLY|wx.TE_MULTILINE)
		self.tb = tb

		sizer = wx.BoxSizer()
		sizer.Add(tb, 1, wx.EXPAND)
		self.SetSizer(sizer)

class MyFrame(wx.Frame):
	def __init__(self, parent, ID, title):
		wx.Frame.__init__(self, parent, ID, title,
						 wx.DefaultPosition, wx.Size(500, 650))
		self.CreateStatusBar()
		self.SetStatusText("This is the statusbar")

		menu = wx.Menu()
		menu.Append(ID_ABOUT, "&About", "More information about this program")
		menu.AppendSeparator()
		menu.Append(ID_EXIT, "E&xit", "Terminate the program")

		menuBar = wx.MenuBar()
		menuBar.Append(menu, "&File");

		self.SetMenuBar(menuBar)

		self.nb = wx.aui.AuiNotebook( self, style=wx.aui.AUI_NB_DEFAULT_STYLE&~wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)
		
		self.page1 = MyFriendsPanel(self.nb)
		self.nb.AddPage( self.page1, "Online")

		self.page2 = MySetupPanel(self.nb)
		self.nb.AddPage( self.page2, "Configuration" )

		self.page3 = MyHistoryPanel(self.nb)
		self.nb.AddPage( self.page3, "History" )

		sizer = wx.BoxSizer()
		sizer.Add(self.nb, 1, wx.EXPAND)
		self.SetSizer(sizer)


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, "SL Friends Online")
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()

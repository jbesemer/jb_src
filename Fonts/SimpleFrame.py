#########################################
# A simple SDI App framework.
#
#
# Creates a simple framed window app with a toolbar and a status bar.
# The middle of the window is filled with a single control.
# This is handy for unit-testing and other simple usage.


import wx
from SimpleSettings import SimpleSettings

# ------------------------------------------
# demo/default main frame

SMF_STATUSBAR = 1
SMF_TOOLBAR = 1
SMF_FRAME_ONLY = 0

class MainFrame( wx.Frame ):
	"""
		Frame with toolbar and status bar, features a control
		and saves/restores window position.
	"""
	def __init__( self, controlClass, style=SMF_TOOLBAR|SMF_STATUSBAR ):

		self.userStyle = style

		appName = wx.GetApp().GetName()
		self.settings = wx.GetApp().GetSettings()

		wx.Frame.__init__(
				self, None, -1, 
				pos=self.settings.GetPos((150,150)), 
				size=self.settings.GetSize((500,400)))

		# status bar / toolbar init - - - - - - - - - - - - - - - - - - - -

		if style & SMF_STATUSBAR:
			self.status = SimpleStatusBar( self )
			self.SetStatusBar( self.status )

		# Use the wxFrame internals to create the toolbar and associate it all
		# in one tidy method call.
		if style & SMF_TOOLBAR:
			self.toolbar = self.CreateToolBar( 
								wx.TB_HORIZONTAL
								 | wx.NO_BORDER
								 | wx.TB_FLAT
								 | wx.TB_TEXT
								 )
	
			self.toolbar.AddSeparator()
			self.toolbar.Realize()	# end toolbar init - - - - - - - - - -

		self.ctrl= controlClass( self )
		self.SetTitle( appName + " -- " + self.ctrl.GetName())

		self.Bind( wx.EVT_CLOSE, self.OnCloseWindow )
		self.Show(True)

	def OnCloseWindow(self, event):
		self.settings.SetPos( self.GetPositionTuple())
		self.settings.SetSize( self.GetSizeTuple())
		self.Destroy()

	def SetBusy( self, percent=10 ):
		if self.userStyle & SMF_STATUSBAR:
			self.status.SetBusy( percent )
		else:
			print "Working..."

	def SetDone( self ):
		if self.userStyle & SMF_STATUSBAR:
			self.status.SetDone()
		else:
			print "Done"
		
	def SetStatusText( self, text, panel=0 ):
		if self.userStyle & SMF_STATUSBAR:
			self.status.SetStatusText( text, panel )
		else:
			if panel:
				print "Status[%d]:" % panel, text
			else:
				print "Status:", text
		
	def GetSettings( self ):
		return self.settings


# ------------------------------------------
# demo/default status bar

class SimpleStatusBar(wx.StatusBar):
	
	def __init__(self, parent ):
		wx.StatusBar.__init__(self, parent, -1)

		# First N fields just text -- Last field is a gauge:
		self.guage = wx.Gauge( self, -1, 100, style=wx.GA_HORIZONTAL )

		# this is the default -- client may add extra fields
		self.SetFieldWidths([ -5, -1, -2 ])

		# bind events
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_IDLE, self.OnIdle)

	def SetFieldWidths( self, widths ):
		self.SetFieldsCount( len( widths ))
		self.SetStatusWidths( widths )
		self.RepositionGauge()

	def OnSize( self, evt ):
		self.RepositionGauge()  # for normal size events
		
		# Set a flag so the idle time handler will also do the repositioning.
		# It is done this way to get around a buglet where GetFieldRect is not
		# accurate during the EVT_SIZE resulting from a frame maximize.
		self.sizeChanged = True

	def OnIdle( self, evt ):
		if self.sizeChanged:
			self.RepositionGauge()

	def RepositionGauge( self ):
		rect = self.GetFieldRect( self.GetFieldsCount() - 1 )
		self.guage.SetPosition(( rect.x+2, rect.y+2 ))
		self.guage.SetSize(( rect.width, rect.height - 4 ))
		self.sizeChanged = False

	def SetBusy( self, percent=10 ):
		self.guage.SetValue( percent )
		self.Update()

	def SetDone( self ):
		self.guage.SetValue( 0 )
		self.Update()


# ------------------------------------------
# demo/command line app

class SimpleApp(wx.App):
	def __init__( self, name, mainControlClass, *largs, **kargs ):
		self.name = name
		self.mainControlClass = mainControlClass
		wx.App.__init__( self, *largs, **kargs )
		
	def OnInit(self):
		self.settings = SimpleSettings( self.GetName())
		frame = MainFrame( self.mainControlClass )
		self.SetTopWindow(frame)
		return True
		
	def OnExit( self ):
		self.settings.Save()
		
	def GetName( self ):
		return self.name
		
	def GetSettings( self ):
		return self.settings

def GetRedirect():
	""" conditionally set redirect flag OFF if launched from cmd line shell"""
	import os
	
	if "REDIRECT" in os.environ:
		return int( os.environ[ "REDIRECT" ])
	elif "PYTHON_REDIRECT" in os.environ:
		return int( os.environ[ "PYTHON_REDIRECT" ])
	else:
		# old heuristic
		return ( 'SHELL' not in os.environ 
			and 'PWD' not in os.environ 
			and 'PROMPT' not in os.environ )

if __name__ == "__main__":

		
	SimpleApp( "test", wx.TextCtrl, redirect=GetRedirect())			\
		.MainLoop()

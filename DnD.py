import  wx
import time

#----------------------------------------------------------------------
ID_CopyBtn	  = wx.NewId()
ID_PasteBtn	 = wx.NewId()
ID_BitmapBtn	= wx.NewId()

#----------------------------------------------------------------------

#----------------------------------------------------------------------


class MyFileDropTarget(wx.FileDropTarget):
	def __init__(self, window):
		wx.FileDropTarget.__init__(self)
		self.window = window

	def OnDropFiles(self, x, y, filenames):
		self.window.SetInsertionPointEnd()
		if 0:
			self.window.WriteText("\n%d file(s) dropped at %d,%d:\n" %
				(len(filenames), x, y))

		for file in filenames:
			self.window.WriteText(file + '\n')
			
		wx.GetApp().BeginProcessing()

class FileDropPanel(wx.Panel):
	def __init__(self, parent ):
		wx.Panel.__init__(self, parent, -1)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(
			wx.StaticText(self, -1, " \nFiles to be processed:"),
			0, wx.EXPAND|wx.ALL, 2
			)

		self.text = wx.TextCtrl(
						self, -1, "",
						style = wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY
						)

		dt = MyFileDropTarget(self )
		self.text.SetDropTarget(dt)
		sizer.Add(self.text, 1, wx.EXPAND)

		sizer.Add(
			wx.StaticText(self, -1, " \nFiles processed:"),
			0, wx.EXPAND|wx.ALL, 2
			)

		self.text2 = wx.TextCtrl(
						self, -1, "",
						style = wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY
						)

		if 0:
			dt = MyTextDropTarget(self.text2 )
			self.text2.SetDropTarget(dt)
		sizer.Add(self.text2, 1, wx.EXPAND)

		self.SetAutoLayout(True)
		self.SetSizer(sizer)


	def WriteText(self, text):
		self.text.WriteText(text)

	def SetInsertionPointEnd(self):
		self.text.SetInsertionPointEnd()
		
	def BeginProcessing( self ):
		while 1:
			line = self.text.GetLineText( 0 )
			if not line:
				break
			self.ProcessLine( line )
			self.text.Remove( 0, self.text.XYToPosition( 0, 1 ))

	def ProcessLine( self, line ):
		self.text2.SetInsertionPointEnd()
		self.text2.WriteText( line + "\n" )
#		time.sleep( 0.8 )


#----------------------------------------------------------------------
#----------------------------------------------------------------------

class MainFrame(wx.Frame):
	def __init__(self, parent, title ):
		wx.Frame.__init__(self, parent, -1, title=title )

		self.SetAutoLayout(True)
#		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.panel = FileDropPanel( self )
		sizer.Add( self.panel, 1, wx.EXPAND)
		self.SetSizer(sizer)

	def BeginProcessing( self ):
		self.panel.BeginProcessing()


if __name__ == '__main__':
	class MyApp(wx.App):
		def OnInit(self):
			frame = MainFrame( None, "DnD Example" )
			self.SetTopWindow(frame)
			frame.Show(True)
			return True

		def BeginProcessing( self ):
			self.GetTopWindow().BeginProcessing()
			
	app = MyApp( redirect=0 )
	app.MainLoop()


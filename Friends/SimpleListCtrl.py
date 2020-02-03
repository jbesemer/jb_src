#! env python

import sys
import  wx
import  wx.lib.mixins.listctrl  as  listmix

import images

class TestListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, ID, pos=wx.DefaultPosition,
						size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)


class SimpleListCtrlPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
		
		self.parent = parent
		tID = wx.NewId()

		self.list = TestListCtrl(self, tID,
								 style=wx.LC_REPORT 
								 #| wx.BORDER_SUNKEN
								 | wx.BORDER_NONE
								 | wx.LC_EDIT_LABELS
								 | wx.LC_SORT_ASCENDING
								 #| wx.LC_NO_HEADER
								 #| wx.LC_VRULES
								 #| wx.LC_HRULES
								 #| wx.LC_SINGLE_SEL
								 )

		self.il = wx.ImageList(16, 16)
		self.idx1 = self.il.Add(images.getSmilesBitmap())
		self.sm_up = self.il.Add(images.getSmallUpArrowBitmap())
		self.sm_dn = self.il.Add(images.getSmallDnArrowBitmap())

		self.list.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		sizer = wx.BoxSizer(wx.VERTICAL)

		sizer.Add(self.list, 1, wx.EXPAND)

		self.list.InsertColumn(0, "Artist")
		self.list.InsertColumn(1, "Title" ) #, wx.LIST_FORMAT_RIGHT)
		self.list.InsertColumn(2, "Genre")

		self.SetSizer(sizer)
		self.SetAutoLayout(True)

		width = parent.GetSize().GetWidth()
		print "WidthCol0", parent.settings.GetInt("WidthCol0", width/3)
		print "WidthCol1", parent.settings.GetInt("WidthCol1", width/3)
		print "WidthCol2", parent.settings.GetInt("WidthCol2", width/3)
		self.list.SetColumnWidth(0, parent.settings.GetInt("WidthCol0", width/3))
		self.list.SetColumnWidth(1, parent.settings.GetInt("WidthCol1", width/3))
		self.list.SetColumnWidth(2, parent.settings.GetInt("WidthCol2", width/3))
		print "WidthCol0", self.list.GetColumnWidth(0)
		print "WidthCol1", self.list.GetColumnWidth(1)
		print "WidthCol2", self.list.GetColumnWidth(2)

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self.list)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.list)
		self.Bind(wx.EVT_LIST_DELETE_ITEM, self.OnItemDelete, self.list)
		self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.list)
		self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.OnColRightClick, self.list)
		self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColBeginDrag, self.list)
		self.Bind(wx.EVT_LIST_COL_DRAGGING, self.OnColDragging, self.list)
		self.Bind(wx.EVT_LIST_COL_END_DRAG, self.OnColEndDrag, self.list)
		self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.list)

		self.list.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
		self.list.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

		# for wxMSW
		self.list.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

		# for wxGTK
		self.list.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

		
	def AppendRow(self, a,b,c):
		index = self.list.InsertImageStringItem(sys.maxint, a, self.idx1)
		self.list.SetStringItem(index, 1, b)
		self.list.SetStringItem(index, 2, c)

	# Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
	def GetListCtrl(self):
		return self.list

	# Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
	def GetSortImages(self):
		return (self.sm_dn, self.sm_up)

	def OnRightDown(self, event):
		x = event.GetX()
		y = event.GetY()
		print ("x, y = %s\n" % str((x, y)))
		item, flags = self.list.HitTest((x, y))

		if item != wx.NOT_FOUND and flags & wx.LIST_HITTEST_ONITEM:
			self.list.Select(item)

		event.Skip()

	def getColumnText(self, index, col):
		item = self.list.GetItem(index, col)
		return item.GetText()

	def OnItemSelected(self, event):
		##print event.GetItem().GetTextColour()
		self.currentItem = event.m_itemIndex
		print ("OnItemSelected: %s, %s, %s, %s\n" %
								(self.currentItem,
								self.list.GetItemText(self.currentItem),
								self.getColumnText(self.currentItem, 1),
								self.getColumnText(self.currentItem, 2)))

		if self.currentItem == 10:
			print ("OnItemSelected: Veto'd selection\n")
			#event.Veto()  # doesn't work
			# this does
			self.list.SetItemState(10, 0, wx.LIST_STATE_SELECTED)

		event.Skip()

	def OnItemDeselected(self, evt):
		item = evt.GetItem()
		print("OnItemDeselected: %d" % evt.m_itemIndex)

		# Show how to reselect something we don't want deselected
		if evt.m_itemIndex == 11:
			wx.CallAfter(self.list.SetItemState, 11, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

	def OnItemActivated(self, event):
		self.currentItem = event.m_itemIndex
		print("OnItemActivated: %s\nTopItem: %s" %
				(self.list.GetItemText(self.currentItem), self.list.GetTopItem()))

	def OnBeginEdit(self, event):
		print("OnBeginEdit")
		event.Allow()

	def OnItemDelete(self, event):
		print("OnItemDelete\n")

	def OnColClick(self, event):
		print("OnColClick: %d\n" % event.GetColumn())
		event.Skip()

	def OnColRightClick(self, event):
		item = self.list.GetColumn(event.GetColumn())
		print("OnColRightClick: %d %s\n" %
							(event.GetColumn(), (item.GetText(), item.GetAlign(),
							item.GetWidth(), item.GetImage())))

	def OnColBeginDrag(self, event):
		print("OnColBeginDrag\n")
		print "WidthCol0", self.list.GetColumnWidth(0)
		print "WidthCol1", self.list.GetColumnWidth(1)
		print "WidthCol2", self.list.GetColumnWidth(2)
		## Show how to not allow a column to be resized
		#if event.GetColumn() == 0:
		#    event.Veto()

	def OnColDragging(self, event):
		# print("OnColDragging\n")
		# print "WidthCol0", self.list.GetColumnWidth(0)
		# print "WidthCol1", self.list.GetColumnWidth(1)
		# print "WidthCol2", self.list.GetColumnWidth(2)
		pass

	def OnColEndDrag(self, event):
		print("OnColEndDrag\n")
		print "WidthCol0", self.list.GetColumnWidth(0)
		print "WidthCol1", self.list.GetColumnWidth(1)
		print "WidthCol2", self.list.GetColumnWidth(2)
		self.parent.settings.SetInt("WidthCol0", self.list.GetColumnWidth(0))
		self.parent.settings.SetInt("WidthCol1", self.list.GetColumnWidth(1))
		self.parent.settings.SetInt("WidthCol2", self.list.GetColumnWidth(2))

	def OnDoubleClick(self, event):
		print("OnDoubleClick item %s\n" % self.list.GetItemText(self.currentItem))
		event.Skip()

	def OnRightClick(self, event):
		print("OnRightClick %s\n" % self.list.GetItemText(self.currentItem))

		# only do this part the first time so the events are only bound once
		if not hasattr(self, "popupID1"):
			self.popupID1 = wx.NewId()
			self.popupID2 = wx.NewId()
			self.popupID3 = wx.NewId()
			self.popupID4 = wx.NewId()
			self.popupID5 = wx.NewId()
			self.popupID6 = wx.NewId()

			self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
			self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
			self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
			self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
			self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
			self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)

		# make a menu
		menu = wx.Menu()
		# add some items
		menu.Append(self.popupID1, "FindItem tests")
		menu.Append(self.popupID2, "Iterate Selected")
		menu.Append(self.popupID3, "ClearAll and repopulate")
		menu.Append(self.popupID4, "DeleteAllItems")
		menu.Append(self.popupID5, "GetItem")
		menu.Append(self.popupID6, "Edit")

		# Popup the menu.  If an item is selected then its handler
		# will be called before PopupMenu returns.
		self.PopupMenu(menu)
		menu.Destroy()


	def OnPopupOne(self, event):
		print("Popup one\n")
		print "FindItem:", self.list.FindItem(-1, "Roxette")
		print "FindItemData:", self.list.FindItemData(-1, 11)

	def OnPopupTwo(self, event):
		print("Selected items:\n")
		index = self.list.GetFirstSelected()

		while index != -1:
			print("      %s: %s\n" % (self.list.GetItemText(index), self.getColumnText(index, 1)))
			index = self.list.GetNextSelected(index)

	def OnPopupThree(self, event):
		print("Popup three\n")
		self.list.ClearAll()
		wx.CallAfter(self.PopulateList)

	def OnPopupFour(self, event):
		self.list.DeleteAllItems()

	def OnPopupFive(self, event):
		item = self.list.GetItem(self.currentItem)
		print item.m_text, item.m_itemId, self.list.GetItemData(self.currentItem)

	def OnPopupSix(self, event):
		self.list.EditLabel(self.currentItem)


#!/usr/bin/env python  
# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from ..util import load_img_path
from .macro import *

wxID_MAINFRAME = 1000

wxID_BUTTONSEND = 1002
wxID_BUTTONRECEIVE = 1003
wxID_TEXTCTRLADDRESS = 1004
wxID_BUTTONCOPY = 1005
wxID_BUTTONCHANGE = 1006


###########################################################################
## Class MainFrameBase
###########################################################################

class MainFrameBase(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wxID_MAINFRAME, title=u"Coin", pos=wx.DefaultPosition,
                          size=wx.Size(705, 484), style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

        self.m_menubar = wx.MenuBar(0)
        self.m_menubar.SetBackgroundColour(wx.Colour(240, 240, 240))

        self.m_menuFile = wx.Menu()
        self.m_menuFileExit = wx.MenuItem(self.m_menuFile, wx.ID_ANY, u"E&xit", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menuFile.AppendItem(self.m_menuFileExit)

        self.m_menubar.Append(self.m_menuFile, u"&File")

        self.m_menuOptions = wx.Menu()
        self.m_menuOptionsGenerateBitcoins = wx.MenuItem(self.m_menuOptions, wxID_OPTIONSGENERATEBITCOINS,
                                                         u"&Generate Coins", wx.EmptyString, wx.ITEM_CHECK)
        self.m_menuOptions.AppendItem(self.m_menuOptionsGenerateBitcoins)

        self.m_menuOptionsOptions = wx.MenuItem(self.m_menuOptions, wx.ID_ANY, u"&Options...", wx.EmptyString,
                                                wx.ITEM_NORMAL)
        self.m_menuOptions.AppendItem(self.m_menuOptionsOptions)

        self.m_menubar.Append(self.m_menuOptions, u"&Options")

        self.m_menuHelp = wx.Menu()
        self.m_menuHelpAbout = wx.MenuItem(self.m_menuHelp, wx.ID_ANY, u"&About...", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menuHelp.AppendItem(self.m_menuHelpAbout)

        self.m_menubar.Append(self.m_menuHelp, u"&Help")

        self.SetMenuBar(self.m_menubar)

        self.m_toolBar = self.CreateToolBar(wx.TB_FLAT | wx.TB_HORZ_TEXT, wx.ID_ANY)
        self.m_toolBar.SetToolBitmapSize(wx.Size(20, 20))
        self.m_toolBar.SetToolSeparation(1)
        self.m_toolBar.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, wx.EmptyString))

        bitmap_send = wx.Bitmap(load_img_path(u"send20.bmp"), wx.BITMAP_TYPE_BMP)
        bitmap_send.SetMask(wx.Mask(wx.Bitmap(load_img_path(u"send20mask.bmp"), wx.BITMAP_TYPE_BMP)))
        self.m_tool_sendconis = self.m_toolBar.AddLabelTool(wxID_BUTTONSEND, u"&Send Coins",
                                                            bitmap_send,
                                                            wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString,
                                                            wx.EmptyString, None)

        bitmap_addrbook = wx.Bitmap(load_img_path(u"addressbook20.bmp"), wx.BITMAP_TYPE_BMP)
        bitmap_addrbook.SetMask(wx.Mask(wx.Bitmap(load_img_path(u"addressbook20mask.bmp"), wx.BITMAP_TYPE_BMP)))
        self.m_tool_addrbook = self.m_toolBar.AddLabelTool(wxID_BUTTONRECEIVE, u"&Address Book",
                                                           bitmap_addrbook,
                                                           wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString,
                                                           wx.EmptyString, None)

        self.m_toolBar.Realize()

        self.m_statusBar = self.CreateStatusBar(1, wx.ST_SIZEGRIP, wx.ID_ANY)
        self.m_statusBar.SetBackgroundColour(wx.Colour(240, 240, 240))

        bSizer_main = wx.BoxSizer(wx.VERTICAL)

        bSizer_main.AddSpacer((0, 2), 0, wx.EXPAND, 5)

        bSizer_addr = wx.BoxSizer(wx.HORIZONTAL)

        self.m_statictext_addr = wx.StaticText(self, wx.ID_ANY, u"Your coin Address:", wx.DefaultPosition,
                                               wx.DefaultSize, 0)
        self.m_statictext_addr.Wrap(-1)
        bSizer_addr.Add(self.m_statictext_addr, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)

        self.m_textCtrl_addr = wx.TextCtrl(self, wxID_TEXTCTRLADDRESS, wx.EmptyString, wx.DefaultPosition,
                                           wx.Size(250, -1), wx.TE_READONLY)
        self.m_textCtrl_addr.SetMaxLength(0)
        self.m_textCtrl_addr.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))

        bSizer_addr.Add(self.m_textCtrl_addr, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)

        self.m_button_copy = wx.Button(self, wxID_BUTTONCOPY, u"&Copy to Clipboard", wx.DefaultPosition,
                                       wx.DefaultSize, wx.BU_EXACTFIT)
        bSizer_addr.Add(self.m_button_copy, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        self.m_button_change = wx.Button(self, wxID_BUTTONCHANGE, u"C&hange...", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer_addr.Add(self.m_button_change, 0, wx.RIGHT, 5)

        bSizer_addr.AddSpacer((0, 0), 0, wx.EXPAND, 5)

        bSizer_main.Add(bSizer_addr, 0, wx.EXPAND | wx.RIGHT | wx.LEFT, 5)

        bSizer_balance = wx.BoxSizer(wx.HORIZONTAL)

        self.m_panel_balance = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer_balance_inner = wx.BoxSizer(wx.HORIZONTAL)

        self.m_statictext_balance_title = wx.StaticText(self.m_panel_balance, wx.ID_ANY, u"Balance:",
                                                        wx.DefaultPosition, wx.Size(-1, 15), 0)
        self.m_statictext_balance_title.Wrap(-1)
        bSizer_balance_inner.Add(self.m_statictext_balance_title, 0,
                                 wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM | wx.LEFT, 5)

        self.m_statictext_balance = wx.StaticText(self.m_panel_balance, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                                  wx.Size(120, 15), wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE)
        self.m_statictext_balance.Wrap(-1)
        self.m_statictext_balance.SetFont(wx.Font(8, 70, 90, 90, False, wx.EmptyString))
        self.m_statictext_balance.SetBackgroundColour(wx.Colour(240, 240, 240))

        bSizer_balance_inner.Add(self.m_statictext_balance, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_panel_balance.SetSizer(bSizer_balance_inner)
        self.m_panel_balance.Layout()
        bSizer_balance_inner.Fit(self.m_panel_balance)
        bSizer_balance.Add(self.m_panel_balance, 1, wx.EXPAND | wx.ALIGN_BOTTOM | wx.ALL, 5)

        bSizer_balance.AddSpacer((0, 0), 0, wx.EXPAND, 5)

        m_choicefilterChoices = [u" All", u" Sent", u" Received", u" In Progress"]
        self.m_choicefilter = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(110, -1), m_choicefilterChoices, 0)
        self.m_choicefilter.SetSelection(0)
        self.m_choicefilter.Hide()

        bSizer_balance.Add(self.m_choicefilter, 0, wx.ALIGN_BOTTOM | wx.TOP | wx.RIGHT | wx.LEFT, 5)

        bSizer_main.Add(bSizer_balance, 0, wx.EXPAND, 5)

        self.m_notebook = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_panel_txs = wx.Panel(self.m_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer_txs = wx.BoxSizer(wx.VERTICAL)

        self.m_listCtrl_txs = wx.ListCtrl(self.m_panel_txs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                          wx.LC_NO_SORT_HEADER | wx.LC_REPORT | wx.LC_SORT_DESCENDING | wx.ALWAYS_SHOW_SB)
        bSizer_txs.Add(self.m_listCtrl_txs, 1, wx.EXPAND | wx.ALL, 5)

        self.m_panel_txs.SetSizer(bSizer_txs)
        self.m_panel_txs.Layout()
        bSizer_txs.Fit(self.m_panel_txs)
        self.m_notebook.AddPage(self.m_panel_txs, u"All Transactions", False)

        bSizer_main.Add(self.m_notebook, 1, wx.EXPAND, 5)

        bSizer_TabsForFutureUse = wx.BoxSizer(wx.VERTICAL)

        self.m_panel_escrows = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.m_panel_escrows.Hide()

        bSizer_escrows = wx.BoxSizer(wx.VERTICAL)

        self.m_listCtrl_escrows = wx.ListCtrl(self.m_panel_escrows, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                              wx.LC_NO_SORT_HEADER | wx.LC_REPORT)
        bSizer_escrows.Add(self.m_listCtrl_escrows, 1, wx.ALL | wx.EXPAND, 5)

        self.m_panel_escrows.SetSizer(bSizer_escrows)
        self.m_panel_escrows.Layout()
        bSizer_escrows.Fit(self.m_panel_escrows)
        bSizer_TabsForFutureUse.Add(self.m_panel_escrows, 1, wx.EXPAND | wx.ALL, 5)

        self.m_panel_orderssent = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.m_panel_orderssent.Hide()

        bSizer_orderssent = wx.BoxSizer(wx.VERTICAL)

        self.m_listCtrl_orderssent = wx.ListCtrl(self.m_panel_orderssent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                                 wx.LC_NO_SORT_HEADER | wx.LC_REPORT)
        bSizer_orderssent.Add(self.m_listCtrl_orderssent, 1, wx.ALL | wx.EXPAND, 5)

        self.m_panel_orderssent.SetSizer(bSizer_orderssent)
        self.m_panel_orderssent.Layout()
        bSizer_orderssent.Fit(self.m_panel_orderssent)
        bSizer_TabsForFutureUse.Add(self.m_panel_orderssent, 1, wx.EXPAND | wx.ALL, 5)

        self.m_panel_productssent = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.m_panel_productssent.Hide()

        bSizer_productssent = wx.BoxSizer(wx.VERTICAL)
        self.m_listCtrl_productssent = wx.ListCtrl(self.m_panel_productssent, wx.ID_ANY, wx.DefaultPosition,
                                                   wx.DefaultSize, wx.LC_NO_SORT_HEADER | wx.LC_REPORT)
        bSizer_productssent.Add(self.m_listCtrl_productssent, 1, wx.ALL | wx.EXPAND, 5)

        self.m_panel_productssent.SetSizer(bSizer_productssent)
        self.m_panel_productssent.Layout()
        bSizer_productssent.Fit(self.m_panel_productssent)
        bSizer_TabsForFutureUse.Add(self.m_panel_productssent, 1, wx.EXPAND | wx.ALL, 5)

        self.m_panel_ordersreceived = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.m_panel_ordersreceived.Hide()

        bSizer_ordersreceived = wx.BoxSizer(wx.VERTICAL)

        self.m_listCtrl_ordersreceived = wx.ListCtrl(self.m_panel_ordersreceived, wx.ID_ANY, wx.DefaultPosition,
                                                     wx.DefaultSize, wx.LC_NO_SORT_HEADER | wx.LC_REPORT)
        bSizer_ordersreceived.Add(self.m_listCtrl_ordersreceived, 1, wx.ALL | wx.EXPAND, 5)

        self.m_panel_ordersreceived.SetSizer(bSizer_ordersreceived)
        self.m_panel_ordersreceived.Layout()
        bSizer_ordersreceived.Fit(self.m_panel_ordersreceived)
        bSizer_TabsForFutureUse.Add(self.m_panel_ordersreceived, 1, wx.EXPAND | wx.ALL, 5)

        bSizer_main.Add(bSizer_TabsForFutureUse, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer_main)
        self.Layout()

        # Connect Events
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MENU, self.OnMenuFileExit, id=self.m_menuFileExit.GetId())
        self.Bind(wx.EVT_MENU, self.OnMenuOptionsGenerate, id=self.m_menuOptionsGenerateBitcoins.GetId())
        self.Bind(wx.EVT_MENU, self.OnMenuOptionsOptions, id=self.m_menuOptionsOptions.GetId())
        self.Bind(wx.EVT_MENU, self.OnMenuHelpAbout, id=self.m_menuHelpAbout.GetId())
        self.Bind(wx.EVT_TOOL, self.OnButtonSend, id=self.m_tool_sendconis.GetId())
        self.Bind(wx.EVT_TOOL, self.OnButtonAddressBook, id=self.m_tool_addrbook.GetId())
        self.m_textCtrl_addr.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrl_addr.Bind(wx.EVT_LEFT_DOWN, self.OnMouseEventsAddress)
        self.m_textCtrl_addr.Bind(wx.EVT_LEFT_UP, self.OnMouseEventsAddress)
        self.m_textCtrl_addr.Bind(wx.EVT_MIDDLE_DOWN, self.OnMouseEventsAddress)
        self.m_textCtrl_addr.Bind(wx.EVT_MIDDLE_UP, self.OnMouseEventsAddress)
        self.m_textCtrl_addr.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseEventsAddress)
        self.m_textCtrl_addr.Bind(wx.EVT_RIGHT_UP, self.OnMouseEventsAddress)
        self.m_textCtrl_addr.Bind(wx.EVT_MOTION, self.OnMouseEventsAddress)
        self.m_textCtrl_addr.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseEventsAddress)
        self.m_textCtrl_addr.Bind(wx.EVT_MIDDLE_DCLICK, self.OnMouseEventsAddress)
        self.m_textCtrl_addr.Bind(wx.EVT_RIGHT_DCLICK, self.OnMouseEventsAddress)
        self.m_textCtrl_addr.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseEventsAddress)
        self.m_textCtrl_addr.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEventsAddress)
        self.m_textCtrl_addr.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseEventsAddress)
        self.m_textCtrl_addr.Bind(wx.EVT_SET_FOCUS, self.OnSetFocusAddress)
        self.m_button_copy.Bind(wx.EVT_BUTTON, self.OnButtonCopy)
        self.m_button_change.Bind(wx.EVT_BUTTON, self.OnButtonChange)
        self.m_listCtrl_txs.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnListColBeginDrag)
        self.m_listCtrl_txs.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListItemActivatedAllTransactions)
        self.m_listCtrl_txs.Bind(wx.EVT_PAINT, self.OnPaintListCtrl)
        self.m_listCtrl_orderssent.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListItemActivatedOrdersSent)
        self.m_listCtrl_productssent.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListItemActivatedProductsSent)
        self.m_listCtrl_ordersreceived.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListItemActivatedOrdersReceived)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnClose(self, event):
        event.Skip()

    def OnIdle(self, event):
        event.Skip()

    def OnMouseEvents(self, event):
        event.Skip()

    def OnPaint(self, event):
        event.Skip()

    def OnMenuFileExit(self, event):
        event.Skip()

    def OnMenuOptionsGenerate(self, event):
        event.Skip()

    def OnMenuOptionsOptions(self, event):
        event.Skip()

    def OnMenuHelpAbout(self, event):
        event.Skip()

    def OnButtonSend(self, event):
        event.Skip()

    def OnButtonAddressBook(self, event):
        event.Skip()

    def OnKeyDown(self, event):
        event.Skip()

    def OnMouseEventsAddress(self, event):
        event.Skip()

    def OnSetFocusAddress(self, event):
        event.Skip()

    def OnButtonCopy(self, event):
        event.Skip()

    def OnButtonChange(self, event):
        event.Skip()

    def OnListColBeginDrag(self, event):
        event.Skip()

    def OnListItemActivatedAllTransactions(self, event):
        event.Skip()

    def OnPaintListCtrl(self, event):
        event.Skip()

    def OnListItemActivatedOrdersSent(self, event):
        event.Skip()

    def OnListItemActivatedProductsSent(self, event):
        event.Skip()

    def OnListItemActivatedOrdersReceived(self, event):
        event.Skip()


def main():
    pass


if __name__ == '__main__':
    main()

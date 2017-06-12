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

wxID_OPENNEWTABLE = 1000


###########################################################################
## Class PokerLobbyDialogBase
###########################################################################

class PokerLobbyDialogBase(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Poker Lobby", pos=wx.DefaultPosition,
                          size=wx.Size(586, 457), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

        bSizer_main = wx.BoxSizer(wx.HORIZONTAL)

        self.m_treeCtrl = wx.TreeCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                      wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT)
        self.m_treeCtrl.SetMinSize(wx.Size(130, -1))

        bSizer_main.Add(self.m_treeCtrl, 0, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT, 5)

        bSizer172 = wx.BoxSizer(wx.VERTICAL)

        self.m_listCtrl = wx.ListCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                      wx.LC_NO_SORT_HEADER | wx.LC_REPORT)
        bSizer172.Add(self.m_listCtrl, 1, wx.EXPAND | wx.ALL, 5)

        self.m_button_newtable = wx.Button(self, wxID_OPENNEWTABLE, u"&Open New Table", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        bSizer172.Add(self.m_button_newtable, 0, wx.ALL, 5)

        bSizer_main.Add(bSizer172, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer_main)
        self.Layout()

        # Connect Events
        self.m_treeCtrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelChanged)
        self.m_listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListItemActivated)
        self.m_listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListItemSelected)
        self.m_button_newtable.Bind(wx.EVT_BUTTON, self.OnButtonNewTable)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnTreeSelChanged(self, event):
        event.Skip()

    def OnListItemActivated(self, event):
        event.Skip()

    def OnListItemSelected(self, event):
        event.Skip()

    def OnButtonNewTable(self, event):
        event.Skip()


wxID_DEALHAND = 1000
wxID_FOLD = 1001
wxID_CALL = 1002
wxID_RAISE = 1003
wxID_LEAVETABLE = 1004
wxID_DITCHPLAYER = 1005


###########################################################################
## Class PokerDialogBase
###########################################################################

class PokerDialogBase(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Poker", pos=wx.DefaultPosition, size=wx.Size(806, 550),
                          style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_NO_TASKBAR | wx.FULL_REPAINT_ON_RESIZE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer_main = wx.BoxSizer(wx.VERTICAL)

        self.m_check_sitout = wx.CheckBox(self, wx.ID_ANY, u"Deal Me Out", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer_main.Add(self.m_check_sitout, 0, wx.ALL, 5)

        self.m_button_dealhand = wx.Button(self, wxID_DEALHAND, u"&Deal Hand", wx.DefaultPosition, wx.Size(150, 25), 0)
        bSizer_main.Add(self.m_button_dealhand, 0, wx.ALL, 5)

        self.m_button_fold = wx.Button(self, wxID_FOLD, u"&Fold", wx.DefaultPosition, wx.Size(80, 25), 0)
        bSizer_main.Add(self.m_button_fold, 0, wx.ALL, 5)

        self.m_button_call = wx.Button(self, wxID_CALL, u"&Call", wx.DefaultPosition, wx.Size(80, 25), 0)
        bSizer_main.Add(self.m_button_call, 0, wx.ALL, 5)

        self.m_button_raise = wx.Button(self, wxID_RAISE, u"&Raise", wx.DefaultPosition, wx.Size(80, 25), 0)
        bSizer_main.Add(self.m_button_raise, 0, wx.ALL, 5)

        self.m_button_leavetable = wx.Button(self, wxID_LEAVETABLE, u"&Leave Table", wx.DefaultPosition,
                                             wx.Size(90, 25), 0)
        bSizer_main.Add(self.m_button_leavetable, 0, wx.ALL, 5)

        self.m_text_ditchplayer = wx.TextCtrl(self, wxID_DITCHPLAYER, wx.EmptyString, wx.DefaultPosition,
                                              wx.Size(45, -1), wx.TE_PROCESS_ENTER)
        self.m_text_ditchplayer.SetMaxLength(0)
        bSizer_main.Add(self.m_text_ditchplayer, 0, wx.ALL, 5)

        self.m_check_pre_fold = wx.CheckBox(self, wx.ID_ANY, u"FOLD", wx.DefaultPosition, wx.Size(100, -1), 0)
        bSizer_main.Add(self.m_check_pre_fold, 0, wx.ALL, 5)

        self.m_check_pre_call = wx.CheckBox(self, wx.ID_ANY, u"CALL", wx.DefaultPosition, wx.Size(100, -1), 0)
        bSizer_main.Add(self.m_check_pre_call, 0, wx.ALL, 5)

        self.m_check_pre_callany = wx.CheckBox(self, wx.ID_ANY, u"CALL ANY", wx.DefaultPosition, wx.Size(100, -1), 0)
        bSizer_main.Add(self.m_check_pre_callany, 0, wx.ALL, 5)

        self.m_check_pre_raise = wx.CheckBox(self, wx.ID_ANY, u"RAISE", wx.DefaultPosition, wx.Size(100, -1), 0)
        bSizer_main.Add(self.m_check_pre_raise, 0, wx.ALL, 5)

        self.m_check_pre_raiseany = wx.CheckBox(self, wx.ID_ANY, u"RAISE ANY", wx.DefaultPosition, wx.Size(100, -1), 0)
        bSizer_main.Add(self.m_check_pre_raiseany, 0, wx.ALL, 5)

        self.SetSizer(bSizer_main)
        self.Layout()
        self.m_statusBar = self.CreateStatusBar(1, wx.ST_SIZEGRIP, wx.ID_ANY)

        # Connect Events
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.m_check_sitout.Bind(wx.EVT_CHECKBOX, self.OnCheckSitOut)
        self.m_button_dealhand.Bind(wx.EVT_BUTTON, self.OnButtonDealHand)
        self.m_button_fold.Bind(wx.EVT_BUTTON, self.OnButtonFold)
        self.m_button_call.Bind(wx.EVT_BUTTON, self.OnButtonCall)
        self.m_button_raise.Bind(wx.EVT_BUTTON, self.OnButtonRaise)
        self.m_button_leavetable.Bind(wx.EVT_BUTTON, self.OnButtonLeaveTable)
        self.m_text_ditchplayer.Bind(wx.EVT_TEXT_ENTER, self.OnDitchPlayer)
        self.m_check_pre_fold.Bind(wx.EVT_CHECKBOX, self.OnCheckPreFold)
        self.m_check_pre_call.Bind(wx.EVT_CHECKBOX, self.OnCheckPreCall)
        self.m_check_pre_callany.Bind(wx.EVT_CHECKBOX, self.OnCheckPreCallAny)
        self.m_check_pre_raise.Bind(wx.EVT_CHECKBOX, self.OnCheckPreRaise)
        self.m_check_pre_raiseany.Bind(wx.EVT_CHECKBOX, self.OnCheckPreRaiseAny)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnClose(self, event):
        event.Skip()

    def OnMouseEvents(self, event):
        event.Skip()

    def OnPaint(self, event):
        event.Skip()

    def OnSize(self, event):
        event.Skip()

    def OnCheckSitOut(self, event):
        event.Skip()

    def OnButtonDealHand(self, event):
        event.Skip()

    def OnButtonFold(self, event):
        event.Skip()

    def OnButtonCall(self, event):
        event.Skip()

    def OnButtonRaise(self, event):
        event.Skip()

    def OnButtonLeaveTable(self, event):
        event.Skip()

    def OnDitchPlayer(self, event):
        event.Skip()

    def OnCheckPreFold(self, event):
        event.Skip()

    def OnCheckPreCall(self, event):
        event.Skip()

    def OnCheckPreCallAny(self, event):
        event.Skip()

    def OnCheckPreRaise(self, event):
        event.Skip()

    def OnCheckPreRaiseAny(self, event):
        event.Skip()


def main():
    pass


if __name__ == '__main__':
    main()

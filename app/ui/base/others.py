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

wxID_TEXTCTRL = 1000


###########################################################################
## Class GetTextFromUserDialogBase
###########################################################################

class GetTextFromUserDialogBase(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                           size=wx.Size(403, 138), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer_container = wx.BoxSizer(wx.VERTICAL)

        bSizer_main = wx.BoxSizer(wx.VERTICAL)

        bSizer_main.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self.m_staticText_msg1 = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_msg1.Wrap(-1)
        bSizer_main.Add(self.m_staticText_msg1, 0, wx.TOP | wx.RIGHT | wx.LEFT, 5)

        self.m_textCtrl1 = wx.TextCtrl(self, wxID_TEXTCTRL, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                       wx.TE_PROCESS_ENTER)
        self.m_textCtrl1.SetMaxLength(0)
        bSizer_main.Add(self.m_textCtrl1, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.m_staticText_msg2 = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_msg2.Wrap(-1)
        self.m_staticText_msg2.Hide()

        bSizer_main.Add(self.m_staticText_msg2, 0, wx.TOP | wx.RIGHT | wx.LEFT, 5)

        self.m_textCtrl2 = wx.TextCtrl(self, wxID_TEXTCTRL, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                       wx.TE_PROCESS_ENTER)
        self.m_textCtrl2.SetMaxLength(0)
        self.m_textCtrl2.Hide()

        bSizer_main.Add(self.m_textCtrl2, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 5)

        bSizer_main.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        bSizer_container.Add(bSizer_main, 1, wx.EXPAND | wx.ALL, 10)

        bSizer_btns = wx.BoxSizer(wx.HORIZONTAL)

        bSizer_btns.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self.m_button_ok = wx.Button(self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_button_ok.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_ok, 0, wx.ALL, 5)

        self.m_button_cancel = wx.Button(self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_cancel.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_cancel, 0, wx.ALL, 5)

        bSizer_container.Add(bSizer_btns, 0, wx.EXPAND, 5)

        self.SetSizer(bSizer_container)
        self.Layout()

        # Connect Events
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.m_textCtrl1.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrl2.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_button_ok.Bind(wx.EVT_BUTTON, self.OnButtonOK)
        self.m_button_cancel.Bind(wx.EVT_BUTTON, self.OnButtonCancel)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnClose(self, event):
        event.Skip()

    def OnKeyDown(self, event):
        event.Skip()

    def OnButtonOK(self, event):
        event.Skip()

    def OnButtonCancel(self, event):
        event.Skip()


def main():
    pass


if __name__ == '__main__':
    main()

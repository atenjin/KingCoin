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
import wx.html


###########################################################################
## Class TxDetailsDialogBase
###########################################################################

class TxDetailsDialogBase(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Transaction Details", pos=wx.DefaultPosition,
                           size=wx.Size(620, 450), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer_htmlwin = wx.BoxSizer(wx.VERTICAL)

        bSizer_htmlwin = wx.BoxSizer(wx.VERTICAL)

        self.m_htmlwin = wx.html.HtmlWindow(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                            wx.html.HW_SCROLLBAR_AUTO)
        bSizer_htmlwin.Add(self.m_htmlwin, 1, wx.ALL | wx.EXPAND, 5)

        bSizer_htmlwin.Add(bSizer_htmlwin, 1, wx.EXPAND, 5)

        bSizer_btns = wx.BoxSizer(wx.VERTICAL)

        self.m_button_ok = wx.Button(self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.Size(85, 25), 0)
        bSizer_btns.Add(self.m_button_ok, 0, wx.ALL, 5)

        bSizer_htmlwin.Add(bSizer_btns, 0, wx.ALIGN_RIGHT, 5)

        self.SetSizer(bSizer_htmlwin)
        self.Layout()

        # Connect Events
        self.m_button_ok.Bind(wx.EVT_BUTTON, self.OnButtonOK)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnButtonOK(self, event):
        event.Skip()


def main():
    pass


if __name__ == '__main__':
    main()

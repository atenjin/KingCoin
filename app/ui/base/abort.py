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


###########################################################################
## Class AboutDialogBase
###########################################################################

class AboutDialogBase(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"About XXcoin", pos=wx.DefaultPosition,
                           size=wx.Size(514, 404), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer60 = wx.BoxSizer(wx.VERTICAL)

        bSizer62 = wx.BoxSizer(wx.HORIZONTAL)

        bSizer62.AddSpacer((60, 0), 0, wx.EXPAND, 5)

        bSizer63 = wx.BoxSizer(wx.VERTICAL)

        bSizer63.AddSpacer((0, 50), 0, wx.EXPAND, 5)

        bSizer64 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText40 = wx.StaticText(self, wx.ID_ANY, u"XXcoin ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText40.Wrap(-1)
        self.m_staticText40.SetFont(wx.Font(10, 74, 90, 92, False, "Tahoma"))

        bSizer64.Add(self.m_staticText40, 0, wx.ALIGN_BOTTOM | wx.TOP | wx.BOTTOM | wx.LEFT, 5)

        self.m_staticTextVersion = wx.StaticText(self, wx.ID_ANY, u"version", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextVersion.Wrap(-1)
        self.m_staticTextVersion.SetFont(wx.Font(10, 74, 90, 90, False, "Tahoma"))

        bSizer64.Add(self.m_staticTextVersion, 0, wx.ALIGN_BOTTOM | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)

        bSizer63.Add(bSizer64, 0, wx.EXPAND, 5)

        bSizer63.AddSpacer((0, 4), 0, wx.EXPAND, 5)

        self.m_staticTextMain = wx.StaticText(self, wx.ID_ANY,
                                              u"Copyright © 2017 Atom King.\n\nThis is experimental software. \nI just use this project to undersatand how bitcon working.\nDo not rely on it for actual financial transactions.\n\nDistributed under the MIT/X11 software license, see the accompanying file license.txt or http://www.opensource.org/licenses/mit-license.php.\n\nThis product includes software developed by the OpenSSL Project for use in the OpenSSL Toolkit (http://www.openssl.org/)",
                                              wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextMain.Wrap(400)
        bSizer63.Add(self.m_staticTextMain, 0, wx.ALL, 5)

        bSizer63.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        bSizer62.Add(bSizer63, 1, wx.EXPAND, 5)

        bSizer60.Add(bSizer62, 1, wx.EXPAND, 5)

        bSizer61 = wx.BoxSizer(wx.HORIZONTAL)

        bSizer61.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self.m_buttonOK = wx.Button(self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.Size(85, 25), 0)
        bSizer61.Add(self.m_buttonOK, 0, wx.ALL, 5)

        bSizer60.Add(bSizer61, 0, wx.ALIGN_RIGHT | wx.EXPAND, 5)

        self.SetSizer(bSizer60)
        self.Layout()

        # Connect Events
        self.m_buttonOK.Bind(wx.EVT_BUTTON, self.OnButtonOK)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnButtonOK(self, event):
        event.Skip()


def main():
    pass


if __name__ == '__main__':
    main()

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

wxID_TRANSACTIONFEE = 1000


###########################################################################
## Class OptionsDialogBase
###########################################################################

class OptionsDialogBase(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Options", pos=wx.DefaultPosition, size=wx.Size(500, 261),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer_container = wx.BoxSizer(wx.VERTICAL)

        bSizer_options_main = wx.BoxSizer(wx.VERTICAL)

        bSizer_options_main.AddSpacer((0, 20), 0, wx.EXPAND, 5)

        self.m_staticText32 = wx.StaticText(self, wx.ID_ANY,
                                            u"Optional transaction fee you give to the nodes that process your transactions.",
                                            wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText32.Wrap(-1)
        bSizer_options_main.Add(self.m_staticText32, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        bSizer_tx_fee = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText_tx_fee = wx.StaticText(self, wx.ID_ANY, u"Transaction fee:", wx.DefaultPosition,
                                                 wx.DefaultSize, 0)
        self.m_staticText_tx_fee.Wrap(-1)
        bSizer_tx_fee.Add(self.m_staticText_tx_fee, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM | wx.LEFT, 5)

        self.m_textCtrl_tx_fee = wx.TextCtrl(self, wxID_TRANSACTIONFEE, wx.EmptyString, wx.DefaultPosition,
                                             wx.Size(-1, -1), 0)
        self.m_textCtrl_tx_fee.SetMaxLength(0)
        bSizer_tx_fee.Add(self.m_textCtrl_tx_fee, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL | wx.EXPAND | wx.SHAPED, 5)

        bSizer_options_main.Add(bSizer_tx_fee, 0, wx.EXPAND, 5)

        bSizer_container.Add(bSizer_options_main, 1, wx.EXPAND | wx.LEFT, 5)

        bSizer_btns = wx.BoxSizer(wx.HORIZONTAL)

        self.m_button_ok = wx.Button(self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.Size(85, 25), 0)
        bSizer_btns.Add(self.m_button_ok, 0, wx.ALL, 5)

        self.m_button_cancel = wx.Button(self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_button_cancel.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_cancel, 0, wx.ALL, 5)

        bSizer_container.Add(bSizer_btns, 0, wx.ALIGN_RIGHT, 5)

        self.SetSizer(bSizer_container)
        self.Layout()

        # Connect Events
        self.m_textCtrl_tx_fee.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusTransactionFee)
        self.m_button_ok.Bind(wx.EVT_BUTTON, self.OnButtonOK)
        self.m_button_cancel.Bind(wx.EVT_BUTTON, self.OnButtonCancel)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnKillFocusTransactionFee(self, event):
        event.Skip()

    def OnButtonOK(self, event):
        event.Skip()

    def OnButtonCancel(self, event):
        event.Skip()


def main():
    pass


if __name__ == '__main__':
    main()

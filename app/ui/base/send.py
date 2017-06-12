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
from app import config as cfg
from ..util import *

wxID_TEXTCTRLPAYTO = 1000
wxID_BUTTONPASTE = 1001
wxID_BUTTONADDRESSBOOK = 1002
wxID_TEXTCTRLAMOUNT = 1003
wxID_CHOICETRANSFERTYPE = 1004
wxID_BUTTONSEND = 1005


###########################################################################
## Class SendDialogBase
###########################################################################

class SendDialogBase(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Send Coins", pos=wx.DefaultPosition,
                           size=wx.Size(730, 350), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer_main = wx.BoxSizer(wx.VERTICAL)

        bSizer_main.AddSpacer((0, 5), 0, wx.EXPAND, 5)

        fgSizer = wx.FlexGridSizer(4, 2, 0, 0)
        fgSizer.AddGrowableCol(1)
        fgSizer.SetFlexibleDirection(wx.BOTH)
        fgSizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fgSizer.AddSpacer((0, 0), 0, wx.EXPAND, 5)

        self.m_staticText = wx.StaticText(self, wx.ID_ANY,
                                          u"Enter the recipient's IP address (e.g. 123.45.6.7:%d) for online transfer with comments and confirmation, \nor bitcoin address (e.g. 1NS17iag9jJgTHD1VXjvLCEnZuQ3rJED9L) if recipient is not online." % cfg.DEFAULT_PORT,
                                          wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText.Wrap(-1)
        fgSizer.Add(self.m_staticText, 0, wx.TOP | wx.RIGHT | wx.LEFT, 5)

        bSizer_payto = wx.BoxSizer(wx.HORIZONTAL)

        bSizer_payto.SetMinSize(wx.Size(70, -1))

        bSizer_payto.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self.m_bitmapCheckMark = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(load_img_path(u"check.ico"), wx.BITMAP_TYPE_ANY),
                                                 wx.DefaultPosition, wx.Size(16, 16), 0)
        bSizer_payto.Add(self.m_bitmapCheckMark, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_staticText36 = wx.StaticText(self, wx.ID_ANY, u"Pay &To:", wx.DefaultPosition, wx.Size(-1, -1),
                                            wx.ALIGN_RIGHT)
        self.m_staticText36.Wrap(-1)
        bSizer_payto.Add(self.m_staticText36, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM | wx.LEFT, 5)

        fgSizer.Add(bSizer_payto, 1, wx.EXPAND | wx.LEFT, 5)

        bSizer_payto2 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_textCtrl_addr = wx.TextCtrl(self, wxID_TEXTCTRLPAYTO, wx.EmptyString, wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_textCtrl_addr.SetMaxLength(0)
        bSizer_payto2.Add(self.m_textCtrl_addr, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_button_paste = wx.Button(self, wxID_BUTTONPASTE, u"&Paste", wx.DefaultPosition, wx.Size(-1, -1),
                                        wx.BU_EXACTFIT)
        bSizer_payto2.Add(self.m_button_paste, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        self.m_button_addr = wx.Button(self, wxID_BUTTONADDRESSBOOK, u" Address &Book...", wx.DefaultPosition,
                                       wx.DefaultSize, 0)
        bSizer_payto2.Add(self.m_button_addr, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        fgSizer.Add(bSizer_payto2, 1, wx.EXPAND | wx.RIGHT, 5)

        self.m_staticText_amount = wx.StaticText(self, wx.ID_ANY, u"&Amount:", wx.DefaultPosition, wx.Size(-1, -1),
                                                 wx.ALIGN_RIGHT)
        self.m_staticText_amount.Wrap(-1)
        fgSizer.Add(self.m_staticText_amount, 0,
                    wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_RIGHT, 5)

        self.m_textCtrl_amount = wx.TextCtrl(self, wxID_TEXTCTRLAMOUNT, wx.EmptyString, wx.DefaultPosition,
                                             wx.Size(145, -1), 0)
        self.m_textCtrl_amount.SetMaxLength(20)
        self.m_textCtrl_amount.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, wx.EmptyString))

        fgSizer.Add(self.m_textCtrl_amount, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_staticText_transfer = wx.StaticText(self, wx.ID_ANY, u"T&ransfer:", wx.DefaultPosition, wx.Size(-1, -1),
                                                   wx.ALIGN_RIGHT)
        self.m_staticText_transfer.Wrap(-1)
        fgSizer.Add(self.m_staticText_transfer, 0,
                    wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM | wx.LEFT, 5)

        m_choice_transfer_typeChoices = [u" Standard"]
        self.m_choice_transfer_type = wx.Choice(self, wxID_CHOICETRANSFERTYPE, wx.DefaultPosition, wx.DefaultSize,
                                                m_choice_transfer_typeChoices, 0)
        self.m_choice_transfer_type.SetSelection(0)
        fgSizer.Add(self.m_choice_transfer_type, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        bSizer_main.Add(fgSizer, 0, wx.EXPAND | wx.LEFT, 5)

        bSizer_from = wx.BoxSizer(wx.HORIZONTAL)

        bSizer_from_main = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText_from = wx.StaticText(self, wx.ID_ANY, u"&From:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_from.Wrap(-1)
        bSizer_from_main.Add(self.m_staticText_from, 0, wx.BOTTOM | wx.LEFT, 5)

        self.m_textCtrl_from = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_textCtrl_from.SetMaxLength(0)
        bSizer_from_main.Add(self.m_textCtrl_from, 0, wx.LEFT | wx.EXPAND, 5)

        bSizer_from.Add(bSizer_from_main, 1, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)

        bSizer_main.Add(bSizer_from, 0, wx.EXPAND, 5)

        bSizer_msg = wx.BoxSizer(wx.HORIZONTAL)

        bSizer_msg_main = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText_msg = wx.StaticText(self, wx.ID_ANY, u"&Message:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_msg.Wrap(-1)
        bSizer_msg_main.Add(self.m_staticText_msg, 0, wx.TOP | wx.BOTTOM | wx.LEFT, 5)

        self.m_textCtrl_msg = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                          wx.TE_MULTILINE)
        self.m_textCtrl_msg.SetMaxLength(0)
        bSizer_msg_main.Add(self.m_textCtrl_msg, 1, wx.EXPAND | wx.LEFT, 5)

        bSizer_msg.Add(bSizer_msg_main, 1, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)

        bSizer_main.Add(bSizer_msg, 1, wx.EXPAND, 5)

        bSizer_btns = wx.BoxSizer(wx.HORIZONTAL)

        bSizer_btns.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self.m_button_send = wx.Button(self, wxID_BUTTONSEND, u"&Send", wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_button_send.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, wx.EmptyString))
        self.m_button_send.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_send, 0, wx.ALL, 5)

        self.m_button_cancel = wx.Button(self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_button_cancel.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_cancel, 0, wx.ALL, 5)

        bSizer_main.Add(bSizer_btns, 0, wx.EXPAND, 5)

        self.SetSizer(bSizer_main)
        self.Layout()

        # Connect Events
        self.m_textCtrl_addr.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrl_addr.Bind(wx.EVT_TEXT, self.OnTextAddress)
        self.m_button_paste.Bind(wx.EVT_BUTTON, self.OnButtonPaste)
        self.m_button_addr.Bind(wx.EVT_BUTTON, self.OnButtonAddressBook)
        self.m_textCtrl_amount.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrl_amount.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusAmount)
        self.m_textCtrl_from.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrl_msg.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_button_send.Bind(wx.EVT_BUTTON, self.OnButtonSend)
        self.m_button_cancel.Bind(wx.EVT_BUTTON, self.OnButtonCancel)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnKeyDown(self, event):
        event.Skip()

    def OnTextAddress(self, event):
        event.Skip()

    def OnButtonPaste(self, event):
        event.Skip()

    def OnButtonAddressBook(self, event):
        event.Skip()

    def OnKillFocusAmount(self, event):
        event.Skip()

    def OnButtonSend(self, event):
        event.Skip()

    def OnButtonCancel(self, event):
        event.Skip()


class SendingDialogBase(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Sending...", pos=wx.DefaultPosition,
                           size=wx.Size(442, 151), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer_main = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText_sending = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(-1, 14),
                                                  0)
        self.m_staticText_sending.Wrap(-1)
        bSizer_main.Add(self.m_staticText_sending, 0,
                        wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, 8)

        self.m_textCtrl_status = wx.TextCtrl(self, wx.ID_ANY, u"\n\nConnecting...", wx.DefaultPosition, wx.DefaultSize,
                                             wx.TE_CENTRE | wx.TE_MULTILINE | wx.TE_NO_VSCROLL | wx.TE_READONLY | wx.NO_BORDER)
        self.m_textCtrl_status.SetMaxLength(0)
        self.m_textCtrl_status.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

        bSizer_main.Add(self.m_textCtrl_status, 1, wx.EXPAND | wx.RIGHT | wx.LEFT, 10)

        bSizer_btns = wx.BoxSizer(wx.HORIZONTAL)

        bSizer_btns.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self.m_button_ok = wx.Button(self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_ok.Enable(False)
        self.m_button_ok.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_ok, 0, wx.ALL, 5)

        self.m_button_cancel = wx.Button(self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_button_cancel.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_cancel, 0, wx.ALL, 5)

        bSizer_main.Add(bSizer_btns, 0, wx.EXPAND, 5)

        self.SetSizer(bSizer_main)
        self.Layout()

        # Connect Events
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.m_button_ok.Bind(wx.EVT_BUTTON, self.OnButtonOK)
        self.m_button_cancel.Bind(wx.EVT_BUTTON, self.OnButtonCancel)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnClose(self, event):
        event.Skip()

    def OnPaint(self, event):
        event.Skip()

    def OnButtonOK(self, event):
        event.Skip()

    def OnButtonCancel(self, event):
        event.Skip()


def main():
    pass


if __name__ == '__main__':
    main()

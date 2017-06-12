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

wxID_LISTCTRL = 1000
wxID_BUTTONRENAME = 1001
wxID_BUTTONNEW = 1002
wxID_BUTTONCOPY = 1003


###########################################################################
## Class YourAddressDialogBase
###########################################################################

class YourAddressDialogBase(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Your coin Address", pos=wx.DefaultPosition,
                           size=wx.Size(610, 390), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer_main = wx.BoxSizer(wx.VERTICAL)

        bSizer_main.AddSpacer((0, 5), 0, wx.EXPAND, 5)

        self.m_staticText45 = wx.StaticText(self, wx.ID_ANY,
                                            u"These are your Bitcoin addresses for receiving payments.\nYou may want to give a different one to each sender so you can keep track of who is paying you.",
                                            wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText45.Wrap(600)
        bSizer_main.Add(self.m_staticText45, 0, wx.ALL, 5)

        self.m_listCtrl = wx.ListCtrl(self, wxID_LISTCTRL, wx.DefaultPosition, wx.DefaultSize,
                                      wx.LC_NO_SORT_HEADER | wx.LC_REPORT | wx.LC_SORT_ASCENDING)
        bSizer_main.Add(self.m_listCtrl, 1, wx.ALL | wx.EXPAND, 5)

        bSizer_btns = wx.BoxSizer(wx.HORIZONTAL)

        bSizer_btns.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self.m_button_rename = wx.Button(self, wxID_BUTTONRENAME, u"&Rename...", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_rename.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_rename, 0, wx.ALL, 5)

        self.m_button_new = wx.Button(self, wxID_BUTTONNEW, u"&New Address...", wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_button_new.SetMinSize(wx.Size(110, 25))

        bSizer_btns.Add(self.m_button_new, 0, wx.ALL, 5)

        self.m_button_copy = wx.Button(self, wxID_BUTTONCOPY, u"&Copy to Clipboard", wx.DefaultPosition,
                                       wx.Size(-1, -1), 0)
        self.m_button_copy.SetMinSize(wx.Size(120, 25))

        bSizer_btns.Add(self.m_button_copy, 0, wx.ALL, 5)

        self.m_button_ok = wx.Button(self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.DefaultSize, 0)
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
        self.m_listCtrl.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnListEndLabelEdit)
        self.m_listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListItemActivated)
        self.m_listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListItemSelected)
        self.m_button_rename.Bind(wx.EVT_BUTTON, self.OnButtonRename)
        self.m_button_new.Bind(wx.EVT_BUTTON, self.OnButtonNew)
        self.m_button_copy.Bind(wx.EVT_BUTTON, self.OnButtonCopy)
        self.m_button_ok.Bind(wx.EVT_BUTTON, self.OnButtonOK)
        self.m_button_cancel.Bind(wx.EVT_BUTTON, self.OnButtonCancel)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnClose(self, event):
        event.Skip()

    def OnListEndLabelEdit(self, event):
        event.Skip()

    def OnListItemActivated(self, event):
        event.Skip()

    def OnListItemSelected(self, event):
        event.Skip()

    def OnButtonRename(self, event):
        event.Skip()

    def OnButtonNew(self, event):
        event.Skip()

    def OnButtonCopy(self, event):
        event.Skip()

    def OnButtonOK(self, event):
        event.Skip()

    def OnButtonCancel(self, event):
        event.Skip()


wxID_ADDRBOOK_LISTCTRL = 1000
wxID_ADDRBOOK_BUTTONEDIT = 1001
wxID_ADDRBOOK_BUTTONNEW = 1002
wxID_ADDRBOOK_BUTTONDELETE = 1003


class AddressBookDialogBase(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Address Book", pos=wx.DefaultPosition,
                           size=wx.Size(610, 390), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer_main = wx.BoxSizer(wx.VERTICAL)

        bSizer_main.AddSpacer((0, 5), 0, wx.EXPAND, 5)

        self.m_staticText_coinaddr = wx.StaticText(self, wx.ID_ANY, u"Coin Address", wx.DefaultPosition,
                                                   wx.DefaultSize, 0)
        self.m_staticText_coinaddr.Wrap(-1)
        self.m_staticText_coinaddr.Hide()

        bSizer_main.Add(self.m_staticText_coinaddr, 0, wx.TOP | wx.RIGHT | wx.LEFT, 5)

        self.m_listCtrl = wx.ListCtrl(self, wxID_ADDRBOOK_LISTCTRL, wx.DefaultPosition, wx.DefaultSize,
                                      wx.LC_NO_SORT_HEADER | wx.LC_REPORT | wx.LC_SORT_ASCENDING)
        bSizer_main.Add(self.m_listCtrl, 1, wx.ALL | wx.EXPAND, 5)

        bSizer_btns = wx.BoxSizer(wx.HORIZONTAL)

        bSizer_btns.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self.m_button_edit = wx.Button(self, wxID_ADDRBOOK_BUTTONEDIT, u"&Edit...", wx.DefaultPosition, wx.DefaultSize,
                                       0)
        self.m_button_edit.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_edit, 0, wx.ALL, 5)

        self.m_button_new = wx.Button(self, wxID_ADDRBOOK_BUTTONNEW, u"&New Address...", wx.DefaultPosition,
                                      wx.DefaultSize, 0)
        self.m_button_new.SetMinSize(wx.Size(110, 25))

        bSizer_btns.Add(self.m_button_new, 0, wx.ALL, 5)

        self.m_button_delete = wx.Button(self, wxID_ADDRBOOK_BUTTONDELETE, u"&Delete", wx.DefaultPosition,
                                         wx.DefaultSize, 0)
        self.m_button_delete.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_delete, 0, wx.ALL, 5)

        self.m_button_ok = wx.Button(self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.Size(-1, -1), 0)
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
        self.m_listCtrl.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnListEndLabelEdit)
        self.m_listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListItemActivated)
        self.m_listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListItemSelected)
        self.m_button_edit.Bind(wx.EVT_BUTTON, self.OnButtonEdit)
        self.m_button_new.Bind(wx.EVT_BUTTON, self.OnButtonNew)
        self.m_button_delete.Bind(wx.EVT_BUTTON, self.OnButtonDelete)
        self.m_button_ok.Bind(wx.EVT_BUTTON, self.OnButtonOK)
        self.m_button_cancel.Bind(wx.EVT_BUTTON, self.OnButtonCancel)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnClose(self, event):
        event.Skip()

    def OnListEndLabelEdit(self, event):
        event.Skip()

    def OnListItemActivated(self, event):
        event.Skip()

    def OnListItemSelected(self, event):
        event.Skip()

    def OnButtonEdit(self, event):
        event.Skip()

    def OnButtonNew(self, event):
        event.Skip()

    def OnButtonDelete(self, event):
        event.Skip()

    def OnButtonOK(self, event):
        event.Skip()

    def OnButtonCancel(self, event):
        event.Skip()


def main():
    pass


if __name__ == '__main__':
    main()

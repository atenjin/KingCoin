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
import wx.richtext


###########################################################################
## Class ProductsDialogBase
###########################################################################

class ProductsDialogBase(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Marketplace", pos=wx.DefaultPosition,
                           size=wx.Size(708, 535), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer_main = wx.BoxSizer(wx.VERTICAL)

        bSizer_category = wx.BoxSizer(wx.HORIZONTAL)

        m_comboBoxCategoryChoices = [u"(Any Category)"]
        self.m_comboBox_category = wx.ComboBox(self, wx.ID_ANY, u"(Any Category)", wx.DefaultPosition, wx.Size(150, -1),
                                               m_comboBoxCategoryChoices, 0)
        bSizer_category.Add(self.m_comboBox_category, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_textCtrl_search = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_textCtrl_search.SetMaxLength(0)
        bSizer_category.Add(self.m_textCtrl_search, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_button_search = wx.Button(self, wx.ID_ANY, u"&Search", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer_category.Add(self.m_button_search, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer_main.Add(bSizer_category, 0, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)

        self.m_listCtrl = wx.ListCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                      wx.LC_NO_SORT_HEADER | wx.LC_REPORT)
        bSizer_main.Add(self.m_listCtrl, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(bSizer_main)
        self.Layout()

        # Connect Events
        self.m_comboBox_category.Bind(wx.EVT_COMBOBOX, self.OnCombobox)
        self.m_textCtrl_search.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_button_search.Bind(wx.EVT_BUTTON, self.OnButtonSearch)
        self.m_listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListItemActivated)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnCombobox(self, event):
        event.Skip()

    def OnKeyDown(self, event):
        event.Skip()

    def OnButtonSearch(self, event):
        event.Skip()

    def OnListItemActivated(self, event):
        event.Skip()


wxID_DEL0 = 1000
wxID_DEL1 = 1001
wxID_DEL2 = 1002
wxID_DEL3 = 1003
wxID_DEL4 = 1004
wxID_DEL5 = 1005
wxID_DEL6 = 1006
wxID_DEL7 = 1007
wxID_DEL8 = 1008
wxID_DEL9 = 1009
wxID_DEL10 = 1010
wxID_DEL11 = 1011
wxID_DEL12 = 1012
wxID_DEL13 = 1013
wxID_DEL14 = 1014
wxID_DEL15 = 1015
wxID_DEL16 = 1016
wxID_DEL17 = 1017
wxID_DEL18 = 1018
wxID_DEL19 = 1019
wxID_BUTTONSEND = 1020
wxID_BUTTONPREVIEW = 1021


###########################################################################
## Class EditProductDialogBase
###########################################################################

class EditProductDialogBase(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Edit Product", pos=wx.DefaultPosition,
                          size=wx.Size(660, 640), style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))

        bSizer_container = wx.BoxSizer(wx.VERTICAL)

        self.m_scrolled_window = wx.ScrolledWindow(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                                   wx.HSCROLL | wx.TAB_TRAVERSAL | wx.VSCROLL)
        self.m_scrolled_window.SetScrollRate(5, 5)
        self.m_scrolled_window.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        bSizer_main = wx.BoxSizer(wx.VERTICAL)

        fgSizer = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer.AddGrowableCol(1)
        fgSizer.SetFlexibleDirection(wx.BOTH)
        fgSizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText_category = wx.StaticText(self.m_scrolled_window, wx.ID_ANY, u"Category", wx.DefaultPosition,
                                                   wx.DefaultSize, wx.ALIGN_RIGHT)
        self.m_staticText_category.Wrap(-1)
        fgSizer.Add(self.m_staticText_category, 0,
                    wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM | wx.LEFT, 5)

        m_comboBox_categoryChoices = []
        self.m_comboBox_category = wx.ComboBox(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                               wx.DefaultSize, m_comboBox_categoryChoices, 0)
        self.m_comboBox_category.SetMinSize(wx.Size(180, -1))

        fgSizer.Add(self.m_comboBox_category, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_staticText_title = wx.StaticText(self.m_scrolled_window, wx.ID_ANY, u"Title", wx.DefaultPosition,
                                                wx.DefaultSize, wx.ALIGN_RIGHT)
        self.m_staticText_title.Wrap(-1)
        fgSizer.Add(self.m_staticText_title, 0,
                    wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM | wx.LEFT, 5)

        self.m_textCtrl_title = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_textCtrl_title.SetMaxLength(0)
        fgSizer.Add(self.m_textCtrl_title, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 5)

        self.m_staticText_price = wx.StaticText(self.m_scrolled_window, wx.ID_ANY, u"Price", wx.DefaultPosition,
                                                wx.DefaultSize, wx.ALIGN_RIGHT)
        self.m_staticText_price.Wrap(-1)
        fgSizer.Add(self.m_staticText_price, 0,
                    wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM | wx.LEFT, 5)

        self.m_textCtrl_price = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_textCtrl_price.SetMaxLength(0)
        self.m_textCtrl_price.SetMinSize(wx.Size(105, -1))

        fgSizer.Add(self.m_textCtrl_price, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer_main.Add(fgSizer, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, 5)

        self.m_staticText_description = wx.StaticText(self.m_scrolled_window, wx.ID_ANY, u"Page 1: Description",
                                                      wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_description.Wrap(-1)
        bSizer_main.Add(self.m_staticText_description, 0, wx.TOP | wx.RIGHT | wx.LEFT, 5)

        self.m_textCtrl_description = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                                  wx.DefaultSize, wx.TE_MULTILINE)
        self.m_textCtrl_description.SetMaxLength(0)
        self.m_textCtrl_description.SetMinSize(wx.Size(-1, 170))

        bSizer_main.Add(self.m_textCtrl_description, 0, wx.ALL | wx.EXPAND, 5)

        self.m_staticText_orderform = wx.StaticText(self.m_scrolled_window, wx.ID_ANY, u"Page 2: Order Form",
                                                    wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_orderform.Wrap(-1)
        bSizer_main.Add(self.m_staticText_orderform, 0, wx.TOP | wx.RIGHT | wx.LEFT, 5)

        self.m_textCtrl_instructions = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString,
                                                   wx.DefaultPosition,
                                                   wx.DefaultSize, wx.TE_MULTILINE)
        self.m_textCtrl_instructions.SetMaxLength(0)
        self.m_textCtrl_instructions.SetMinSize(wx.Size(-1, 120))

        bSizer_main.Add(self.m_textCtrl_instructions, 0, wx.EXPAND | wx.ALL, 5)

        fgSizer_container = wx.FlexGridSizer(0, 3, 0, 0)
        fgSizer_container.AddGrowableCol(1)
        fgSizer_container.SetFlexibleDirection(wx.BOTH)
        fgSizer_container.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText_label = wx.StaticText(self.m_scrolled_window, wx.ID_ANY, u"Label", wx.DefaultPosition,
                                                wx.DefaultSize, 0)
        self.m_staticText_label.Wrap(-1)
        fgSizer_container.Add(self.m_staticText_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.RIGHT | wx.LEFT, 5)

        self.m_staticText_commants = wx.StaticText(self.m_scrolled_window, wx.ID_ANY,
                                                   u"Comma separated list of choices, or leave blank for text field",
                                                   wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_commants.Wrap(-1)
        fgSizer_container.Add(self.m_staticText_commants, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.RIGHT | wx.LEFT, 5)

        fgSizer_container.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self.m_buttonDel = list()
        self.m_textCtrlLabel = list()
        self.m_textCtrlField = list()

        self.m_textCtrlLabel0 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_textCtrlLabel0.SetMaxLength(0)
        self.m_textCtrlLabel0.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel0, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel0)
        self.m_textCtrlField0 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.Size(-1, -1), 0)
        self.m_textCtrlField0.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField0, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField0)
        self.m_buttonDel0 = wx.Button(self.m_scrolled_window, wxID_DEL0, u"Delete", wx.DefaultPosition, wx.Size(60, 20),
                                      0)
        fgSizer_container.Add(self.m_buttonDel0, 0, wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_buttonDel.append(self.m_buttonDel0)
        self.m_textCtrlLabel1 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_textCtrlLabel1.SetMaxLength(0)
        self.m_textCtrlLabel1.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel1)
        self.m_textCtrlField1 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.Size(-1, -1), 0)
        self.m_textCtrlField1.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField1, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField1)
        self.m_buttonDel1 = wx.Button(self.m_scrolled_window, wxID_DEL1, u"Delete", wx.DefaultPosition, wx.Size(60, 20),
                                      0)
        fgSizer_container.Add(self.m_buttonDel1, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel1)
        self.m_textCtrlLabel2 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_textCtrlLabel2.SetMaxLength(0)
        self.m_textCtrlLabel2.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel2)
        self.m_textCtrlField2 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.Size(-1, -1), 0)
        self.m_textCtrlField2.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField2, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField2)
        self.m_buttonDel2 = wx.Button(self.m_scrolled_window, wxID_DEL2, u"Delete", wx.DefaultPosition, wx.Size(60, 20),
                                      0)
        fgSizer_container.Add(self.m_buttonDel2, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel2)
        self.m_textCtrlLabel3 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_textCtrlLabel3.SetMaxLength(0)
        self.m_textCtrlLabel3.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel3, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel3)
        self.m_textCtrlField3 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.Size(-1, -1), 0)
        self.m_textCtrlField3.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField3, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField3)
        self.m_buttonDel3 = wx.Button(self.m_scrolled_window, wxID_DEL3, u"Delete", wx.DefaultPosition, wx.Size(60, 20),
                                      0)
        fgSizer_container.Add(self.m_buttonDel3, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel3)
        self.m_textCtrlLabel4 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_textCtrlLabel4.SetMaxLength(0)
        self.m_textCtrlLabel4.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel4, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel4)
        self.m_textCtrlField4 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.Size(-1, -1), 0)
        self.m_textCtrlField4.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField4, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField4)
        self.m_buttonDel4 = wx.Button(self.m_scrolled_window, wxID_DEL4, u"Delete", wx.DefaultPosition, wx.Size(60, 20),
                                      0)
        fgSizer_container.Add(self.m_buttonDel4, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel4)
        self.m_textCtrlLabel5 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_textCtrlLabel5.SetMaxLength(0)
        self.m_textCtrlLabel5.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel5, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel5)
        self.m_textCtrlField5 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.Size(-1, -1), 0)
        self.m_textCtrlField5.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField5, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField5)
        self.m_buttonDel5 = wx.Button(self.m_scrolled_window, wxID_DEL5, u"Delete", wx.DefaultPosition, wx.Size(60, 20),
                                      0)
        fgSizer_container.Add(self.m_buttonDel5, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel5)
        self.m_textCtrlLabel6 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_textCtrlLabel6.SetMaxLength(0)
        self.m_textCtrlLabel6.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel6, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel6)
        self.m_textCtrlField6 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.Size(-1, -1), 0)
        self.m_textCtrlField6.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField6, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField6)
        self.m_buttonDel6 = wx.Button(self.m_scrolled_window, wxID_DEL6, u"Delete", wx.DefaultPosition, wx.Size(60, 20),
                                      0)
        fgSizer_container.Add(self.m_buttonDel6, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel6)
        self.m_textCtrlLabel7 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_textCtrlLabel7.SetMaxLength(0)
        self.m_textCtrlLabel7.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel7, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel7)
        self.m_textCtrlField7 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.Size(-1, -1), 0)
        self.m_textCtrlField7.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField7, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField7)
        self.m_buttonDel7 = wx.Button(self.m_scrolled_window, wxID_DEL7, u"Delete", wx.DefaultPosition, wx.Size(60, 20),
                                      0)
        fgSizer_container.Add(self.m_buttonDel7, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel7)
        self.m_textCtrlLabel8 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_textCtrlLabel8.SetMaxLength(0)
        self.m_textCtrlLabel8.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel8, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel8)
        self.m_textCtrlField8 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.Size(-1, -1), 0)
        self.m_textCtrlField8.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField8, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField8)
        self.m_buttonDel8 = wx.Button(self.m_scrolled_window, wxID_DEL8, u"Delete", wx.DefaultPosition, wx.Size(60, 20),
                                      0)
        fgSizer_container.Add(self.m_buttonDel8, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel8)
        self.m_textCtrlLabel9 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_textCtrlLabel9.SetMaxLength(0)
        self.m_textCtrlLabel9.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel9, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel9)
        self.m_textCtrlField9 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                            wx.Size(-1, -1), 0)
        self.m_textCtrlField9.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField9, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField9)
        self.m_buttonDel9 = wx.Button(self.m_scrolled_window, wxID_DEL9, u"Delete", wx.DefaultPosition, wx.Size(60, 20),
                                      0)
        fgSizer_container.Add(self.m_buttonDel9, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel9)
        self.m_textCtrlLabel10 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.m_textCtrlLabel10.SetMaxLength(0)
        self.m_textCtrlLabel10.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel10, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel10)
        self.m_textCtrlField10 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.Size(-1, -1), 0)
        self.m_textCtrlField10.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField10, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField10)
        self.m_buttonDel10 = wx.Button(self.m_scrolled_window, wxID_DEL10, u"Delete", wx.DefaultPosition,
                                       wx.Size(60, 20), 0)
        fgSizer_container.Add(self.m_buttonDel10, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel10)
        self.m_textCtrlLabel11 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.m_textCtrlLabel11.SetMaxLength(0)
        self.m_textCtrlLabel11.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel11, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel11)
        self.m_textCtrlField11 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.Size(-1, -1), 0)
        self.m_textCtrlField11.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField11, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField11)
        self.m_buttonDel11 = wx.Button(self.m_scrolled_window, wxID_DEL11, u"Delete", wx.DefaultPosition,
                                       wx.Size(60, 20), 0)
        fgSizer_container.Add(self.m_buttonDel11, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel11)
        self.m_textCtrlLabel12 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.m_textCtrlLabel12.SetMaxLength(0)
        self.m_textCtrlLabel12.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel12, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel12)
        self.m_textCtrlField12 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.Size(-1, -1), 0)
        self.m_textCtrlField12.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField12, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField12)
        self.m_buttonDel12 = wx.Button(self.m_scrolled_window, wxID_DEL12, u"Delete", wx.DefaultPosition,
                                       wx.Size(60, 20), 0)
        fgSizer_container.Add(self.m_buttonDel12, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel12)
        self.m_textCtrlLabel13 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.m_textCtrlLabel13.SetMaxLength(0)
        self.m_textCtrlLabel13.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel13, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel13)
        self.m_textCtrlField13 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.Size(-1, -1), 0)
        self.m_textCtrlField13.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField13, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField13)
        self.m_buttonDel13 = wx.Button(self.m_scrolled_window, wxID_DEL13, u"Delete", wx.DefaultPosition,
                                       wx.Size(60, 20), 0)
        fgSizer_container.Add(self.m_buttonDel13, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel13)
        self.m_textCtrlLabel14 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.m_textCtrlLabel14.SetMaxLength(0)
        self.m_textCtrlLabel14.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel14, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel14)
        self.m_textCtrlField14 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.Size(-1, -1), 0)
        self.m_textCtrlField14.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField14, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField14)
        self.m_buttonDel14 = wx.Button(self.m_scrolled_window, wxID_DEL14, u"Delete", wx.DefaultPosition,
                                       wx.Size(60, 20), 0)
        fgSizer_container.Add(self.m_buttonDel14, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel14)
        self.m_textCtrlLabel15 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.m_textCtrlLabel15.SetMaxLength(0)
        self.m_textCtrlLabel15.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel15, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel15)
        self.m_textCtrlField15 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.Size(-1, -1), 0)
        self.m_textCtrlField15.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField15, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField15)
        self.m_buttonDel15 = wx.Button(self.m_scrolled_window, wxID_DEL15, u"Delete", wx.DefaultPosition,
                                       wx.Size(60, 20), 0)
        fgSizer_container.Add(self.m_buttonDel15, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel15)
        self.m_textCtrlLabel16 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.m_textCtrlLabel16.SetMaxLength(0)
        self.m_textCtrlLabel16.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel16, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel16)
        self.m_textCtrlField16 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.Size(-1, -1), 0)
        self.m_textCtrlField16.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField16, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField16)
        self.m_buttonDel16 = wx.Button(self.m_scrolled_window, wxID_DEL16, u"Delete", wx.DefaultPosition,
                                       wx.Size(60, 20), 0)
        fgSizer_container.Add(self.m_buttonDel16, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel16)
        self.m_textCtrlLabel17 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.m_textCtrlLabel17.SetMaxLength(0)
        self.m_textCtrlLabel17.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel17, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel17)
        self.m_textCtrlField17 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.Size(-1, -1), 0)
        self.m_textCtrlField17.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField17, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField17)
        self.m_buttonDel17 = wx.Button(self.m_scrolled_window, wxID_DEL17, u"Delete", wx.DefaultPosition,
                                       wx.Size(60, 20), 0)
        fgSizer_container.Add(self.m_buttonDel17, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel17)
        self.m_textCtrlLabel18 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.m_textCtrlLabel18.SetMaxLength(0)
        self.m_textCtrlLabel18.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel18, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel18)
        self.m_textCtrlField18 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.Size(-1, -1), 0)
        self.m_textCtrlField18.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField18, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField18)
        self.m_buttonDel18 = wx.Button(self.m_scrolled_window, wxID_DEL18, u"Delete", wx.DefaultPosition,
                                       wx.Size(60, 20), 0)
        fgSizer_container.Add(self.m_buttonDel18, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel18)
        self.m_textCtrlLabel19 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.m_textCtrlLabel19.SetMaxLength(0)
        self.m_textCtrlLabel19.SetMinSize(wx.Size(150, -1))

        fgSizer_container.Add(self.m_textCtrlLabel19, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlLabel.append(self.m_textCtrlLabel19)
        self.m_textCtrlField19 = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                             wx.Size(-1, -1), 0)
        self.m_textCtrlField19.SetMaxLength(0)
        fgSizer_container.Add(self.m_textCtrlField19, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_textCtrlField.append(self.m_textCtrlField19)
        self.m_buttonDel19 = wx.Button(self.m_scrolled_window, wxID_DEL19, u"Delete", wx.DefaultPosition,
                                       wx.Size(60, 20), 0)
        fgSizer_container.Add(self.m_buttonDel19, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 5)
        self.m_buttonDel.append(self.m_buttonDel19)
        bSizer_main.Add(fgSizer_container, 0, wx.EXPAND, 5)

        bSizer_mainbtn = wx.BoxSizer(wx.HORIZONTAL)

        self.m_button_addfield = wx.Button(self.m_scrolled_window, wx.ID_ANY, u"&Add Field", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        bSizer_mainbtn.Add(self.m_button_addfield, 0, wx.ALL, 5)

        bSizer_main.Add(bSizer_mainbtn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.m_scrolled_window.SetSizer(bSizer_main)
        self.m_scrolled_window.Layout()
        bSizer_main.Fit(self.m_scrolled_window)
        bSizer_container.Add(self.m_scrolled_window, 1, wx.EXPAND | wx.ALL, 5)

        bSizer_btns = wx.BoxSizer(wx.HORIZONTAL)

        self.m_button_ok = wx.Button(self, wxID_BUTTONSEND, u"&Send", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_ok.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_ok, 0, wx.ALL, 5)

        self.m_button_preview = wx.Button(self, wxID_BUTTONPREVIEW, u"&Preview", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_preview.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_preview, 0, wx.ALL, 5)

        self.m_button_cancel = wx.Button(self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_cancel.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_cancel, 0, wx.ALL, 5)

        bSizer_container.Add(bSizer_btns, 0, wx.ALIGN_RIGHT, 5)

        self.SetSizer(bSizer_container)
        self.Layout()

        # Connect Events
        self.m_textCtrl_title.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrl_price.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrl_description.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrl_instructions.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlLabel0.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField0.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel0.Bind(wx.EVT_BUTTON, self.OnButtonDel0)
        self.m_textCtrlLabel1.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField1.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel1.Bind(wx.EVT_BUTTON, self.OnButtonDel1)
        self.m_textCtrlLabel2.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField2.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel2.Bind(wx.EVT_BUTTON, self.OnButtonDel2)
        self.m_textCtrlLabel3.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField3.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel3.Bind(wx.EVT_BUTTON, self.OnButtonDel3)
        self.m_textCtrlLabel4.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField4.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel4.Bind(wx.EVT_BUTTON, self.OnButtonDel4)
        self.m_textCtrlLabel5.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField5.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel5.Bind(wx.EVT_BUTTON, self.OnButtonDel5)
        self.m_textCtrlLabel6.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField6.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel6.Bind(wx.EVT_BUTTON, self.OnButtonDel6)
        self.m_textCtrlLabel7.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField7.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel7.Bind(wx.EVT_BUTTON, self.OnButtonDel7)
        self.m_textCtrlLabel8.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField8.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel8.Bind(wx.EVT_BUTTON, self.OnButtonDel8)
        self.m_textCtrlLabel9.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField9.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel9.Bind(wx.EVT_BUTTON, self.OnButtonDel9)
        self.m_textCtrlLabel10.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField10.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel10.Bind(wx.EVT_BUTTON, self.OnButtonDel10)
        self.m_textCtrlLabel11.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField11.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel11.Bind(wx.EVT_BUTTON, self.OnButtonDel11)
        self.m_textCtrlLabel12.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField12.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel12.Bind(wx.EVT_BUTTON, self.OnButtonDel12)
        self.m_textCtrlLabel13.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField13.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel13.Bind(wx.EVT_BUTTON, self.OnButtonDel13)
        self.m_textCtrlLabel14.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField14.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel14.Bind(wx.EVT_BUTTON, self.OnButtonDel14)
        self.m_textCtrlLabel15.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField15.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel15.Bind(wx.EVT_BUTTON, self.OnButtonDel15)
        self.m_textCtrlLabel16.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField16.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel16.Bind(wx.EVT_BUTTON, self.OnButtonDel16)
        self.m_textCtrlLabel17.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField17.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel17.Bind(wx.EVT_BUTTON, self.OnButtonDel17)
        self.m_textCtrlLabel18.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField18.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel18.Bind(wx.EVT_BUTTON, self.OnButtonDel18)
        self.m_textCtrlLabel19.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_textCtrlField19.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_buttonDel19.Bind(wx.EVT_BUTTON, self.OnButtonDel19)
        self.m_button_addfield.Bind(wx.EVT_BUTTON, self.OnButtonAddField)
        self.m_button_ok.Bind(wx.EVT_BUTTON, self.OnButtonSend)
        self.m_button_preview.Bind(wx.EVT_BUTTON, self.OnButtonPreview)
        self.m_button_cancel.Bind(wx.EVT_BUTTON, self.OnButtonCancel)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnKeyDown(self, event):
        event.Skip()

    def OnButtonDel0(self, event):
        event.Skip()

    def OnButtonDel1(self, event):
        event.Skip()

    def OnButtonDel2(self, event):
        event.Skip()

    def OnButtonDel3(self, event):
        event.Skip()

    def OnButtonDel4(self, event):
        event.Skip()

    def OnButtonDel5(self, event):
        event.Skip()

    def OnButtonDel6(self, event):
        event.Skip()

    def OnButtonDel7(self, event):
        event.Skip()

    def OnButtonDel8(self, event):
        event.Skip()

    def OnButtonDel9(self, event):
        event.Skip()

    def OnButtonDel10(self, event):
        event.Skip()

    def OnButtonDel11(self, event):
        event.Skip()

    def OnButtonDel12(self, event):
        event.Skip()

    def OnButtonDel13(self, event):
        event.Skip()

    def OnButtonDel14(self, event):
        event.Skip()

    def OnButtonDel15(self, event):
        event.Skip()

    def OnButtonDel16(self, event):
        event.Skip()

    def OnButtonDel17(self, event):
        event.Skip()

    def OnButtonDel18(self, event):
        event.Skip()

    def OnButtonDel19(self, event):
        event.Skip()

    def OnButtonAddField(self, event):
        event.Skip()

    def OnButtonSend(self, event):
        event.Skip()

    def OnButtonPreview(self, event):
        event.Skip()

    def OnButtonCancel(self, event):
        event.Skip()


wxID_BUTTONSAMPLE = 1050
wxID_CANCEL2 = 1051
wxID_BUTTONBACK = 1052
wxID_BUTTONNEXT = 1053


###########################################################################
## Class ViewProductDialogBase
###########################################################################

class ViewProductDialogBase(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Order Form", pos=wx.DefaultPosition,
                          size=wx.Size(630, 520), style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))

        bSizer_container = wx.BoxSizer(wx.VERTICAL)

        bSizer_main = wx.BoxSizer(wx.HORIZONTAL)

        self.m_html_winreviews = wx.html.HtmlWindow(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                                    wx.html.HW_SCROLLBAR_AUTO)
        self.m_html_winreviews.Hide()

        bSizer_main.Add(self.m_html_winreviews, 1, wx.ALL | wx.EXPAND, 5)

        self.m_scrolled_window = wx.ScrolledWindow(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                                   wx.HSCROLL | wx.TAB_TRAVERSAL | wx.VSCROLL)
        self.m_scrolled_window.SetScrollRate(5, 5)
        self.m_scrolled_window.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        bSizer_inner = wx.BoxSizer(wx.VERTICAL)

        self.m_richText_heading = wx.richtext.RichTextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString,
                                                           wx.DefaultPosition, wx.Size(-1, 200),
                                                           wx.TE_READONLY | wx.NO_BORDER)
        bSizer_inner.Add(self.m_richText_heading, 0, wx.EXPAND, 5)

        self.m_staticText_instructions = wx.StaticText(self.m_scrolled_window, wx.ID_ANY,
                                                       u"Order Form instructions here\nmultiple lines\n1\n2\n3\n4\n5\n6",
                                                       wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_instructions.Wrap(-1)
        bSizer_inner.Add(self.m_staticText_instructions, 1, wx.ALL | wx.EXPAND, 5)

        bSizer_innerbtns = wx.BoxSizer(wx.HORIZONTAL)

        self.m_button_submitform = wx.Button(self.m_scrolled_window, wxID_BUTTONSAMPLE, u"&Submit", wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        bSizer_innerbtns.Add(self.m_button_submitform, 0, wx.ALL, 5)

        self.m_button_cancelform = wx.Button(self.m_scrolled_window, wxID_CANCEL2, u"Cancel", wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        bSizer_innerbtns.Add(self.m_button_cancelform, 0, wx.ALL, 5)

        bSizer_inner.Add(bSizer_innerbtns, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.m_scrolled_window.SetSizer(bSizer_inner)
        self.m_scrolled_window.Layout()
        bSizer_inner.Fit(self.m_scrolled_window)
        bSizer_main.Add(self.m_scrolled_window, 1, wx.EXPAND | wx.ALL, 5)

        bSizer_container.Add(bSizer_main, 1, wx.EXPAND, 5)

        bSizer_btns = wx.BoxSizer(wx.HORIZONTAL)

        self.m_button_back = wx.Button(self, wxID_BUTTONBACK, u"< &Back  ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_back.Enable(False)
        self.m_button_back.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_back, 0, wx.ALL, 5)

        self.m_button_next = wx.Button(self, wxID_BUTTONNEXT, u"  &Next >", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_next.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_next, 0, wx.ALL, 5)

        self.m_button_cancel = wx.Button(self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_cancel.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_cancel, 0, wx.ALL, 5)

        bSizer_container.Add(bSizer_btns, 0, wx.ALIGN_RIGHT, 5)

        self.SetSizer(bSizer_container)
        self.Layout()

        # Connect Events
        self.m_button_submitform.Bind(wx.EVT_BUTTON, self.OnButtonSubmitForm)
        self.m_button_cancelform.Bind(wx.EVT_BUTTON, self.OnButtonCancelForm)
        self.m_button_back.Bind(wx.EVT_BUTTON, self.OnButtonBack)
        self.m_button_next.Bind(wx.EVT_BUTTON, self.OnButtonNext)
        self.m_button_cancel.Bind(wx.EVT_BUTTON, self.OnButtonCancel)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnButtonSubmitForm(self, event):
        event.Skip()

    def OnButtonCancelForm(self, event):
        event.Skip()

    def OnButtonBack(self, event):
        event.Skip()

    def OnButtonNext(self, event):
        event.Skip()

    def OnButtonCancel(self, event):
        event.Skip()


###########################################################################
## Class ViewOrderDialogBase
###########################################################################

class ViewOrderDialogBase(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"View Order", pos=wx.DefaultPosition,
                          size=wx.Size(630, 520), style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))

        bSizer_container = wx.BoxSizer(wx.VERTICAL)

        bSizer_main = wx.BoxSizer(wx.HORIZONTAL)

        self.m_html_win = wx.html.HtmlWindow(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                             wx.html.HW_SCROLLBAR_AUTO)
        bSizer_main.Add(self.m_html_win, 1, wx.ALL | wx.EXPAND, 5)

        bSizer_container.Add(bSizer_main, 1, wx.EXPAND, 5)

        bSizer_btns = wx.BoxSizer(wx.HORIZONTAL)

        self.m_button_ok = wx.Button(self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_ok.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_ok, 0, wx.ALL, 5)

        bSizer_container.Add(bSizer_btns, 0, wx.ALIGN_RIGHT, 5)

        self.SetSizer(bSizer_container)
        self.Layout()

        # Connect Events
        self.m_button_ok.Bind(wx.EVT_BUTTON, self.OnButtonOK)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnButtonOK(self, event):
        event.Skip()


wxID_SUBMIT = 1060


###########################################################################
## Class EditReviewDialogBase
###########################################################################

class EditReviewDialogBase(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Enter Review", pos=wx.DefaultPosition,
                          size=wx.Size(630, 440), style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))

        bSizer_main = wx.BoxSizer(wx.VERTICAL)

        bSizer_main.AddSpacer((0, 3), 0, 0, 5)

        self.m_staticText_seller = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_seller.Wrap(-1)
        bSizer_main.Add(self.m_staticText_seller, 0, wx.ALL | wx.EXPAND, 5)

        bSizer_main.AddSpacer((0, 3), 0, 0, 5)

        self.m_staticText_rating = wx.StaticText(self, wx.ID_ANY, u"Rating", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_rating.Wrap(-1)
        bSizer_main.Add(self.m_staticText_rating, 0, wx.TOP | wx.RIGHT | wx.LEFT, 5)

        m_choice_starsChoices = [u" 1 star", u" 2 stars", u" 3 stars", u" 4 stars", u" 5 stars"]
        self.m_choice_stars = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice_starsChoices, 0)
        self.m_choice_stars.SetSelection(0)
        bSizer_main.Add(self.m_choice_stars, 0, wx.ALL, 5)

        self.m_staticText_review = wx.StaticText(self, wx.ID_ANY, u"Review", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_review.Wrap(-1)
        bSizer_main.Add(self.m_staticText_review, 0, wx.TOP | wx.RIGHT | wx.LEFT, 5)

        self.m_textCtrl_review = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                             wx.TE_MULTILINE)
        self.m_textCtrl_review.SetMaxLength(0)
        bSizer_main.Add(self.m_textCtrl_review, 1, wx.ALL | wx.EXPAND, 5)

        bSizer_btns = wx.BoxSizer(wx.HORIZONTAL)

        self.m_button_submit = wx.Button(self, wxID_SUBMIT, u"&Submit", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_submit.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_submit, 0, wx.ALL, 5)

        self.m_button_cancel = wx.Button(self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button_cancel.SetMinSize(wx.Size(85, 25))

        bSizer_btns.Add(self.m_button_cancel, 0, wx.ALL, 5)

        bSizer_main.Add(bSizer_btns, 0, wx.ALIGN_RIGHT, 5)

        self.SetSizer(bSizer_main)
        self.Layout()

        # Connect Events
        self.m_textCtrl_review.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.m_button_submit.Bind(wx.EVT_BUTTON, self.OnButtonSubmit)
        self.m_button_cancel.Bind(wx.EVT_BUTTON, self.OnButtonCancel)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def OnKeyDown(self, event):
        event.Skip()

    def OnButtonSubmit(self, event):
        event.Skip()

    def OnButtonCancel(self, event):
        event.Skip()


def main():
    pass


if __name__ == '__main__':
    main()

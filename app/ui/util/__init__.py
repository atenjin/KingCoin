#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import cgi
import wx
from copy import deepcopy
from app import config as cfg, context as ctx

ROOT = 'app/rc/'


def date_str(t):
    return wx.DateTime(t).FormatDate()


def date_time_str(t):
    datetime = wx.DateTime(t)
    return datetime.Format("%x %H:%M")


def html_escape(s, multiline=False):
    if multiline:
        s = s.replace("\n", "<br/>")
    return cgi.escape(s)


def load_img_path(rs_name):
    return ROOT + rs_name


def set_selection(listctrl, index):
    size = listctrl.GetItemCount()
    state = wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
    for i in range(size):
        listctrl.SetItemState(i, (state if i == index else 0), state)
    pass


def get_selection(listctrl):
    size = listctrl.GetItemCount()
    for i in range(size):
        if listctrl.GetItemState(i, wx.LIST_STATE_FOCUSED):
            return i
    return -1


def get_item_text(listctrl, index, column):
    # Helper to simplify access to listctrl
    # item = wx.ListItem()
    # item.SetId(index)
    # item.SetColumn(column)
    # item.SetMask(wx.LIST_MASK_TEXT)
    # if not listctrl.GetItem(item):
    #     return ""
    # return item.GetText()
    return str(listctrl.GetItemText(index, column))


def format_tx_status(wtx):
    """

    :param wtx:
    :type wtx: Block.PyWalletTx
    :return:
    """
    depth = wtx.get_depth_in_main_chain()
    if not wtx.is_final():
        return "Open for %d blocks" % depth
    elif depth < cfg.CONFIRMED_BLOCK_NUM:  # TODO check this confirmed block_num
        return "%d/unconfirmed" % depth
    else:
        return "%d blocks" % depth


def insert_line(listctrl, *strs, **datas):
    index = listctrl.InsertStringItem(listctrl.GetItemCount(), strs[0])
    data = datas.get('data', None)
    if data is not None:
        data_hash = hash(data)
        ctx.dictBuff[data_hash] = data
        listctrl.SetItemData(index, data_hash)

    for i, s in enumerate(strs[1:]):  # remove first str
        listctrl.SetStringItem(index, i + 1, s)
    return index


def add_to_my_products(product):
    # copy of product
    product_tmp = deepcopy(product)

    product_hash = product_tmp.get_hash()
    product_insert = ctx.dictMyProducts.get(product_hash, None)
    if product_insert is not None:
        ctx.dictMyProducts[product_hash] = product_tmp
        if ctx.frameMain is not None:
            insert_line(ctx.frameMain.m_listCtrl_productssent,
                        product_tmp.dict_value["category"],
                        product_tmp.dict_value["title"][:100],
                        product_tmp.dict_value["description"][:100],
                        product_tmp.dict_value["price"],
                        "",
                        data=product_tmp)
    pass


def handle_ctrl_A(event):
    # Ctrl-a select all
    text_ctrl = event.GetEventObject()
    if event.GetModifiers() == wx.MOD_CONTROL and event.GetKeyCode() == 'A':
        text_ctrl.SetSelection(-1, -1)
    event.Skip()
    pass


def main():
    pass


if __name__ == '__main__':
    main()

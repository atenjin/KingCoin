#!/usr/bin/env python  
# -*- coding: utf-8 -*-

from enum import IntEnum
import wx
# ui
from .base.mainframe import MainFrameBase
from .base.macro import *
from .dialog import *

# core
from app import context as ctx
from app import thread as mythread
from app.base import serialize
from app.block import txaction
from app.block.tx import tx as Tx
from app.block.tx import script as Script
from app.block import block as Block
from app.block.key import action as keyaction
from app.net import nodeaction
from app.utils import util, timeutil

from app.db import db

shutdownLock = threading.Lock()


def shutdown():
    with shutdownLock:
        if ctx.fShutdown:
            return

        ctx.fShutdown = True
        ctx.transactionsUpdated += 1
        nodeaction.stop_node()
        if ctx.hlistenSocket is not None:
            ctx.hlistenSocket.close()
        print "exiting!"


def wait_threads_exit():
    for work_t, _ in ctx.listWorkThreads:
        work_t.join()
    db.PyDBInit.destroy_env()  # wait until all threads finish!


class UICallType(IntEnum):
    UICALL_ADDORDER = 1
    UICALL_UPDATEORDER = 2


class MainFrame(MainFrameBase):
    nLastTop = 0
    nLastTime = 0

    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent=parent)
        self.Bind(EVT_CROSSTHREADCALL, self.OnCrossThreadCall)

        # init
        self.f_refresh_listctrl = False
        self.f_refresh_listctrl_running = False
        self.f_on_setfouces_addr = False
        self.index_best_last = None
        self.set_unmatured_displayed = set()

        self.m_choicefilter.SetSelection(0)
        self.m_statictext_balance.SetLabel(util.format_money(txaction.get_balance()) + "  ")
        self.m_listCtrl_txs.SetFocus()
        self.SetIcon(wx.Icon(load_img_path(u"bitcoin.ico")))
        self.m_menuOptions.Check(wxID_OPTIONSGENERATEBITCOINS, ctx.fGenerateCoins)

        # init column headers
        date_width = len(timeutil.date_time_str(timeutil.get_time())) * 6 + 8
        self.m_listCtrl_txs.InsertColumn(0, "", wx.LIST_FORMAT_LEFT, 0)
        self.m_listCtrl_txs.InsertColumn(1, "", wx.LIST_FORMAT_LEFT, 0)
        self.m_listCtrl_txs.InsertColumn(2, "Status", wx.LIST_FORMAT_LEFT, 90)
        self.m_listCtrl_txs.InsertColumn(3, "Date", wx.LIST_FORMAT_LEFT, date_width)
        self.m_listCtrl_txs.InsertColumn(4, "Description", wx.LIST_FORMAT_LEFT, 409 - date_width)
        self.m_listCtrl_txs.InsertColumn(5, "Debit", wx.LIST_FORMAT_RIGHT, 79)
        self.m_listCtrl_txs.InsertColumn(6, "Credit", wx.LIST_FORMAT_RIGHT, 79)

        # Init status bar
        widths = [-80, 150, 286]
        self.m_statusBar.SetFieldsCount(3)
        self.m_statusBar.SetStatusWidths(widths)
        with Tx.PyWalletDB("r") as walletdb:
            default_key = walletdb.read_default_key()
        if default_key is not None:
            self.m_textCtrl_addr.SetValue(keyaction.pubkey_to_addr(default_key))
        self.RefreshListCtrl()

        ctx.frameMain = self

        self.miner_thread = None
        pass

    def __del__(self):
        if ctx.frameMain is not None:
            ctx.frameMain = None

    def OnClose(self, event):
        t = threading.Thread(target=shutdown, name='exit')
        t.start()
        # add wait dialog
        w = WaitThreadsDialog(self)
        w.ShowModal()
        t.join()
        print 'closed!'
        self.Destroy()

    def OnListColBeginDrag(self, event):
        # Hidden columns not resizeable
        if event.GetColumn() <= 1 and not ctx.fDebug:
            event.Veto()

    def InsertLine(self, f_new, index, tx_hash, str_sort, *strs):
        data = hash(tx_hash)
        hexformat = serialize.hexser_uint256(tx_hash)
        if f_new:
            # index = self.m_listCtrl_txs.InsertItem(0, str_sort)
            index = self.m_listCtrl_txs.InsertStringItem(0, str_sort)
        else:
            if index == -1:
                # find item
                index = self.m_listCtrl_txs.FindItemData(index, data)
                while index != -1:
                    if get_item_text(self.m_listCtrl_txs, index, 1) == hexformat:
                        break
                    index = self.m_listCtrl_txs.FindItemData(index, data)
                if index == -1:
                    print ("MainFrame::InsertLine : Couldn't find item to be updated")
                    return
            # If sort key changed, must delete and reinsert to make it relocate
            if get_item_text(self.m_listCtrl_txs, index, 0) != str_sort:
                self.m_listCtrl_txs.DeleteItem(index)
                # index = self.m_listCtrl_txs.InsertItem(0, str_sort)
                index = self.m_listCtrl_txs.InsertStringItem(0, str_sort)

        # self.m_listCtrl_txs.SetItem(index, 1, hexformat)
        self.m_listCtrl_txs.SetStringItem(index, 1, hexformat)
        for i in range(2, min(7, len(strs))):
            # self.m_listCtrl_txs.SetItem(index, i, strs[i - 2])
            self.m_listCtrl_txs.SetStringItem(index, i, strs[i - 2])
        self.m_listCtrl_txs.SetItemData(index, data)

    def InsertTransaction(self, wtx, f_new, index=-1):
        """

        :param wtx:
        :type wtx: Block.PyWalletTx
        :param f_new:
        :param index:
        :return:
        """
        wtx.time_displayed = wtx.get_tx_time()
        time = wtx.time_displayed
        credit = wtx.get_credit()
        debit = wtx.get_debit()
        net = credit - debit  # diff
        tx_hash = wtx.get_hash()
        str_status = format_tx_status(wtx)
        dict_value = wtx.dict_value

        is_coinbase = wtx.is_coinbase()

        # Find the block the tx is in
        block_index = ctx.dictBlockIndex.get(wtx.hash_block, None)
        # Sort order, unrecorded transactions sort to the top
        str_sort = "%010d-%01d-%010u" % (block_index.height if block_index is not None else 0xFFFFFFFF,
                                         1 if is_coinbase else 0,
                                         wtx.time_received)
        # Insert line
        if net > 0 or is_coinbase:
            # Credit
            str_description = ""
            if is_coinbase:  # coinbase 下会跳过 credit 的计算
                # Coinbase
                str_description = "Generated"
                if credit == 0:
                    if wtx.is_in_main_chain():
                        unmatured = 0
                        for out in wtx.l_out:
                            unmatured += out.get_credit()
                        str_description += u" (%s matures in %d blocks)" % \
                                           (util.format_money(unmatured),
                                            wtx.get_blocks_to_maturity())  # TODO check maturity
                    else:
                        str_description += " (not accepted)"
            elif dict_value.get("from", None) or dict_value.get("message", None):
                # Online transaction
                from_data = dict_value.get("from", None)
                msg_data = dict_value.get("message", None)
                if from_data:
                    str_description = "".join((str_description, "From: ", from_data))
                if msg_data:
                    if str_description:
                        str_description += " - "
                    str_description += msg_data
            else:
                # Offline transaction
                for out in wtx.l_out:
                    if out.is_mine():
                        pubkey = Script.extract_pubkey(out.script_pubkey, True)
                        if pubkey is not None:
                            addr = keyaction.pubkey_to_addr(pubkey)
                            if addr in ctx.dictAddressBook:
                                str_description += "Received with: "
                                if ctx.dictAddressBook[addr]:
                                    str_description += ctx.dictAddressBook[addr] + " "
                                str_description += addr
                        break  # when meet is_mine, jump out the loop
                        pass  # end if for is_mine()
                    pass  # end for loop

            str_description2 = filter(lambda x: True if x >= ' ' else False, str_description)
            self.InsertLine(f_new, index, tx_hash, str_sort,
                            unicode(str_status),
                            unicode(timeutil.date_time_str(time)) if time else u"",
                            str_description2,
                            u"",
                            unicode(util.format_money(net, True)))
        else:  # net < 0  get more than input
            f_all_from_me = True
            for txin in wtx.l_in:
                f_all_from_me = f_all_from_me and txin.is_mine()

            f_all_to_me = True
            for txout in wtx.l_out:
                f_all_to_me = f_all_to_me and txout.is_mine()

            if f_all_from_me and f_all_to_me:  # transfer only in self wallet
                # Payment to self
                value = wtx.l_out[0].value
                self.InsertLine(f_new, index, tx_hash, str_sort,
                                unicode(str_status),
                                unicode(timeutil.date_time_str(time)) if time else u"",
                                u"Payment to yourself",
                                unicode(util.format_money(net - value, True)),
                                unicode(util.format_money(value, True)))
            elif f_all_from_me:
                # Debit
                tx_fee = debit - wtx.get_value_out()  # all out
                for outindex, txout in enumerate(wtx.l_out):
                    if txout.is_mine():
                        continue
                    # filter txout not belong to me
                    addr = ''
                    r = dict_value.get("to", '')
                    if r:
                        # Online transaction
                        addr = r
                    else:
                        # Offline transaction
                        hash160_str = Script.extract_hash160(txout.script_pubkey, out_type='str')
                        if hash160_str is not None:
                            addr = keyaction.hash160_to_addr(hash160_str)
                    str_description = "To: "
                    addrname = ctx.dictAddressBook.get(addr, '')
                    if addrname:
                        str_description += addrname
                    else:
                        str_description += addr

                    msg = dict_value.get("message", '')
                    if msg:
                        if str_description:
                            str_description += " - "
                        str_description += msg
                    str_description2 = filter(lambda x: True if x >= ' ' else False, str_description)

                    value = txout.value
                    if outindex == 0 and tx_fee > 0:  # only calc once
                        value += tx_fee

                    self.InsertLine(f_new, index, tx_hash, "%s-%d" % (str_sort, outindex),
                                    str_status,
                                    timeutil.date_time_str(time) if time else "",
                                    str_description2,
                                    util.format_money(-value, True),  # 注意这里添加上了负号,代表支出
                                    "")
            else:  # f_all_to_me
                # Mixed debit transaction, can't break down payees
                # f_all_mine = True
                # for txout in wtx.l_out:
                #     f_all_mine = f_all_mine and txout.is_mine()
                # for txin in wtx.l_in:
                #     f_all_mine = f_all_mine and txin.is_mine()
                self.InsertLine(f_new, index, tx_hash, str_sort,
                                str_status,
                                timeutil.date_time_str(time) if time else "",
                                "",
                                util.format_money(net, True),
                                "")
                pass  # end else
            pass  # end else
        pass  # end func

    def RefreshStatus(self):
        top = self.m_listCtrl_txs.GetTopItem()
        if top == MainFrame.nLastTop and id(self.index_best_last) == id(ctx.indexBest):
            return
        if ctx.dictWalletLock._RLock__count == 0:
            with ctx.dictWalletLock:
                start = top
                end = min(start + 100, self.m_listCtrl_txs.GetItemCount())
                if id(self.index_best_last) == id(ctx.indexBest):
                    # If no updates, only need to do the part that moved onto the screen
                    if MainFrame.nLastTop <= start < (MainFrame.nLastTop + 100):
                        start = MainFrame.nLastTop + 100
                    if MainFrame.nLastTop <= end < (MainFrame.nLastTop + 100):
                        end = MainFrame.nLastTop  # end will less than start
                MainFrame.nLastTop = top
                self.index_best_last = ctx.indexBest
                end = min(end, self.m_listCtrl_txs.GetItemCount())
                for i in range(start, end):
                    tx_hash = get_item_text(self.m_listCtrl_txs, i, 1)
                    wtx = ctx.dictWallet.get(tx_hash, None)
                    if wtx is None:
                        print ("MainFrame::RefreshStatus() : tx not found in dictWallet")
                        continue
                    if wtx.is_coinbase() or wtx.get_tx_time() != wtx.time_displayed:
                        self.InsertTransaction(wtx, False, i)
                    else:
                        self.m_listCtrl_txs.SetItem(i, 2, format_tx_status(wtx))
                pass  # end block
            pass  # end try block

    def RefreshListCtrl(self):
        self.f_refresh_listctrl = True
        wx.WakeUpIdle()

    def OnIdle(self, event):
        if self.f_refresh_listctrl:
            # Collect list of wallet transactions and sort newest first
            f_entered = False
            list_sorted = list()
            if ctx.dictWalletLock._RLock__count == 0:
                with ctx.dictWalletLock:
                    print ("RefreshListCtrl starting")
                    f_entered = True
                    self.f_refresh_listctrl = False
                    del ctx.listWalletUpdated[:]

                    # Do the newest transactions first
                    for tx_hash, wtx in ctx.dictWallet.iteritems():
                        time = 0xFFFFFFFF - wtx.get_tx_time()
                        list_sorted.append((time, tx_hash))
                    self.m_listCtrl_txs.DeleteAllItems()
                    pass  # end block
                pass  # end try block

            if not f_entered:
                return

            list_sorted.sort(key=lambda x: x[0])

            # Fill list control
            for i, item in enumerate(list_sorted):
                if ctx.fShutdown:
                    return
                f_entered = False
                if ctx.dictWalletLock._RLock__count == 0:
                    with ctx.dictWalletLock:
                        f_entered = True
                        tx_hash = item[1]
                        wtx = ctx.dictWallet.get(tx_hash, None)
                        if wtx is not None:
                            self.InsertTransaction(wtx, True)
                        pass  # end block
                    pass  # end try block
                if not f_entered or i == 100 or i % 500 == 0:
                    wx.Yield()
            print ("RefreshListCtrl done")
        else:
            # Check for time updates
            current_time = timeutil.get_time()
            if current_time > MainFrame.nLastTime + 30:
                if ctx.dictWalletLock._RLock__count == 0:
                    with ctx.dictWalletLock:
                        MainFrame.nLastTime = current_time
                        for wtx in ctx.dictWallet.values():
                            if wtx.time_displayed and wtx.time_displayed != wtx.get_tx_time:
                                self.InsertTransaction(wtx, False)

            pass
        pass  # end func

    def OnPaintListCtrl(self, event):

        # Update listctrl contents
        if ctx.listWalletUpdated:
            if ctx.dictWalletLock._RLock__count == 0:
                with ctx.dictWalletLock:
                    for tx_hash, f_new in ctx.listWalletUpdated:
                        wtx = ctx.dictWallet.get(tx_hash, None)
                        if wtx is not None:
                            print ("listWalletUpdated: %s %s" %
                                   (serialize.hexser_uint256(tx_hash)[:6], "new" if f_new else ""))
                            self.InsertTransaction(wtx, f_new)
                    self.m_listCtrl_txs.ScrollList(0, 0xFFFF)
                    del ctx.listWalletUpdated[:]
                    pass  # end block
                pass  # end try block
        # Update status column of visible items only
        self.RefreshStatus()

        # Update status bar
        str_gen = ''
        if ctx.fGenerateCoins:
            str_gen = "    Generating"
        if ctx.fGenerateCoins and len(ctx.listNodes) == 0:
            str_gen = "(not connected)"

        self.m_statusBar.SetStatusText(unicode(str_gen), 1)

        str_status = "     %d connections     %d blocks     %d transactions" % \
                     (len(ctx.listNodes), ctx.bestHeight + 1, self.m_listCtrl_txs.GetItemCount())
        self.m_statusBar.SetStatusText(unicode(str_status), 2)

        # Balance total
        if ctx.dictWalletLock._RLock__count == 0:
            with ctx.dictWalletLock:
                self.m_statictext_balance.SetLabel(util.format_money(txaction.get_balance()) + '  ')
                # print 'set label'
        self.m_listCtrl_txs.OnPaint(event)
        pass  # end func

    def OnCrossThreadCall(self, event):
        """

        :param event:
        :type event: wx.CommandEvent
        :return:
        """
        data = event.GetClientData()
        if event.GetInt() == UICallType.UICALL_ADDORDER:
            pass
        elif event.GetInt() == UICallType.UICALL_UPDATEORDER:
            pass
        pass

    def OnMenuFileExit(self, event):
        self.Close(True)

    def OnMenuOptionsGenerate(self, event):
        ctx.fGenerateCoins = event.IsChecked()
        ctx.transactionsUpdated += 1
        with Tx.PyWalletDB() as walletdb:
            walletdb.write_setting(Tx.PyWalletDB.DBKEY_SETTING_GEN_COIN, ctx.fGenerateCoins)

        self.MinerThread(ctx.fGenerateCoins)

        self.Refresh()
        self.AddPendingEvent(wx.PaintEvent())

    def MinerThread(self, generate):
        if generate:
            if self.miner_thread is None:
                miner_t = mythread.CoinMinerThread(None)
                self.miner_thread = miner_t
                miner_t.start()
            print ("start miner thread!")
        else:
            if self.miner_thread is not None:
                self.miner_thread.try_exit()
                self.miner_thread = None

    def OnMenuOptionsOptions(self, event):
        OptionsDialog(self).ShowModal()

    def OnMenuHelpAbout(self, event):
        AboutDialog(self).ShowModal()

    def OnButtonSend(self, event):
        # Toolbar: Send
        SendDialog(self).ShowModal()

    def OnButtonAddressBook(self, event):
        # Toolbar: Address Book
        ret = AddressBookDialog(self, "", False).ShowModal()
        if ret == 2:
            # Send
            SendDialog(self).ShowModal()

    def OnSetFocusAddress(self, event):
        # Automatically select-all when entering window
        self.m_textCtrl_addr.SetSelection(-1, -1)
        self.f_on_setfouces_addr = True
        event.Skip()

    def OnMouseEventsAddress(self, event):
        if self.f_on_setfouces_addr:
            self.m_textCtrl_addr.SetSelection(-1, -1)
        self.f_on_setfouces_addr = False
        event.Skip()

    def OnButtonCopy(self, event):
        # Copy address box to clipboard
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.PyTextDataObject(self.m_textCtrl_addr.GetValue()))
            wx.TheClipboard.Close()

    def OnButtonChange(self, event):
        dialog = YourAddressDialog(self, self.m_textCtrl_addr.GetValue())
        ret = dialog.ShowModal()
        if not ret:
            return
        addr = dialog.GetAddress()
        if addr != self.m_statictext_addr.GetValue():
            hash160 = keyaction.addr_to_hash160(addr)
            if hash160 is None:
                return
            if hash160 not in ctx.dictPubKeys:
                return

            with Tx.PyWalletDB() as walletdb:
                walletdb.write_default_key(ctx.dictPubKeys[hash160])
            self.m_textCtrl_addr.SetValue(addr)

    def OnListItemActivatedAllTransactions(self, event):
        tx_hash = get_item_text(self.m_listCtrl_txs, event.GetIndex(), 1)
        with ctx.dictWalletLock:
            wtx = ctx.dictWallet.get(tx_hash, None)
            if wtx is None:
                print ("MainFrame::OnListItemActivatedAllTransactions() : tx not found in mapWallet")
                return

        TxDetailsDialog(self, wtx).ShowModal()

    def OnListItemActivatedProductsSent(self, event):
        product = event.GetItem().GetData()
        dialog = EditProductDialog(self)
        dialog.SetProduct(product)
        dialog.Show()

    def OnListItemActivatedOrdersSent(self, event):  # sent
        order = event.GetItem().GetData()
        ViewOrderDialog(self, order, received=False).Show()

    def OnListItemActivatedOrdersReceived(self, event):  # received
        order = event.GetItem().GetData()
        ViewOrderDialog(self, order, received=True).Show()
        pass

    pass


class WaitThreadsDialog(wx.Dialog):
    nLastTime = 0

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Wait until all threads exit!", pos=wx.DefaultPosition,
                           size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE)

        self.parent = parent

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer_container = wx.BoxSizer(wx.VERTICAL)

        bSizer_main = wx.BoxSizer(wx.VERTICAL)

        self.text_list = list()

        self.m_staticText_thread0 = wx.StaticText(self, wx.ID_ANY, u"None", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_thread0.Wrap(-1)
        bSizer_main.Add(self.m_staticText_thread0, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.text_list.append(self.m_staticText_thread0)

        self.m_staticText_thread1 = wx.StaticText(self, wx.ID_ANY, u"None", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_thread1.Wrap(-1)
        bSizer_main.Add(self.m_staticText_thread1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.text_list.append(self.m_staticText_thread1)

        self.m_staticText_thread2 = wx.StaticText(self, wx.ID_ANY, u"None", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_thread2.Wrap(-1)
        bSizer_main.Add(self.m_staticText_thread2, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.text_list.append(self.m_staticText_thread2)

        self.m_staticText_thread3 = wx.StaticText(self, wx.ID_ANY, u"None", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_thread3.Wrap(-1)
        bSizer_main.Add(self.m_staticText_thread3, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.text_list.append(self.m_staticText_thread3)

        self.m_staticText_thread4 = wx.StaticText(self, wx.ID_ANY, u"None", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText_thread4.Wrap(-1)
        bSizer_main.Add(self.m_staticText_thread4, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.text_list.append(self.m_staticText_thread4)

        bSizer_container.Add(bSizer_main, 0, wx.ALL | wx.EXPAND, 30)

        self.SetSizer(bSizer_container)
        self.Layout()

        self.Centre(wx.BOTH)

        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.t = threading.Thread(target=wait_threads_exit, name='wait_threads')
        self.t.start()
        # add wait dialog
        # t.join()

    def __del__(self):
        pass

    def OnIdle(self, event):
        current_time = timeutil.get_time()
        if current_time - WaitThreadsDialog.nLastTime > 1:  # lookup every 1 second
            WaitThreadsDialog.nLastTime = current_time
        else:
            return

        for i, data in enumerate(ctx.listWorkThreads):
            t, name = data
            s = "run" if t.isAlive() else "exit"
            ret = "%s: %s" % (name, s)
            self.text_list[i].SetLabelText(ret)
        if self.parent.miner_thread is not None:
            s = "run" if self.parent.miner_thread.isAlive() else "exit"
            ret = "%s: %s" % ("miner coin", s)
            self.m_staticText_thread4.SetLabelText(ret)
        else:
            self.m_staticText_thread4.SetLabelText("miner coin: not working")
        pass

    def OnClose(self, event):
        self.EndModal(0)
        pass


def main():
    pass


if __name__ == '__main__':
    main()

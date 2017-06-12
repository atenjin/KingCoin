#!/usr/bin/env python  
# -*- coding: utf-8 -*-

from collections import defaultdict

from .util import *
from .base.abort import AboutDialogBase
from .base.options import OptionsDialogBase
from .base.send import SendDialogBase, SendingDialogBase
from .base.addr import AddressBookDialogBase, YourAddressDialogBase
from .base.details import TxDetailsDialogBase
from .base.market import *
from .base.others import GetTextFromUserDialogBase
from .event import *

from app import context as ctx
from app.base import serialize, ui
from app.block import block as Block, txaction
from app.block.key import action as keyaction
from app.block.tx import script as Script, tx as Tx
from app.net import net as Net, base as netbase, action as netaction
from app.market import market
from app.utils import util, timeutil


class AboutDialog(AboutDialogBase):
    def OnButtonOK(self, event):
        self.EndModal(True)

    pass


class TxDetailsDialog(TxDetailsDialogBase):
    def __init__(self, parent, wtx):
        """

        :param parent:
        :param wtx:
        :type wtx: Block.PyWalletTx
        """
        super(TxDetailsDialog, self).__init__(parent)
        time = wtx.get_tx_time()
        credit = wtx.get_credit()
        debit = wtx.get_debit()
        net = credit - debit

        html = self.__create_html(wtx, timeutil, credit, debit, net)
        self.m_htmlwin.SetPage(html)
        self.m_button_ok.SetFocus()

    @staticmethod
    def __create_html(wtx, time, credit, debit, net):
        """

        :param wtx:
        :type wtx: Block.PyWalletTx
        :param time:
        :param credit:
        :param debit:
        :param net:
        :return:
        """

        buff = [
            "<b>Status:</b> ", format_tx_status(wtx), "<br>",
            "<b>Date:</b> ", (timeutil.date_time_str(time) if time  else ""), "<br>"]
        #
        # From
        #
        if wtx.is_coinbase():
            buff.append("<b>Source:</b> Generated<br>")
        elif wtx.dict_value["from"]:
            # Online transaction
            buff.append("<b>From:</b> " + html_escape(wtx.dict_value["from"]) + "<br>")
        else:
            # Offline transaction
            for txout in wtx.l_out:
                if txout.is_mine():
                    pubkey = Script.extract_pubkey(txout.script_pubkey, True)
                    if pubkey is not None:
                        addr = keyaction.pubkey_to_addr(pubkey)
                        addrname = ctx.dictAddressBook.get(addr, None)
                        if addrname:
                            buff.append(addrname + " ")
                        buff.append(html_escape(addr))
                        buff.append("<br>")
                    break  # only once ismine()

        #
        # To
        #
        if wtx.dict_value["to"]:
            # Online transaction
            strAddress = wtx.dict_value["to"]
            buff.append("<b>To:</b> ")

            addrname = ctx.dictAddressBook.get(strAddress, '')
            if addrname:
                buff.append(addrname + " ")
            buff.append(html_escape(strAddress) + "<br>")

        #
        # Amount
        #
        if wtx.is_coinbase() and credit == 0:
            #
            # Coinbase
            #
            unmatured = 0
            for txout in wtx.l_out:
                unmatured += txout.get_credit()
            if wtx.is_in_main_chain():
                buff.append("<b>Credit:</b> (%s matures in %d blocks)<br>" %
                            (util.format_money(unmatured), wtx.get_blocks_to_maturity()))
            else:
                buff.append("<b>Credit:</b> (not accepted)<br>")
        elif net > 0:
            #
            # Credit
            #
            buff.append("<b>Credit:</b> " + util.format_money(net) + "<br>")
        else:
            all_from_me = True
            for txin in wtx.l_in:
                all_from_me = all_from_me and txin.is_mine()

            all_to_me = True
            for txout in wtx.l_out:
                all_to_me = all_to_me and txout.is_mine()

            if all_from_me:
                #
                # Debit
                #

                for txout in wtx.l_out:
                    if txout.is_mine():
                        continue
                    addr = wtx.dict_value.get("to", '')
                    if addr:
                        pass  # Online tx
                    else:
                        # offline tx
                        hash160 = Script.extract_hash160(txout.script_pubkey)
                        if hash160 is not None:
                            addr = keyaction.hash160_to_addr(hash160)

                        buff.append("<b>Debit:</b> " + util.format_money(-txout.nValue) + " &nbsp&nbsp ")
                        buff.append("(to ")
                        addrname = ctx.dictAddressBook.get(addr, '')
                        if addrname:
                            buff.append(addrname + " ")
                        buff.append(addr)
                        buff.append(")<br>")

                    if all_to_me:
                        # Payment to self
                        value = wtx.l_out[0].value
                        buff.append("<b>Debit:</b> " + util.format_money(-value) + "<br>")
                        buff.append("<b>Credit:</b> " + util.format_money(value) + "<br>")

                        tx_fee = debit - wtx.get_value_out()
                        if tx_fee > 0:
                            buff.append("<b>Transaction fee:</b> " + util.format_money(-tx_fee) + "<br>")
            else:  # all from me
                #
                # Mixed debit transaction
                #
                for txin in wtx.l_in:
                    if txin.is_mine():
                        buff.append("<b>Debit:</b> " + util.format_money(-txin.get_debit()) + "<br>")
                for txout in wtx.l_out:
                    if txout.is_mine():
                        buff.append("<b>Credit:</b> " + util.format_money(txout.get_credit()) + "<br>")
            pass  # end else
        buff.append("<b>Net amount:</b> " + util.format_money(net, True) + "<br>")

        #
        # Message
        #
        msg = wtx.dict_value.get("message", '')
        if msg:
            buff.append("<br><b>Message:</b><br>" + html_escape(msg, True) + "<br>")

        #
        # Debug view
        #
        if ctx.fDebug:
            buff.append("<hr><br>debug print<br><br>")

            for txin in wtx.l_in:
                if txin.is_mine():
                    buff.append("<b>Debit:</b> " + util.format_money(-txin.get_debit()) + "<br>")
            for txout in wtx.l_out:
                if txout.is_mine():
                    buff.append("<b>Credit:</b> " + util.format_money(txout.get_credit()) + "<br>")

            buff.append("<b>Inputs:</b><br>")
            with ctx.dictWalletLock:
                for txin in wtx.l_in:
                    prev_out = txin.prev_out
                    prev_tx = ctx.dictWallet.get(prev_out.hash_tx)
                    if prev_tx is not None:  # prev is tx
                        if prev_out.index < len(prev_tx.l_out):
                            buff.append(html_escape(str(prev_tx), True))
                            buff.append(" &nbsp&nbsp " + format_tx_status(prev_tx) + ", ")
                            buff.append(
                                "IsMine=" + ("true" if prev_tx.l_out[prev_out.index].is_mine() else "false") + "<br>")
                pass  # end block
            buff.append("<br><hr><br><b>Transaction:</b><br>")
            buff.append(html_escape(str(wtx), True))
            pass  # end if debug
        return ''.join(buff)

    pass


class OptionsDialog(OptionsDialogBase):
    def __init__(self, parent):
        super(OptionsDialog, self).__init__(parent)
        self.m_textCtrl_tx_fee.SetValue(util.format_money(ctx.transactionFee))
        # self.m_button_ok.SetFocus()
        self.m_textCtrl_tx_fee.SetFocus()

    def OnKillFocusTransactionFee(self, event):
        prev = ctx.transactionFee
        now = util.parse_money(self.m_textCtrl_tx_fee.GetValue())
        if now is not None:
            self.m_textCtrl_tx_fee.SetValue(util.format_money(now))
        else:
            self.m_textCtrl_tx_fee.SetValue(util.format_money(prev))

    def OnButtonOK(self, event):
        # TransactionFee
        prev = ctx.transactionFee
        now = util.parse_money(self.m_textCtrl_tx_fee.GetValue())
        if now is not None and now != prev:
            ctx.transactionFee = now
            with Tx.PyWalletDB() as walletdb:
                walletdb.write_setting(Tx.PyWalletDB.DBKEY_SETTING_TX_FEE, ctx.transactionFee)
        self.EndModal(True)

    def OnButtonCancel(self, event):
        self.EndModal(False)

    pass


class SendDialog(SendDialogBase):
    def __init__(self, parent, addr=""):
        super(SendDialog, self).__init__(parent)
        # init
        self.m_textCtrl_addr.SetValue(addr)
        self.m_choice_transfer_type.SetSelection(0)
        self.m_bitmapCheckMark.Show(False)
        ## TODO should add a display of your balance for convenience

        # set icon
        bmp_send = wx.Bitmap(load_img_path(u"send16.bmp"), wx.BITMAP_TYPE_BMP)
        bmp_send.SetMask(wx.Mask(wx.Bitmap(load_img_path(u"send16masknoshadow.bmp"), wx.BITMAP_TYPE_BMP)))
        icon_send = wx.Icon(load_img_path(u"send16.bmp"))
        icon_send.CopyFromBitmap(bmp_send)
        self.SetIcon(icon_send)

        self.OnTextAddress(wx.CommandEvent())

        # Fixup the tab order
        self.m_button_paste.MoveAfterInTabOrder(self.m_button_cancel)
        self.m_button_addr.MoveAfterInTabOrder(self.m_button_paste)
        self.Layout()

    def OnTextAddress(self, event):
        # Check mark
        f_coin_addr = keyaction.is_valid_address(self.m_textCtrl_addr.GetValue())
        self.m_bitmapCheckMark.Show(f_coin_addr)

        # Grey out message if bitcoin address
        f_enable = not f_coin_addr
        self.m_staticText_from.Enable(f_enable)
        self.m_textCtrl_from.Enable(f_enable)
        self.m_staticText_msg.Enable(f_enable)
        self.m_textCtrl_msg.Enable(f_enable)
        self.m_textCtrl_msg.SetBackgroundColour(wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_WINDOW if f_enable else wx.SYS_COLOUR_BTNFACE))

    def OnKillFocusAmount(self, event):
        # Reformat the amount
        s = self.m_textCtrl_amount.GetValue().strip()
        if not s:
            return
        tmp = util.parse_money(s)
        if tmp is not None:
            self.m_textCtrl_amount.SetValue(util.format_money(tmp))

    def OnButtonAddressBook(self, event):
        # Open address book
        dialog = AddressBookDialog(self, self.m_textCtrl_addr.GetValue(), True)
        if dialog.ShowModal():
            self.m_textCtrl_addr.SetValue(dialog.GetAddress())

    def OnButtonPaste(self, event):
        # Copy clipboard to address box
        if wx.TheClipboard.Open():
            if wx.TheClipboard.IsSupported(wx.DF_TEXT):
                data = wx.TextDataObject()
                wx.TheClipboard.GetData(data)
                self.m_textCtrl_addr.SetValue(data.GetText())
            wx.TheClipboard.Close()

    def OnButtonSend(self, event):
        wtx = Block.PyWalletTx()
        addr = self.m_textCtrl_addr.GetValue()
        # Parse amount
        value = util.parse_money(self.m_textCtrl_amount.GetValue())
        if value is None or value <= 0:
            wx.MessageBox("Error in amount ")
            return

        balance = txaction.get_balance()
        if value > balance:
            wx.MessageBox("Amount exceeds your balance ")
            return
        if value + ctx.transactionFee > balance:
            wx.MessageBox("Total exceeds your balance when the %s transaction fee is included " %
                          util.format_money(ctx.transactionFee))
            return

        # Parse address
        hash160 = keyaction.addr_to_hash160(addr, onlyhash=True, out_type='num')
        if hash160 is not None:
            # Send to bitcoin address
            script_pubkey = Script.PyScript()
            script_pubkey.append(Script.OpCodeType.OP_DUP).append(Script.OpCodeType.OP_HASH160) \
                .append(hash160, var_type="uint160") \
                .append(Script.OpCodeType.OP_EQUALVERIFY) \
                .append(Script.OpCodeType.OP_CHECKSIG)

            if not txaction.send_money(script_pubkey, value, wtx, ignoreui=False):
                return

            wx.MessageBox("Payment sent ", "Sending...")
        else:
            # Parse IP address
            tmp = addr.split(':')
            if len(tmp) != 2 or netbase.ip2uint(tmp[0]) == 0 or not tmp[1].isdigit():
                wx.MessageBox("Invalid address for: %s" % addr)
                return
            Net.PyAddress(tmp[0], int(tmp[1]))
            # Message
            wtx.dict_value["to"] = addr
            wtx.dict_value["from"] = self.m_textCtrl_from.GetValue()
            wtx.dict_value["message"] = self.m_textCtrl_msg.GetValue()

            # Send to IP address
            dialog = SendingDialog(self, addr, value, wtx)
            if not dialog.ShowModal():
                return
        if addr not in ctx.dictAddressBook:
            keyaction.set_address_book_name(addr, "")

        self.EndModal(True)

    def OnButtonCancel(self, event):
        self.EndModal(False)

    pass


class SendingDialog(SendingDialogBase):
    def __init__(self, parent, addr, price, wtx):
        super(SendingDialog, self).__init__(parent)
        self.addr = addr
        self.price = price
        self.wtx = wtx
        self.start = wx.DateTime.Now()
        self.status = ""
        self.can_cancel = True
        self.abort = False
        self.success = False
        self.UI_done = False
        self.work_done = False

        self.SetTitle("Sending %s to %s..." % (util.format_money(self.price), wtx.dict_value.get("to", '')))
        self.m_textCtrl_status.SetValue("")

        threading.Thread(target=sending_dialog_start_transfer,
                         name="SendingDialog:sending_dialog_start_transfer(obj)",
                         args=(self,)).start()

    def Close(*args, **kwargs):
        # Last one out turn out the lights.
        # fWorkDone signals that work side is done and UI thread should call destroy.
        # fUIDone signals that UI window has closed and work thread should call destroy.
        # This allows the window to disappear and end modality when cancelled
        # without making the user wait for ConnectNode to return.  The dialog object
        # hangs around in the background until the work thread exits.
        self = args[0]
        if self.IsModal():
            self.EndModal(self.success)
        else:
            self.Show(False)

        if self.work_done:
            self.Destroy()
        else:
            self.UI_done = True

    def OnClose(self, event):
        if not event.CanVeto() or self.work_done or self.abort or not self.can_cancel:
            self.Close()
        else:
            event.Veto()
            self.OnButtonCancel(wx.CommandEvent())

    def OnButtonOK(self, event):
        if self.work_done:
            self.Close()

    def OnButtonCancel(self, event):
        if self.can_cancel:
            self.abort = True

    def OnPaint(self, event):
        if len(self.status) > 130:
            self.m_textCtrl_status.SetValue("\n" + self.status)
        else:
            self.m_textCtrl_status.SetValue("\n\n" + self.status)
        self.m_staticText_sending.SetFocus()
        if not self.can_cancel:
            self.m_button_cancel.Enable(False)
        if self.work_done:
            self.m_button_ok.Enable(True)
            self.m_button_ok.SetFocus()
            self.m_button_cancel.Enable(False)
        if self.abort and self.can_cancel and self.IsShown():
            self.status = "CANCELLED"
            self.m_button_ok.Enable(True)
            self.m_button_ok.SetFocus()
            self.m_button_cancel.Enable(False)
            self.m_button_cancel.SetLabel("Cancelled")
            self.Close()
            wx.MessageBox("Transfer cancelled ", "Sending...", wx.OK, self)

        event.Skip()

    def Repaint(self):
        self.Refresh()
        self.AddPendingEvent(wx.PaintEvent())

    def Error(self, s):
        self.can_cancel = False
        self.work_done = True
        self.Status("Error: " + s)
        return False

    def Status(self, s=None):
        if s is None:
            if self.UI_done:
                self.Destroy()
                return False
            if self.abort and self.can_cancel:
                self.status = "CANCELLED"
                self.Repaint()
                self.work_done = True
                return False
            return True
        else:
            if not self.Status():
                return False
            self.status = s
            self.Repaint()
            return True

    def StartTransfer(self):
        # Make sure we have enough money
        if self.price + ctx.transactionFee > txaction.get_balance():
            self.Error("You don't have enough money")
            return
        # We may have connected already for product details
        if not self.Status("Connecting..."):
            return

        node = netaction.connect_node(self.addr, 5 * 60)
        if node is None:
            self.Error("Unable to connect")
            return

        # Send order to seller, with response going to OnReply2 via event handler
        if not self.Status("Requesting public key..."):
            return
        node.push_request(netbase.COMMAND_CHECKORDER, sending_dialog_on_reply2, self, self.wtx)

    def OnRelay2(self, recv):
        """

        :param recv:
        :type recv: serialize.PyDataStream
        :return:
        """
        if not self.Status("Received public key..."):
            return

        script_pubkey = Script.PyScript()
        ret = 0
        try:
            ret = recv.stream_out(out_type="int")
            if ret > 0:
                msg = recv.stream_out(out_type='str')
                self.Error("Transfer was not accepted, msg: %s" % msg)
                return

            script_pubkey.extend(recv.stream_out(out_type='str'), raw=True)
        except:
            self.Error("Invalid response received")
            return

        # Should already be connected
        node = netaction.connect_node(self.addr, 5 * 60)
        if node is None:
            self.Error("Lost connection")
            return

        # Pause to give the user a chance to cancel
        while wx.DateTime.UNow() < self.start + wx.TimeSpan(0, 0, 0, 2 * 1000):
            timeutil.sleep_msec(200)
            if not self.Status():
                return

        with ctx.mainLock:
            balance = txaction.get_balance()
            # pay
            if not self.Status("Creating transaction..."):
                return
            if self.price + ctx.transactionFee > balance:
                self.Error("You don't have enough money")
                return
            fee_required = list()
            ret = txaction.create_transaction(script_pubkey, self.price, self.wtx, fee_required=fee_required)
            if ret is None:
                if self.price + fee_required[0] > balance:
                    self.Error("This is an oversized transaction that requires a transaction fee of %s" %
                               util.format_money(fee_required[0]))
                else:
                    self.Error("Transaction creation failed")
                return
            # las chance to cancel
            timeutil.sleep_msec(50)
            if not self.Status():
                return
            self.can_cancel = False
            if self.abort:
                self.can_cancel = True
                if not self.Status():
                    return
                self.can_cancel = False
            if not self.Status("Sending payment..."):
                return

            # Commit
            if not txaction.commit_transaction_spend(self.wtx):  # in mainLock
                self.Error("Error finalizing payment")
                return

            # Send payment tx to seller, with response going to OnReply3 via event handler
            if not self.Status("Requesting public key..."):
                return
            node.push_request(netbase.COMMAND_SUBMITORDER, sending_dialog_on_reply3, self, self.wtx)

            # Accept and broadcast transaction
            if not self.wtx.accept_transaction():
                print("ERROR: SendingDialog : wtxNew.AcceptTransaction() %s failed" % self.wtx.get_hash(out_type="hex"))
            self.wtx.relay_wallet_transaction()

            self.Status("Waiting for confirmation...")

            # TODO 检查跨线程
            ui.mainframe_repaint()
            pass  # end block
        pass

    def OnRelay3(self, recv):
        """

        :param recv:
        :type recv: serialize.PyDataStream
        :return:
        """
        try:
            ret = recv.stream_out(out_type='int')
            if ret > 0:
                self.Error("The payment was sent, but the recipient was unable to verify it.\n"
                           "The transaction is recorded and will credit to the recipient if it is valid,\n"
                           "but without comment information.")
                return
        except:
            self.Error("Payment was sent, but an invalid response was received")
            return

        self.success = True
        self.work_done = True
        self.Status("Payment completed")

    pass


def sending_dialog_start_transfer(obj):
    obj.StartTransfer()


def sending_dialog_on_reply2(obj, recv):
    obj.OnRelay2(recv)  # this obj is SendingDialog


def sending_dialog_on_reply3(obj, recv):
    obj.OnRelay3(recv)  # this obj is SendingDialog


class YourAddressDialog(YourAddressDialogBase):
    def __init__(self, parent, init_selected=''):
        super(YourAddressDialog, self).__init__(parent)
        # Init column headers
        self.m_listCtrl.InsertColumn(0, "Name", wx.LIST_FORMAT_LEFT, 200)
        self.m_listCtrl.InsertColumn(1, "Coin Address", wx.LIST_FORMAT_LEFT, 350)
        self.m_listCtrl.SetFocus()
        # Fill listctrl with address book data
        with ctx.dictKeysLock:
            for addr, addrname in ctx.dictAddressBook.iteritems():
                hash160 = keyaction.addr_to_hash160(addr, onlyhash=True)  # hash160 is str
                if hash160 is not None and hash160 in ctx.dictPubKeys:
                    index = insert_line(self.m_listCtrl, addrname, addr)
                    if addr == init_selected:
                        self.m_listCtrl.SetItemState(index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                                                     wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)

    def GetAddress(self):
        index = get_selection(self.m_listCtrl)
        if index == -1:
            return ""
        return get_item_text(self.m_listCtrl, index, 1)

    def OnListEndLabelEdit(self, event):
        # Update address book with edited name
        if event.IsEditCancelled():
            return
        address = get_item_text(self.m_listCtrl, event.GetIndex(), 1)
        keyaction.set_address_book_name(address, event.GetText())
        if ctx.frameMain is not None:
            ctx.frameMain.RefreshListCtrl()

    def OnListItemSelected(self, event):
        pass  # remove event.skip()

    def OnListItemActivated(self, event):
        # Doubleclick returns selection
        self.EndModal(True)

    def OnButtonRename(self, event):
        # Ask new name
        index = get_selection(self.m_listCtrl)
        if index == -1:
            return
        addrname = self.m_listCtrl.GetItemText(index)
        addr = get_item_text(self.m_listCtrl, index, 1)
        dialog = GetTextFromUserDialog(self, "Rename coin Address", "New Name", addrname)
        if not dialog.ShowModal():
            return
        addrname = dialog.GetValue()

        # Change name
        keyaction.set_address_book_name(addr, addrname)
        self.m_listCtrl.SetItemText(index, addrname)
        if ctx.frameMain is not None:
            ctx.frameMain.RefreshListCtrl()

    def OnButtonNew(self, event):
        # Ask name
        dialog = GetTextFromUserDialog(self, "New coin Address", "Name", "")
        if not dialog.ShowModal():
            return
        addrname = dialog.GetValue()

        # Generate new key
        addr = keyaction.pubkey_to_addr(keyaction.generate_new_key())
        keyaction.set_address_book_name(addr, addrname)

        # Add to list and select it
        index = insert_line(self.m_listCtrl, addrname, addr)
        set_selection(self.m_listCtrl, index)
        self.m_listCtrl.SetFocus()

    def OnButtonCopy(self, event):
        # Copy address box to clipboard
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.GetAddress()))
            wx.TheClipboard.Close()
        pass

    def OnButtonOK(self, event):
        self.EndModal(True)

    def OnButtonCancel(self, event):
        self.EndModal(False)

    def OnClose(self, event):
        self.EndModal(False)

    pass


class AddressBookDialog(AddressBookDialogBase):
    def __init__(self, parent, init_selected, sending):
        super(AddressBookDialog, self).__init__(parent)
        self.sending = sending
        if not self.sending:
            self.m_button_cancel.Show(False)

        # Init column headers
        self.m_listCtrl.InsertColumn(0, u"Name", wx.LIST_FORMAT_LEFT, 200)
        self.m_listCtrl.InsertColumn(1, u"Address", wx.LIST_FORMAT_LEFT, 350)
        self.m_listCtrl.SetFocus()

        # Set Icon
        bmp_addr_book = wx.Bitmap(load_img_path(u"addressbook16.bmp"), wx.BITMAP_TYPE_BMP)
        bmp_addr_book.SetMask(wx.Mask(wx.Bitmap(load_img_path(u"addressbook16mask.bmp"), wx.BITMAP_TYPE_BMP)))
        icon_addr_book = wx.Icon(load_img_path(u"addressbook16.bmp"))
        icon_addr_book.CopyFromBitmap(bmp_addr_book)
        self.SetIcon(icon_addr_book)

        # Fill listctrl with address book data
        with ctx.dictKeysLock:
            for addr, addrname in ctx.dictAddressBook.iteritems():
                hash160 = keyaction.addr_to_hash160(addr, onlyhash=True)
                if not (hash160 is not None and hash160 in ctx.dictKeys):
                    index = insert_line(self.m_listCtrl, addrname, addr)
                    if addr == init_selected:
                        self.m_listCtrl.SetItemState(index, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                                                     wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
        pass

    def GetAddress(self):
        index = get_selection(self.m_listCtrl)
        if index == -1:
            return ""
        return get_item_text(self.m_listCtrl, index, 1)

    def OnListEndLabelEdit(self, event):
        # Update address book with edited name
        if event.IsEditCancelled():
            return
        addr = get_item_text(self.m_listCtrl, event.GetIndex(), 1)
        keyaction.set_address_book_name(addr, event.GetText())
        if ctx.frameMain is not None:
            ctx.frameMain.RefreshListCtrl()
        pass

    def OnListItemSelected(self, event):
        pass  # remove event.skip()

    def OnListItemActivated(self, event):
        if self.sending:
            # Doubleclick returns selection
            self.EndModal(2 if self.GetAddress()  else 0)
        else:
            # Doubleclick edits item
            self.OnButtonEdit(wx.CommandEvent())
        pass

    def OnButtonEdit(self, event):
        # // Ask new name
        index = get_selection(self.m_listCtrl)
        if index == -1:
            return
        addrname = self.m_listCtrl.GetItemText(index)
        addr = get_item_text(self.m_listCtrl, index, 1)
        addr_org = addr
        dialog = GetTextFromUserDialog(self, "Edit Address", "Name", addrname, "Address", addr)
        if not dialog.ShowModal():
            return
        addrname = dialog.GetValue1()
        addr = dialog.GetValue2()

        # Change name
        if addr != addr_org:
            with Tx.PyWalletDB() as walletdb:
                walletdb.erase_name(addr_org)
        keyaction.set_address_book_name(addr, addrname)
        self.m_listCtrl.SetItem(index, 1, addr)
        self.m_listCtrl.SetItemText(index, addrname)

        if ctx.frameMain is not None:
            ctx.frameMain.RefreshListCtrl()

    def OnButtonNew(self, event):
        # Ask name
        dialog = GetTextFromUserDialog(self, "New Address", "Name", "", "Address", "")
        if not dialog.ShowModal():
            return
        addrname = dialog.GetValue1()
        addr = dialog.GetValue2()

        # Add to list and select it
        keyaction.set_address_book_name(addr, addrname)
        index = insert_line(self.m_listCtrl, addrname, addr)
        set_selection(self.m_listCtrl, index)
        self.m_listCtrl.SetFocus()

    def OnButtonDelete(self, event):
        for i in range(self.m_listCtrl.GetItemCount()):
            if self.m_listCtrl.GetItemState(i, wx.LIST_STATE_SELECTED):
                addr = get_item_text(self.m_listCtrl, i, 1)
                walletdb = Tx.PyWalletDB()
                walletdb.erase_name(addr)
                walletdb.close()
                self.m_listCtrl.DeleteItem(i)
        if ctx.frameMain is not None:
            ctx.frameMain.RefreshListCtrl()

    def OnButtonOK(self, event):
        self.EndModal(1 if self.GetAddress() else 0)

    def OnButtonCancel(self, event):
        self.EndModal(0)

    def OnClose(self, event):
        self.EndModal(0)

    pass


class ProductsDialog(ProductsDialogBase):
    def __init__(self, parent):
        super(ProductsDialog, self).__init__(parent)

        # Init column headers
        self.m_listCtrl.InsertColumn(0, u"Title", wx.LIST_FORMAT_LEFT, 200)
        self.m_listCtrl.InsertColumn(1, u"Price", wx.LIST_FORMAT_LEFT, 80)
        self.m_listCtrl.InsertColumn(2, u"Seller", wx.LIST_FORMAT_LEFT, 80)
        self.m_listCtrl.InsertColumn(3, u"Stars", wx.LIST_FORMAT_LEFT, 50)
        self.m_listCtrl.InsertColumn(4, u"Power", wx.LIST_FORMAT_LEFT, 50)

        # Tally top categories
        dict_top_categories = defaultdict(int)
        with ctx.dictProductsLock:
            for product in ctx.dictProducts.itervalues():
                dict_top_categories[product.dict_value["category"]] += 1
        # Sort top categories
        list_top_categories = dict_top_categories.items()  # dict<string, int>
        list_top_categories.sort(key=lambda x: x[1], reverse=False)

        # Fill categories combo box
        limit = 250
        for category, index in list_top_categories:
            if limit <= 0:
                break
            limit -= 1
            self.m_comboBox_category.Append(category)

        self._list_products = list()

    def OnCombobox(self, event):
        self.OnButtonSearch(event)

    def OnButtonSearch(self, event):
        category = self.m_comboBox_category.GetValue()
        search = self.m_textCtrl_search.GetValue()

        # Search products
        list_products_found = list()
        with ctx.dictProductsLock:
            for product in ctx.dictProducts:  # O(n)
                if product.dict_value["category"].find(category) != -1:
                    if product.dict_value["title"].find(search) != -1 or \
                                    product.dict_value["description"].find(search) != -1 or \
                                    product.dict_value["seller"].find(search) != -1:
                        list_products_found.append(product)

        # Sort
        list_products_found.sort(key=lambda x: x.atoms, reverse=True)

        # Display
        for product in list_products_found:
            insert_line(self.m_listCtrl,
                        product.dict_value["title"],
                        product.dict_value["price"],
                        product.dict_value["seller"],
                        product.dict_value["stars"],
                        str(product.nAtoms))
        self._list_products = list_products_found

    def OnListItemActivated(self, event):
        # Doubleclick opens product
        index = int(event.GetIndex())
        product = self._list_products[index]
        dialog = ViewProductDialog(self, product)
        dialog.Show()
        pass

    pass


class EditProductDialog(EditProductDialogBase):
    FIELDS_MAX = 20

    def __init__(self, parent):
        super(EditProductDialog, self).__init__(parent)

        for i in range(EditProductDialog.FIELDS_MAX):
            self.ShowLine(i, False)
        self.LayoutAll()

    def LayoutAll(self):
        self.m_scrolled_window.Layout()
        self.m_scrolled_window.GetSizer().Fit(self.m_scrolled_window)
        self.Layout()

    def ShowLine(self, i, show):
        self.m_textCtrlLabel[i].Show(show)
        self.m_textCtrlField[i].Show(show)
        self.m_buttonDel[i].Show(show)
        pass

    def OnButtonDel0(self, event):
        self.OnButtonDel(event, 0)

    def OnButtonDel1(self, event):
        self.OnButtonDel(event, 1)

    def OnButtonDel2(self, event):
        self.OnButtonDel(event, 2)

    def OnButtonDel3(self, event):
        self.OnButtonDel(event, 3)

    def OnButtonDel4(self, event):
        self.OnButtonDel(event, 4)

    def OnButtonDel5(self, event):
        self.OnButtonDel(event, 5)

    def OnButtonDel6(self, event):
        self.OnButtonDel(event, 6)

    def OnButtonDel7(self, event):
        self.OnButtonDel(event, 7)

    def OnButtonDel8(self, event):
        self.OnButtonDel(event, 8)

    def OnButtonDel9(self, event):
        self.OnButtonDel(event, 9)

    def OnButtonDel10(self, event):
        self.OnButtonDel(event, 10)

    def OnButtonDel11(self, event):
        self.OnButtonDel(event, 11)

    def OnButtonDel12(self, event):
        self.OnButtonDel(event, 12)

    def OnButtonDel13(self, event):
        self.OnButtonDel(event, 13)

    def OnButtonDel14(self, event):
        self.OnButtonDel(event, 14)

    def OnButtonDel15(self, event):
        self.OnButtonDel(event, 15)

    def OnButtonDel16(self, event):
        self.OnButtonDel(event, 16)

    def OnButtonDel17(self, event):
        self.OnButtonDel(event, 17)

    def OnButtonDel18(self, event):
        self.OnButtonDel(event, 18)

    def OnButtonDel19(self, event):
        self.OnButtonDel(event, 19)

    def OnButtonDel(self, event, n):
        self.Freeze()
        point = self.m_scrolled_window.GetViewStart()

        index = 0
        for i in range(n, EditProductDialog.FIELDS_MAX - 1):
            self.m_textCtrlLabel[i].SetValue(self.m_textCtrlLabel[i + 1].GetValue())
            self.m_textCtrlField[i].SetValue(self.m_textCtrlField[i + 1].GetValue())
            index = i
            if not self.m_buttonDel[i + 1].IsShown():
                break
        self.m_textCtrlLabel[index].SetValue("")
        self.m_textCtrlField[index].SetValue("")
        self.ShowLine(index, False)
        self.m_button_addfield.Enable(True)
        self.LayoutAll()
        self.m_scrolled_window.Scroll(0, point.Get()[1])  # point.Get() . (x, y)
        self.Thaw()

    def OnButtonAddField(self, event):
        for i in range(EditProductDialog.FIELDS_MAX):
            if not self.m_buttonDel[i].IsShown():
                self.Freeze()
                self.ShowLine(i, True)
                if i == EditProductDialog.FIELDS_MAX - 1:
                    self.m_button_addfield.Enable(False)
                self.LayoutAll()
                self.m_scrolled_window.Scroll(0, 99999)
                self.Thaw()
                break

    def OnButtonSend(self, event):
        product = self.GetProduct()
        # Sign the detailed product
        product.pubkey_from = ctx.keyUser.get_pubkey()
        sig_ret = ctx.keyUser.sign(product.get_sig_hash())
        if sig_ret is None:
            wx.MessageBox("Error digitally signing the product ")
            return
        product.sig = sig_ret

        # Save detailed product
        add_to_my_products(product)

        # Strip down to summary product
        product.dict_details.clear()
        product.list_order_from.clear()

        # Sign the summary product
        sig_ret = ctx.keyUser.sign(product.get_sig_hash())
        if sig_ret is None:
            wx.MessageBox("Error digitally signing the product ")
            return
        # Verify
        if not product.check_product():
            wx.MessageBox("Errors found in product ")
            return
        # Broadcast
        Net.advert_start_publish(ctx.nodeLocalHost, Net.MsgType.MSG_PRODUCT, 0, product)

        self.Destroy()

    def SetProduct(self, product):
        """

        :param product:
        :type product: Block.PyWalletTx
        :return:
        """
        self.m_comboBox_category.SetValue(product.dict_value["category"])
        self.m_textCtrl_title.SetValue(product.dict_value["title"])
        self.m_textCtrl_price.SetValue(product.dict_value["price"])
        self.m_textCtrl_description.SetValue(product.dict_value["description"])
        self.m_textCtrl_instructions.SetValue(product.dict_value["instructions"])

        for i in range(EditProductDialog.FIELDS_MAX):
            f_used = i < len(product.list_order_form)
            self.m_buttonDel[i].Show(f_used)
            self.m_textCtrlLabel[i].Show(f_used)
            self.m_textCtrlField[i].Show(f_used)
            if not f_used:
                continue
            self.m_textCtrlLabel[i].SetValue(product.list_order_form[i][0])  # vector<pair<string,string>>
            control = product.list_order_form[i][1]
            if control[:5] == "text=":
                self.m_textCtrlField[i].SetValue("")
            elif control[:7] == "choice=":
                self.m_textCtrlField[i].SetValue(control[7:])
            else:
                self.m_textCtrlField[i].SetValue(control)
        pass

    def GetProduct(self, product=None):
        """

        :param product:
        :type product: market.PyProduct
        :return:
        :rtype product: market.PyProduct
        """
        if product is None:
            product = market.PyProduct()
            s = ''
            s.strip()
        product.dict_value["category"] = self.m_comboBox_category.GetValue().strip()
        product.dict_value["title"] = self.m_textCtrl_title.GetValue().strip()
        product.dict_value["price"] = self.m_textCtrl_price.GetValue().strip()
        product.dict_value["description"] = self.m_textCtrl_description.GetValue().strip()
        product.dict_value["instructions"] = self.m_textCtrl_instructions.GetValue().strip()

        for i in range(EditProductDialog.FIELDS_MAX):
            if self.m_buttonDel[i].IsShown():
                label = self.m_textCtrlLabel[i].GetValue().strip()
                control = self.m_textCtrlField[i].GetValue()
                if len(control) == 0:
                    control = "text="
                else:
                    control = "choice=" + control
                product.list_order_from.append((label, control))
        return product

    pass


class ViewProductDialog(ViewProductDialogBase):
    FIELDS_MAX = 20

    def __init__(self, parent, product):
        """

        :param parent:
        :param product:
        :type product: market.PyProduct
        """
        super(ViewProductDialog, self).__init__(parent)
        self.Bind(EVT_REPLY1, self.OnReply1, None)
        add_callback_available(self.GetEventHandler())

        self.product = product
        self.UpdateProductDisplay(False)
        self.m_button_back.Enable(False)
        self.m_button_next.Enable(len(product.list_order_from) != 0)
        self.m_html_winreviews.Show(True)
        self.m_scrolled_window.Show(True)
        self.Layout()

        self._staticTextLabel = [None] * ViewProductDialog.FIELDS_MAX
        self._textCtrlField = [None] * ViewProductDialog.FIELDS_MAX
        self._choiceField = [None] * ViewProductDialog.FIELDS_MAX

        # Request details from seller
        threading.Thread(target=thread_request_product_details,
                         name="ViewProductDialog:thread_request_product_details(obj)",
                         args=((product, self.GetEventHandler()),))

    def __del__(self):
        remove_callback_available(self.GetEventHandler())

    def OnReply1(self, event):  # event: wx.CommandEvent
        ss = get_stream_from_event(event)
        if not len(ss):
            self.product.dict_value["description"] = "-- CAN'T CONNECT TO SELLER --\n"
            self.UpdateProductDisplay(True)
            return

        try:
            ret = ss.stream_out(out_type='int')
            if ret > 0:
                raise ValueError("False")
            product_tmp = ss.stream_out(cls=market.PyProduct)
            if product_tmp.get_hash() != self.product.get_hash():
                raise ValueError("False")
            if not product_tmp.check_signature():
                raise ValueError("False")
        except:
            self.product.dict_value["description"] = "-- INVALID RESPONSE --\n"
            self.UpdateProductDisplay(True)
            return
        self.product = product_tmp
        self.UpdateProductDisplay(True)
        pass

    def UpdateProductDisplay(self, details):
        # Product and reviews
        buff = list()
        buff.append("<html>\n"
                    "<head>\n"
                    "<meta http-equiv=\"content-type\" content=\"text/html charset=UTF-8\">\n"
                    "</head>\n"
                    "<body>\n")

        buff.append("<b>Category:</b> " + html_escape(self.product.dict_value["category"]) + "<br>\n")
        buff.append("<b>Title:</b> " + html_escape(self.product.dict_value["title"]) + "<br>\n")
        buff.append("<b>Price:</b> " + html_escape(self.product.dict_value["price"]) + "<br>\n")

        if not details:
            buff.append("<b>Loading details...</b><br>\n<br>\n")
        else:
            buff.append(html_escape(self.product.dict_value["description"], True) + "<br>\n<br>\n")

        buff.append("<b>Reviews:</b><br>\n<br>\n")

        if self.product.pubkey_from:
            reviewdb = market.PyReviewDB("r")
            # Get reviews
            list_reviews = reviewdb.read_reviews(self.product.get_user_hash())
            sorted_reviews = list()
            for r in list_reviews:
                user = reviewdb.read_user(r.get_user_hash())
                r.atoms = user.get_atom_count()
                sorted_reviews.append(r)
            reviewdb.close()
            # sort
            sorted_reviews.sort(key=lambda x: x.atoms, reverse=True)
            # display
            for r in sorted_reviews:
                stars = int(r.dict_value["stars"])
                if stars < 1 or stars > 5:
                    continue

                buff.append("<b>" + str(stars) + (" star" if stars == 1 else " stars") + "</b>")
                buff.append(" &nbsp&nbsp&nbsp ")
                buff.append(date_str(int(r.dict_value["date"])) + "<br>\n")
                buff.append(html_escape(r.dict_value["review"], True))
                buff.append("<br>\n<br>\n")
        buff.append("</body>\n</html>\n")
        # Shrink capacity to fit
        self.m_html_winreviews.SetPage("".join(buff))

        # need to find some other indicator to use so can allow empty order form
        if not self.product.list_order_from:
            return
        # Order form
        self.m_staticText_instructions.SetLabel(self.product.dict_value["instructions"])

        # Construct flexgridsizer
        bSizer = self.m_scrolled_window.GetSizer()
        fgSizer = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer.AddGrowableCol(1)
        fgSizer.SetFlexibleDirection(wx.BOTH)
        fgSizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        # Construct order form fields
        window_last = None
        for i, item in enumerate(self.product.list_order_from):
            label, control = item
            if len(label) < 20:
                label += " " * (20 - len(label))

            self._staticTextLabel[i] = wx.StaticText(self.m_scrolled_window, wx.ID_ANY, label,
                                                     wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT)
            self._staticTextLabel[i].Wrap(-1)
            fgSizer.Add(self._staticTextLabel[i], 0,
                        wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

            if control[:5] == "text=":
                self._textCtrlField[i] = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY, wx.EmptyString,
                                                     wx.DefaultPosition, wx.DefaultSize, 0)
                fgSizer.Add(self._textCtrlField[i], 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 5)
                window_last = self._textCtrlField[i]
            elif control[:7] == "choice=":
                choices = control[7:]
                choices = choices.split(',')
                self._choiceField[i] = wx.Choice(self.m_scrolled_window, wx.ID_ANY,
                                                 wx.DefaultPosition, wx.DefaultSize, choices, 0)
                fgSizer.Add(self._choiceField[i], 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                window_last = self._choiceField[i]
            else:
                self._textCtrlField[i] = wx.TextCtrl(self.m_scrolled_window, wx.ID_ANY,
                                                     wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
                fgSizer.Add(self._textCtrlField[i], 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 5)
                self._staticTextLabel[i].Show(False)
                self._textCtrlField[i].Show(False)
            pass

        # Insert after instructions and before submit / cancel buttons
        bSizer.Insert(2, fgSizer, 0, wx.EXPAND | wx.RIGHT | wx.LEFT, 5)
        self.m_scrolled_window.Layout()
        bSizer.Fit(self.m_scrolled_window)
        self.Layout()

        # Fixup the tab order
        self.m_button_submitform.MoveAfterInTabOrder(window_last)
        self.m_button_submitform.MoveAfterInTabOrder(self.m_button_submitform)
        self.Layout()

    def GetOrder(self):
        """

        :return:
        :rtype Block.PyWalletTx
        """
        wtx = Block.PyWalletTx()
        for i in range(len(self.product.list_order_from)):
            if self._textCtrlField[i]:
                value = self._textCtrlField[i].GetValue().strip()
            else:
                value = self._choiceField[i].GetStringSelection()
            wtx.list_order_form.append((self._staticTextLabel[i].GetLabel(), value))
        return wtx

    def OnButtonSubmitForm(self, event):
        self.m_button_submitform.Enable(False)
        self.m_button_cancelform.Enable(False)

        wtx = self.GetOrder()

        dialog = SendingDialog(self, self.product.addr, int(self.product.dict_value["price"]), wtx)
        if not dialog.ShowModal():
            self.m_button_submitform.Enable(True)
            self.m_button_cancelform.Enable(True)
            return

    def OnButtonCancelForm(self, event):
        self.Destroy()

    def OnButtonBack(self, event):
        self.Freeze()
        self.m_html_winreviews.Show(True)
        self.m_scrolled_window.Show(False)
        self.m_button_back.Enable(False)
        self.m_button_next.Enable(len(self.product.list_order_from) != 0)
        self.Layout()
        self.Thaw()

    def OnButtonNext(self, event):
        if self.product.list_order_from:
            self.Freeze()
            self.m_html_winreviews.Show(False)
            self.m_scrolled_window.Show(True)
            self.m_button_back.Enable(True)
            self.m_button_next.Enable(False)
            self.Layout()
            self.Thaw()

    def OnButtonCancel(self, event):
        self.Destroy()

    pass


def thread_request_product_details(obj):
    # Extract parameters
    item = obj  # pair<PyProduct, wx.EvtHandler>
    product = item[0]
    evthandler = item[1]
    # Connect to seller
    node = netaction.connect_node(product.addr, 5 * 60)
    if node is not None:
        empty = serialize.PyDataStream()
        add_pending_reply_event1(evthandler, empty)
        return
    # Request detailed product, with response going to OnReply1 via dialog's event handler
    node.push_request(netbase.COMMAND_GETDETAILS, add_pending_reply_event1, evthandler, (product.get_hash(), 'uint256'))


class ViewOrderDialog(ViewOrderDialogBase):
    def __init__(self, parent, order, received):
        """

        :param parent:
        :param order:
        :type order: Block.PyWalletTx
        :param received:
        """
        super(ViewOrderDialog, self).__init__(parent)
        price = order.get_credit() if received else order.get_debit()
        html = self.__create_html(order, price)
        self.m_html_win.SetPage(html)

    @staticmethod
    def __create_html(order, price):
        """

        :param order:
        :type order: Block.PyWalletTx
        :return:
        """
        html = "".join(("<html>\n",
                        "<head>\n",
                        "<meta http-equiv=\"content-type\" content=\"text/html charset=UTF-8\">\n",
                        "</head>\n",
                        "<body>\n",
                        "<b>Time:</b> ", html_escape(timeutil.date_time_str(order.nTimeReceived)), "<br>\n",
                        "<b>Price:</b> ", html_escape(util.format_money(price)), "<br>\n",
                        "<b>Status:</b> ", html_escape(format_tx_status(order)), "<br>\n",
                        "<table>\n",
                        "</body>\n</html>\n"))
        return html

    def OnButtonOK(self, event):
        self.Destroy()

    pass


class EditReviewDialog(EditReviewDialogBase):
    def GetReview(self, review=None):
        if review is None:
            review = market.PyReview()

        review.dict_value["time"] = str(timeutil.get_adjusted_time())
        review.dict_value["stars"] = str(self.m_choice_stars.GetSelection() + 1)
        review.dict_value["review"] = self.m_textCtrl_review.GetValue()
        return review

    def OnButtonSubmit(self, event):
        if self.m_choice_stars.GetSelection() == -1:
            wx.MessageBox("Please select a rating ")
            return
        review = self.GetReview()

        # Sign the review
        review.pubkey_from = ctx.keyUser.get_pubkey()
        sig_ret = ctx.keyUser.sign(review.get_sig_hash())
        if sig_ret is None:
            wx.MessageBox("Unable to digitally sign the review ")
            return
        review.sig = sig_ret
        # Broadcast
        if not review.accept_review():
            wx.MessageBox("Save failed ")
            return
        netaction.relay_message(Net.PyInv(Net.MsgType.MSG_REVIEW, review.get_hash()), review)

        self.Destroy()

    def OnButtonCancel(self, event):
        self.Destroy()

    pass


class GetTextFromUserDialog(GetTextFromUserDialogBase):
    def __init__(self, parent, caption, msg1, value1='', msg2='', value2=''):
        super(GetTextFromUserDialog, self).__init__(parent)
        self.m_staticText_msg1.SetLabel(msg1)
        self.m_textCtrl1.SetValue(value1)
        if msg2:
            self.m_staticText_msg2.Show(True)
            self.m_staticText_msg2.SetLabel(msg2)
            self.m_textCtrl2.Show(True)
            self.m_textCtrl2.SetValue(value2)
            self.SetSize((wx.DefaultCoord, 250), )

    def OnButtonOK(self, event):
        self.EndModal(True)

    def OnButtonCancel(self, event):
        self.EndModal(False)

    def OnClose(self, event):
        self.EndModal(False)

    def OnKeyDown(self, event):
        if event.GetKeyCode() == '\r' or event.GetKeyCode() == wx.WXK_NUMPAD_ENTER:
            self.EndModal(True)
        else:
            handle_ctrl_A(event)

    def GetValue(self):
        return self.m_textCtrl1.GetValue()

    def GetValue1(self):
        return self.m_textCtrl1.GetValue()

    def GetValue2(self):
        return self.m_textCtrl2.GetValue()


def main():
    pass


if __name__ == '__main__':
    main()

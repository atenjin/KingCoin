#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import random
import wx
from app import context as ctx
from app.base import serialize, ui
from app.block import block as Block
from app.block.tx import tx as Tx, script as Script
from app.utils import util


##########
# actions
##
def get_balance():
    total = 0
    with ctx.dictWalletLock:
        # coin is PyWalletTx
        for coin in ctx.dictWallet.itervalues():
            if not coin.is_final() or coin.spent:
                continue
            total += coin.get_credit()
    return total


def select_coins(target_value):
    """
    根据target_value的值从自己的wallet钱包中选取出合适的交易\n
    若钱包的钱总额达不到 target 则返回None \n
    :param target_value:
    :return: 能用于支付的交易集合 set<PyWalletTx> 或 None
    :rtype set | None
    """
    set_coins = set()  # set<PyWalletTx>

    lowest_larger = 0x7FFFFFFFFFFFFFFF  # int64_max  # 超过target_value的最大的交易持有的钱
    coin_lowest_larger = None  # 超过target_value的最大的交易
    value = list()  # tuple for (coin,tx)
    total_lower = 0  # 小于target的小钱的总数
    # with ctx.dictWalletLock:
    # coin is PyWalletTx
    for coin in ctx.dictWallet.itervalues():  # 这里是收集自己钱包里满足条件的交易
        if not coin.is_final() or coin.spent:  # 应该是筛选出没有被花掉的交易
            continue
        n = coin.get_credit()  # 这个wallettx转给自己的coin
        if n <= 0:  # 没钱...
            continue
        if n < target_value:  # target_value 表面想要转账的数目
            value.append((n, coin))  # 这里先把小于转账的钱对应的交易存入
            total_lower += n
        elif n == target_value:  # 刚好有符合数目的钱
            set_coins.add(coin)  # 就把对应的交易放入set
            return set_coins
        elif n < lowest_larger:
            lowest_larger = n
            coin_lowest_larger = coin

    if total_lower < target_value:  # 如果小钱总数小于要求
        if coin_lowest_larger is None:  # 如果超过的都没有就是真没钱了
            return None
        set_coins.add(coin_lowest_larger)
        return set_coins

    # Solve subset sum by stochastic approximation
    value.sort(key=lambda x: x[0])

    value_size = len(value)
    flag_best = [True for _ in range(value_size)]
    best = total_lower  # 小钱总数，已经大于 target
    for _ in range(1000):
        if best == target_value:
            break

        flag_included = [False for _ in range(value_size)]
        total = 0
        reached_target = False
        for npass in range(2):
            if reached_target:
                break
            for i in range(value_size):
                if (random.randint(0, 3) % 2 if npass == 0 else not flag_included[i]):
                    total += value[i][0]
                    flag_included[i] = True
                    if total >= target_value:
                        reached_target = True
                        if total < best:
                            best = total
                            flag_best = flag_included[:]  # copy
                        total -= value[i][0]
                        flag_included[i] = False

    # If the next larger is still closer, return it
    if coin_lowest_larger and (lowest_larger - target_value <= best - target_value):
        set_coins.add(coin_lowest_larger)
    else:
        for i in range(value_size):
            if flag_best[i]:
                set_coins.add(value[i][1])

        ## debug print
        print ("SelectCoins() best subset: ")
        for i in range(value_size):
            if flag_best[i]:
                print ("%s " % util.format_money(value[i][0]))
        print ("total %s\n" % util.format_money(best))

    return set_coins


def create_transaction(script_pubkey, value, wtx_new, fee_required=None):
    """
    根据指向自己的PyWalletTx的Out填充wtx_new的 PyTxIn, value指明转账费, 将会验证交易费，合法性，\n
    并自动收集满足条件的交易, 并对 wtx_new 的 PyTxIn进行签名\n
    :param script_pubkey: 填充 wtx_new PyTxOut 的 pubkey_script
    :param value: 转账的数目
    :param wtx_new: 被填充的交易
    :type wtx_new: Block.PyWalletTx
    :return: None 或 需要支付的交易费 fee
    """
    if fee_required is None:
        fee_required = list()
    if len(fee_required) == 0:
        fee_required.append(0)
    else:
        fee_required[0] = 0

    with ctx.mainLock:
        with Tx.PyTxDB("r") as txdb:
            with ctx.dictWalletLock:
                # txdb = Tx.PyTxDB("r")
                fee = ctx.transactionFee  # 全局配置的交易费
                while True:
                    del wtx_new.l_in[:]
                    del wtx_new.l_out[:]

                    if value < 0:
                        return None

                    value_out = value  # 此时的value_out 代表真正想要转出的钱
                    value += fee  # 此时 value 包含手续费
                    # Choose coins to use
                    set_coins = select_coins(value)
                    if set_coins is None:
                        return None
                    set_coins = tuple(set_coins)
                    value_in = 0  # 获取自己能给出的全部钱总和
                    for coin in set_coins:  # PyWalletTx
                        value_in += coin.get_credit()

                    # Fill vout[0] to the payee
                    wtx_new.l_out.append(Tx.PyTxOut(value_out, script_pubkey))

                    # Fill vout[1] back to self with any change
                    if value_in > value:  # value 包含了手续费
                        # Use the same key as one of the coins
                        tx_first = set_coins[0]
                        pubkey = b''
                        for txout in tx_first.l_out:
                            if txout.is_mine():
                                pubkey = Script.extract_pubkey(txout.script_pubkey, True)
                                if pubkey is not None:
                                    break
                        if len(pubkey) == 0:
                            return None

                        # Fill vout[1] to ourself
                        my_script_pubkey = Script.PyScript()
                        my_script_pubkey.extend(pubkey).append(Script.OpCodeType.OP_CHECKSIG)
                        wtx_new.l_out.append(Tx.PyTxOut(value_in - value, my_script_pubkey))

                    # fill vin
                    for coin in set_coins:
                        for index, out in enumerate(coin.l_out):
                            if out.is_mine():
                                wtx_new.l_in.append(Tx.PyTxIn(Tx.PyOutPoint(coin.get_hash(), index)))  # no sign

                    # Sign
                    nin = 0
                    for coin in set_coins:
                        for out in coin.l_out:
                            if out.is_mine():
                                ret = Script.sign_signature(coin, wtx_new, nin)
                                if ret is False:
                                    print ("sign failed for txin index: %d: to wtx_new: %s" % (nin, str(wtx_new)))
                                    return None
                                nin += 1

                    # Check that enough fee is included
                    real_fee = wtx_new.get_min_fee(True)  # 如果交易费小于最小的交易费，那么就要调整并重新运算
                    if fee < real_fee:
                        fee = real_fee
                        fee_required[0] = fee
                        continue

                    wtx_new.add_supporting_transactions(txdb)
                    wtx_new.time_received_is_tx_time = 1  # 该函数只会由生产tx的节点调用，这个属性的意义就代表的这个wtx是自己产生的还是别人

                    break
    return fee


# Call after CreateTransaction unless you want to abort
def commit_transaction_spend(wtx_new):
    """
    在create_transaction 之后，需要修改本地的Tx信息
    :param wtx_new:
    :type wtx_new: Block.PyWalletTx
    :return:
    """
    with ctx.mainLock:
        with ctx.dictWalletLock:
            # todo: make this transactional, never want to add a transaction
            # without marking spent transactions
            # Add tx to wallet, because if it has change it's also ours,
            # otherwise just for transaction history.
            Block.add_to_wallet(wtx_new)
            # Mark old coins as spent
            set_coins = set()
            for txin in wtx_new.l_in:
                set_coins.add(ctx.dictWallet[txin.prev_out.hash_tx])
            for coin in set_coins:  # coin is WalletTx
                coin.spent = 1
                coin.write_to_disk()
                ctx.listWalletUpdated.append((coin.get_hash(), False))

    ui.mainframe_repaint()
    return True


def send_money(script_pubkey, value, wtx_new, ignoreui=True):
    """
    发送 value 的coin
    :param script_pubkey:
    :param value:
    :param wtx_new:
    :type wtx_new: Block.PyWalletTx
    :return:
    :rtype bool
    """
    with ctx.mainLock:
        fee_required = list()
        fee = create_transaction(script_pubkey, value, wtx_new, fee_required)
        if fee is None:
            if value + fee_required[0] > get_balance():
                str_error = "Error: This is an oversized transaction that requires a transaction fee of %s " \
                            % util.format_money(fee)
            else:
                str_error = "Error: Transaction creation failed "

            if not ignoreui:
                wx.MessageBox(str_error, "Sending...")
            print ("SendMoney() : %s" % str_error)
            return False

        if not commit_transaction_spend(wtx_new):
            if not ignoreui:
                wx.MessageBox("Error finalizing transaction", "Sending...")
            print ("SendMoney() : Error finalizing transaction")
            return False

        print ("SendMoney: %s\n" % serialize.hexser_uint256(wtx_new.get_hash())[:6])

        # Broadcast
        if not wtx_new.accept_transaction():  # TODO reject at this point
            # This must not fail. The transaction has already been signed and recorded.
            if not ignoreui:
                wx.MessageBox("Error: Transaction not valid", "Sending...")
            print ("SendMoney() : Error: Transaction not valid")
            return False
        wtx_new.relay_wallet_transaction()

    if not ignoreui:
        ui.mainframe_repaint()
    return True


#
# mapOrphanTransactions
#
def add_orphan_tx(msg):
    """

    :param msg:
    :type msg: serialize.PyDataStream
    :return:
    """
    msg_tmp = msg.copy()
    tx = msg_tmp.stream_out(cls=Tx.PyTransaction)
    tx_hash = tx.get_hash()
    if tx_hash in ctx.dictOrphanTransactions:
        return
    msg_new = msg.copy()
    ctx.dictOrphanTransactions[tx_hash] = msg_new
    for txin in tx.l_in:
        ctx.dictOrphanTransactionsByPrev[txin.prev_out.hash_tx].append(msg_new)
    pass


def erase_orphan_tx(tx_hash):
    msg = ctx.dictOrphanTransactions.get(tx_hash, None)
    if msg is None:
        return
    msg_tmp = msg.copy()
    tx = msg_tmp.stream_out(cls=Tx.PyTransaction)
    for txin in tx.l_in:
        remove_list = list()
        prev_hash = txin.prev_out.hash_tx
        for index, data in enumerate(ctx.dictOrphanTransactionsByPrev[prev_hash]):  # list<PyDataStream>
            if id(data) == id(msg):
                remove_list.append(index)
        [tx.dictOrphanTransactionsByPrev[prev_hash].pop(i) for i in remove_list]
    del msg  # msg is add_orphan_tx->msg_new
    ctx.dictOrphanTransactions.pop(tx_hash)
    pass


def main():
    pass


if __name__ == '__main__':
    main()

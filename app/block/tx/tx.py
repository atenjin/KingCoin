#!/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii

from app import context as ctx
from app.base.serialize import *
from app.block.tx import script as Script
from app.block.tx.script import is_mine, verify_signature
from app.block.utils import util, cryptoutil
from app.db import db
from app.utils import timeutil


def _money_range(nValue):
    return 0 <= nValue <= cfg.MAX_MONEY


class PyInPoint(object):
    def __init__(self, tx=None, n=0xffffffff):
        self.py_tx = None
        self.index = 0xffffffff
        if tx is not None:
            self.py_tx = tx
            self.index = n

    def set_null(self):
        self.py_tx = None
        self.index = 0xffffffff

    def is_null(self):
        return self.py_tx is None and self.index == 0xffffffff

    pass


class PyOutPoint(Serializable):
    def __init__(self, tx_hash=0, index=0xffffffff):
        self.hash_tx = tx_hash  # l_in 中 PyTxIn 对应的Tx 的hash
        self.index = index  # 当前Tx 的 l_in 中 PyTxIn这个in是对应的Tx 的第n个 output

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        f = wrap_to_StringIO(f)
        self.hash_tx = deser_uint256(f)
        self.index = deser_uint(f)
        return self

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        s = StringIO()
        s.write(ser_uint256(self.hash_tx))
        s.write(ser_uint(self.index))
        return s.getvalue()

    def set_null(self):
        self.hash_tx = 0
        self.index = 0xffffffff

    def is_null(self):
        return (self.hash_tx == 0) and (self.index == 0xffffffff)

    def gethash(self):
        return hash(str(self.hash_tx) + str(self.index))

    def __eq__(self, other):
        return self.hash_tx == other.hash_tx and self.index == other.index

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "PyOutPoint(hash=%064x n=%i)" % (self.hash_tx, self.index)


class PyTxIn(Serializable):
    def __init__(self, prev_out=None, script_sig=None, sequence=0xffffffff):
        self.prev_out = PyOutPoint() if prev_out is None else prev_out
        self.script_sig = Script.PyScript() if script_sig is None else script_sig
        self.sequence = sequence

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        f = wrap_to_StringIO(f)
        self.prev_out = PyOutPoint()
        self.prev_out.deserialize(f)
        self.script_sig = Script.PyScript(deser_str(f))
        self.sequence = deser_uint(f)
        return self

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        s = StringIO()
        s.write(self.prev_out.serialize())
        s.write(ser_str(self.script_sig.get_str()))
        s.write(ser_uint(self.sequence))
        return s.getvalue()

    def is_final(self):
        return self.sequence == 0xffffffff  # UINT_MAX

    # def is_valid(self):
    #     script = PyScript()
    #     # if not script.tokenize(self.script_sig):
    #     #     return False
    #     return True

    def is_mine(self):
        """
        判定这个tx的 in 是否 来自 自己
        :return:
        """
        with ctx.dictWalletLock:
            prev_wallet_tx = ctx.dictWallet.get(self.prev_out.hash_tx, None)
            if prev_wallet_tx is not None:
                if self.prev_out.index < len(prev_wallet_tx.l_out):
                    if prev_wallet_tx.l_out[self.prev_out.index].is_mine():
                        return True

        return False

    def get_debit(self):
        with ctx.dictWalletLock:
            if self.prev_out.hash_tx in ctx.dictWallet:
                prev_wallet_tx = ctx.dictWallet.get(self.prev_out.hash_tx, None)
                if prev_wallet_tx is not None:
                    if self.prev_out.index < len(prev_wallet_tx.l_out):
                        if prev_wallet_tx.l_out[self.prev_out.index].is_mine():
                            # wallet_tx.l_out -> PyTxOut  value -> amount
                            return prev_wallet_tx.l_out[self.prev_out.index].value
        return 0

    def __eq__(self, other):
        return self.prev_out == other.prev_out and \
               self.script_sig == other.script_sig and \
               self.sequence == other.sequence

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "PyTxIn(prev_out=%s script_sig=%s sequence=%i)" % (
            repr(self.prev_out), binascii.hexlify(self.script_sig), self.sequence)


class PyTxOut(Serializable):
    def __init__(self, value_out=-1, script_pubkey=None):
        self.value = value_out  # amount  int64
        self.script_pubkey = Script.PyScript() if script_pubkey is None else script_pubkey  # PyScript lock script

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        f = wrap_to_StringIO(f)
        self.value = deser_int64(f)
        self.script_pubkey = Script.PyScript(deser_str(f))
        return self

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        s = StringIO()
        s.write(ser_int64(self.value))
        s.write(ser_str(self.script_pubkey.get_str()))
        return s.getvalue()

    def set_null(self):
        self.value = -1  # amount  int64
        self.script_pubkey = Script.PyScript()  # equal to PyScript

    def is_null(self):
        return self.value == -1

    def get_hash(self, out_type=None):
        return cryptoutil.Hash(serialize_hash(self), out_type=out_type)

    # def is_valid(self):
    #     if not _money_range(self.value):
    #         return False
    #     script = PyScript()
    #     # same equal to is_main
    #     # if not script.tokenize(self.script_pubkey):
    #     #     return False
    #     return True

    def is_mine(self):
        """
        判断out是否指向自己，方法是判断 pubkey_script 中的公钥 是否在本地\n
        :return:
        """
        return is_mine(self.script_pubkey)

    def get_credit(self):
        """
        TxOut 如果是指向自己的，那么就返回这个out的value，表示自己地址上增长的coin\n
        :return:
        """
        if self.is_mine():
            return self.value
        return 0

    def __eq__(self, other):
        return self.value == other.value and \
               self.script_pubkey == other.script_pubkey

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "PyTxOut(value=%i.%08i script_pubkey=%s)" % (
            self.value // cfg.COIN, self.value % cfg.COIN, binascii.hexlify(self.script_pubkey[:24]))


class PyDiskTxPos(Serializable):
    def __init__(self, index=0xffffffff, block_pos=0, tx_pos=0):
        self.file_index = index  # tx 存储的 文件index
        self.block_pos = block_pos  # tx 存储所在的 block pos
        self.tx_pos = tx_pos  # tx 存储在文件中的偏移

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        f = wrap_to_StringIO(f)
        self.file_index = deser_uint(f)
        self.block_pos = deser_uint(f)
        self.tx_pos = deser_uint(f)
        return self

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        s = StringIO()
        s.write(ser_uint(self.file_index))
        s.write(ser_uint(self.block_pos))
        s.write(ser_uint(self.tx_pos))
        return s.getvalue()

    def set_null(self):
        self.file_index = 0xffffffff
        self.block_pos = 0
        self.tx_pos = 0

    def is_null(self):
        return self.file_index == 0xffffffff

    def __eq__(self, other):
        return self.file_index == other.file_index and \
               self.block_pos == other.block_pos and \
               self.tx_pos == other.tx_pos

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        if self.is_null():
            return "(null)"
        return "(nFile=%d, nBlockPos=%d, nTxPos=%d)" % self.file_index, self.block_pos, self.tx_pos


class PyTxIndex(Serializable):
    # 对于 txindex 的存取必须通过 对应的 tx 的hash 作为键， txindex不提供hash， 只有tx提供hash
    def __init__(self, txpos_in=None, noutputs=0):
        if txpos_in is not None and noutputs == 0:
            raise RuntimeError("PyTxIndex init error, when PyDiskTxPos is not None, outputs must not 0")
        self.txpos = txpos_in  # PyDiskTxPos  # 记录当前这个交易在硬盘上的位置(fileindex, blockpos, txpos)
        self.l_spend = list()  # vector<PyDiskTxPos>  # 记录这个交易被花费(output)到那些交易上
        if noutputs != 0:
            for i in range(noutputs):
                self.l_spend.append(PyDiskTxPos())
        pass

    def set_null(self):
        self.txpos = None
        self.l_spend = list()

    def is_null(self):
        return self.txpos.is_null()

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        f = wrap_to_StringIO(f)
        if not (nType & SerType.SER_GETHASH):
            nVersion = deser_uint(f)
        self.l_spend = deser_list(f, PyDiskTxPos)
        txpos = PyDiskTxPos()
        txpos.deserialize(f)
        self.txpos = txpos
        return self

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        s = StringIO()
        if not (nType & SerType.SER_GETHASH):
            s.write(ser_int(nVersion))
        s.write(ser_list(self.l_spend))
        s.write(self.txpos.serialize())
        return s.getvalue()

    def __eq__(self, other):
        if self.txpos != other.tx_pos or len(self.l_spend) != len(other.l_spend):
            return False
        # for f,s in zip(self.l_spend, other.l_spend):
        #     if f != s:
        #         return False
        # return True
        return self.l_spend == other.l_spend

    def __ne__(self, other):
        return not self.__eq__(other)

    pass


class PyTransaction(Serializable):
    def __init__(self, tx=None):
        if tx is not None:
            self.init(tx)
            return
        self.version = 1
        self.l_in = list()
        self.l_out = list()
        self.lock_time = 0  # source code is int not uint

        # used at runtime
        self.sha256 = None
        self.nFeesPaid = 0
        self.dFeePerKB = None
        self.dPriority = None
        self.ser_size = 0
        pass

    def init(self, py_tx):
        assert isinstance(py_tx, PyTransaction), "param must be PyTransaction class"
        self.version = py_tx.version
        self.l_in = py_tx.l_in
        self.l_out = py_tx.l_out
        self.lock_time = py_tx.lock_time
        # used at runtime
        self.sha256 = py_tx.sha256
        self.nFeesPaid = py_tx.nFeesPaid
        self.dFeePerKB = py_tx.dFeePerKB
        self.dPriority = py_tx.dPriority
        self.ser_size = py_tx.ser_size

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        f = wrap_to_StringIO(f)
        self.version = deser_int(f)
        self.l_in = deser_list(f, PyTxIn)
        self.l_out = deser_list(f, PyTxOut)
        self.lock_time = deser_uint(f)  # source code is int not uint
        return self

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        s = StringIO()
        # s.write(struct.pack(b"<i", self.version))
        s.write(ser_int(self.version))
        s.write(ser_list(self.l_in))
        s.write(ser_list(self.l_out))
        s.write(ser_uint(self.lock_time))
        ret = s.getvalue()
        self.ser_size = len(ret)
        return ret

    def set_null(self):
        self.version = 1
        self.l_in = list()
        self.l_out = list()
        self.lock_time = 0

    def is_null(self):
        return len(self.l_in) == 0 and len(self.l_out) == 0

    def __deepcopy__(self, memodict={}):
        new_tx = PyTransaction()
        new_tx.version = self.version
        new_tx.lock_time = self.lock_time
        new_tx.l_in = deepcopy(self.l_in)
        new_tx.l_out = deepcopy(self.l_out)
        return new_tx

    def calc_sha256(self):
        if self.sha256 is None:
            self.sha256 = cryptoutil.Hash(self.serialize())
        return self.sha256

    def get_hash(self, out_type=None):
        s = PyTransaction.serialize(self, SerType.SER_GETHASH, nVersion=cfg.VERSION)
        return cryptoutil.Hash(s, out_type=out_type)

    def is_final(self, block_time=0):
        """
        判定该tx是否在打包成block的时间的前面，如果大于区块时间，则这个tx目前没有完成\n
        https://github.com/bitcoin/bitcoin/blob/0.9/src/main.cpp#L515 \n
        :return:
        """
        # Time based nLockTime implemented in 0.1.6,
        # do not use time based until most 0.1.5 nodes have upgraded.
        if self.lock_time == 0:  # or self.lock_time < ctx.bestHeight:
            return True
        if block_time == 0:
            block_time = timeutil.get_adjusted_time()
        if self.lock_time < block_time:  # fix in v0.1.6
            return True
        for txin in self.l_in:
            if not txin.is_final():  # txin 的 isfinal是判定seq 是否是uint_max
                return False
        return True

    def is_newer_than(self, old_tx):
        """
        比较 oldtx 和本 tx 的新旧情况, 是由txin的seq决定的，而且是由所有txin的seq中最小的决定\n
        最小的seq在 本身，就是False, 最小的deq在old_tx，那么就是True (表明该交易更新) \n
        :param old_tx:
        :return:
        """
        assert isinstance(old_tx, PyTransaction), "param must be a TX"
        # 先比较 input 的数量是否相同
        if len(self.l_in) != len(old_tx.l_in):
            return False
        # 然后比较两者的inpout 的 pre 是否相同
        # for i in range(len(self.l_in)):
        #     if self.l_in[i].prev_out != old_tx.l_in[i].prev_out:
        #         return False
        tx_inputs = zip(self.l_in, old_tx.l_in)
        for first, second in tx_inputs:
            if first.prev_out != second.prev_out:  # 比较的两个txin 应该是相同的
                return False
        newer = False
        lowest = 0xFFFFFFFF
        # 遍历两者的input
        # for i in range(len(self.l_in)):
        #     if self.l_in[i].sequence != old_tx.l_in[i].sequence:
        #         if self.l_in[i].sequence < lowest:
        #             newer = False
        #             lowest = self.l_in[i].sequence
        #         if old_tx.l_in[i].sequence < lowest:
        #             newer = True
        #             lowest = old_tx.l_in[i].sequence
        for first, second in tx_inputs:
            # 两边的input顺序比较seq, 找出最小的seq, 然后最小的seq在本身就是False, 在后者就是True
            if first.sequence != second.sequence:
                if first.sequence < lowest:
                    newer = False
                    lowest = first.sequence
                if second.sequence < lowest:
                    newer = True
                    lowest = second.sequence
        return newer

    def is_coinbase(self):
        # 输入只有1个并且输入的输入是个空，那么就是每个区块的第一个交易(创造货币)
        return len(self.l_in) == 1 and self.l_in[0].prev_out.is_null()

    def check_transaction(self):
        """
        检查交易的基本合法性，注意只是检查in&out的数量，对于coinbase检查脚本长度\n
        其他交易检查 prev_out:PyOutPoint 是否有效 \n
        不检查 script 是否合理，不检查 in/out/fee 是否有效\n
        :return True & False \n
        :rtype bool
        """
        # Basic checks that don't depend on any context
        if len(self.l_in) == 0 or len(self.l_out) == 0:
            # TODO add log to log error info
            print "error! PyTransaction.check_transaction l_in or l_out is empty!"
            return False
        # Check for negative values
        for tout in self.l_out:
            if tout.value < 0:
                print "error! PyTransaction.check_transaction tx_out.value negative!"
                return False

        # return self.is_valid()
        if self.is_coinbase():  # 对于coibase的 sigscript 只能在 2-100B之间
            script_size = len(self.l_in[0].script_sig)
            if script_size < 2 or script_size > 100:
                print ("error! PyTransaction.CheckTransaction() : coinbase script size")
                return False
        else:
            for txin in self.l_in:
                if txin.prev_out.is_null():  # prev_out:PyOutPoin PyoutPoin记载了txin的关键信息，不是是null
                    print ("CTransaction::CheckTransaction() : prevout is null")
                    return False
        return True

    # def is_valid(self):
    #     self.calc_sha256()
    #     if not self.is_coinbase():
    #         for tin in self.l_in:
    #             if not tin.is_valid():
    #                 return False
    #     for tout in self.l_out:
    #         if not tout.is_valid():
    #             return False
    #     return True

    def is_mine(self):
        """
        表明该tx的out是否指向自己，用于判断是否加入wallet\n
        :return: 如果 tx 的 out 是指向我的，就返回True,否则False
         :rtype bool
        """
        for tout in self.l_out:
            if tout.is_mine():
                return True
        return False

    def get_debit(self):
        debit = 0
        for txin in self.l_in:
            debit += txin.get_debit()
        return debit

    def get_credit(self):
        """
        得到这笔tx中指向自己地址的out的value的累计，就是这个交易打向自己的coin数目\n
        :return:
        """
        credit = 0
        for txout in self.l_out:
            credit += txout.get_credit()
        return credit

    # 注意这里要是 value 是负数会抛异常
    def get_value_out(self):
        """
        本交易的所有out的value的和
        :return:
        """
        value_out = 0
        for txout in self.l_out:
            if txout.value < 0:
                raise RuntimeError("PyTransaction.get_value_out() : the tx_out.value is negatived")
            value_out += txout.value
        return value_out

    def get_min_fee(self, discount=False):
        """
        根据该Tx序列化的大小来获取应付的最小交易费，如果设置了discount 那么在10000以下不用付交易费
        :param discount:
        :return:
        """
        self.serialize()
        nbytes = self.ser_size
        if discount and nbytes < cfg.DISCOUNT_FOR_FEE_SIZE:
            return 0
        return (1 + nbytes / 1000) * cfg.CENT

    def read_from_disk(self, disk_tx_pos, release_file=False):
        """

        :param disk_tx_pos:
        :param release_file:
        :return: 返回False 或 True, 如果 f 不是 None 会返回(True, file)
        :rtype bool | tuple
        """
        filein = util.open_block_file(disk_tx_pos.file_index, 0, "rb+" if release_file else "rb")
        if filein is None:
            # TODO add log
            print "PyTransaction::ReadFromDisk() : OpenBlockFile failed"
            return False
        # Read transaction
        filein.seek(disk_tx_pos.tx_pos, 0)
        self.deserialize(filein)

        # return file pointer
        if release_file is not None:
            filein.seek(disk_tx_pos.tx_pos, 0)
            return True, filein.release_file()
        filein.close()
        return True

    def disconnect_inputs(self, txdb):
        """
        检查当前Tx的所有in，把他们对于该Tx的out全部恢复为 Unspent 状态，并把当前的Tx的索引index从disk上删除\n
        注意这个函数并不删除tx在硬盘上的存储，只是删除索引
        :param txdb: PyTxDB
        :return:
        """
        # Relinquish previous transactions' spent pointers
        if not self.is_coinbase():
            for txin in self.l_in:
                prev_out = txin.prev_out
                # prev_txindex = PyTxIndex()
                # 根据该tx的hash从硬盘上读取出这个 tx 对应的 TxIndex 信息
                prev_txindex = txdb.read_txindex(prev_out.hash_tx)
                if prev_txindex is None:
                    # TODO add log
                    print ("DisconnectInputs() : ReadTxIndex failed")
                    return False

                if prev_out.index >= len(prev_txindex.l_spend):
                    print ("DisconnectInputs() : prevout.index out of range")
                    return False
                # Mark outpoint as not spent
                prev_txindex.l_spend[prev_out.index].set_null()  # 这句就是把该交易的 spend 全部置为了空，代表这笔交易没有被花过
                # Write back
                txdb.update_txindex(prev_out.hash_tx, prev_txindex)
        # Remove transaction from index
        if not txdb.erase_txindex(self):
            print ("DisconnectInputs() : EraseTxPos failed")
            return False
        return True

    def connect_inputs(self, txdb, test_pool, this_txpos, height, f_block, f_miner, min_fee=0):
        """
        把当前的Tx进行验证 所有的in, 如果成功了，那么就修改in对应的Tx的out,并将当前的tx存储下来\n
        如果f_block 和 f_miner 都为 False, 则可以用来检查这个 tx 的合法性(包含 script & value & fee)\n
        :param txdb: # 存储
        :type txdb: PyTxDB
        :param test_pool: 对应 f_miner 有用，是miner的内存缓存
        :type test_pool: dict
        :param this_txpos: 这笔交易对应在disk上的位置 PyDiskTxPos
        :type this_txpos: PyDiskTxPos
        :param height:
        :type height: int
        :param f_block: f_block 找txindex时，只查找TxDB，只写入 TxDB，与f_miner不能同时为True，否则以f_miner为首,同为False不会对存储产生任何影响
        :type f_block: bool
        :param f_miner: f_miner 找txindex时，首先查test_pool，找不到会查TxDB, 只写入 test_pool
        :type f_miner: bool
        :param min_fee: 最小交易费，若该交易的交易费最后小于该值，会返回 None
        :type min_fee: int
        :return: None 或者 fee 因为 fee 可能为 0 所以不能用 not 来判断是否 connect 是否成功
        :rtype None | int
        """
        # Take over previous transactions' spent pointers
        fees = 0
        if not self.is_coinbase():
            value_in = 0  # 这个值是记录这个 tx 将要链接的所有in对应的tx的out到本tx的value的和，就是这个交易所有的in和

            for i in range(len(self.l_in)):
                prev_out = self.l_in[i].prev_out  # 这个tx想要链接的 prev tx
                # 首先根据想要找的prev_out 找到这个 prev 对应的 txindex
                # Read txindex
                # prev_txindex = PyTxIndex()  # init 的空白
                found = True
                # 是miner的时候从test_pool找，没找到或者非miner从 txdb 中找
                if f_miner and (prev_out.hash_tx in test_pool):
                    # Get txindex from current proposed changes
                    prev_txindex = test_pool.get(prev_out.hash_tx, PyTxIndex())
                else:  # 非 miner 或者没在 testpool中找到
                    # 如果从存储中找到了该TxIn,那么就是True,否则就是False
                    prev_txindex = txdb.read_txindex(prev_out.hash_tx)
                    if prev_txindex:
                        found = True
                    else:
                        found = False
                        prev_txindex = PyTxIndex()

                # 如果没有找到，并且 是 f_block 或者是 f_miner，会在这里返回
                if not found and (f_block or f_miner):
                    # TODO add log and combine
                    if f_miner:  # 是miner正常返回None
                        return None
                    else:  # 是 block 记录错误后返回None
                        print ("ConnectInputs() : %s prev tx %s index entry not found" %
                               (self.get_hash(out_type='hex')[:6], hexser_uint256(prev_out.hash_tx)))
                        return None

                # 在查找过 txindex 现在查找txindex对应的 Tx
                # Read txPrev
                tx_prev = PyTransaction()
                # 没找到txindex或者找到的这个 txindex 的txpos 是 1，1，1(PyDiskTxPos(1,1,1)似乎是一个标记)
                if not found or prev_txindex.txpos == PyDiskTxPos(1, 1, 1):
                    # Get prev tx from single transactions in memory
                    with ctx.dictTransactionsLock:
                        tx_prev = ctx.dictTransactions.get(prev_out.hash_tx, None)
                        # 从内存缓存中没有找到 prev_tx
                        if tx_prev is None:
                            print ("ConnectInputs() : %s mapTransactions prev not found %s" %
                                   (self.get_hash(out_type='hex')[:6], hexser_uint256(prev_out.hash_tx)))
                            return None
                    if not found:  # 那么此时的 prev_txindex是个空白
                        # 那么就把 prev_txindex 的 out 扩大到找到的 prev_tx 的out 的大小
                        [prev_txindex.l_spend.append(PyDiskTxPos()) for _ in range(len(tx_prev.l_out))]
                else:  # 这个是找到 prev_index 的情况，那么就从本地读取出对应的 tx
                    # Get prev tx from disk
                    if not tx_prev.read_from_disk(prev_txindex.txpos):
                        print ("ConnectInputs() : %s ReadFromDisk prev tx %s failed" %
                               (self.get_hash(out_type='hex')[:6], hexser_uint256(prev_out.hash_tx)))
                        return None

                if prev_out.index >= len(tx_prev.l_out) or prev_out.index >= len(prev_txindex.l_spend):
                    print ("ConnectInputs() : %s prevout.index out of range %d %d %d" %
                           (self.get_hash(out_type='hex')[:6], prev_out.index, len(tx_prev.l_out),
                            len(prev_txindex.l_spend)))
                    return None

                # If prev is coinbase, check that it's matured  # 因为规定是对于coinbase必须等到n个块才行
                if tx_prev.is_coinbase():
                    pindex = ctx.indexBest
                    while True:
                        # 注意这里并不会是找到这个tx所在的区块，而是从当前的区块向前找，看tx在不在一定范围内的区块中
                        if pindex is None or (ctx.bestHeight - pindex.height) >= cfg.COINBASE_MATURITY - 1:
                            break
                        # 找到了就返回表示不满足 coinbase的成熟度
                        if pindex.block_pos == prev_txindex.txpos.block_pos and \
                                        pindex.file_index == prev_txindex.txpos.file_index:
                            print ("ConnectInputs() : tried to spend coinbase at depth %d" %
                                   (ctx.bestHeight - pindex.height))
                            return None
                        pindex = pindex.prev_index
                        # while end
                        pass

                # Verify signature
                if not verify_signature(tx_prev, self, i):
                    print ("ConnectInputs() : %s VerifySignature failed" %
                           self.get_hash(out_type='hex')[:6])
                    return None

                # Check for conflicts
                if not prev_txindex.l_spend[prev_out.index].is_null():  # 这里表明这个tx是已经被花费过的
                    if f_miner:
                        return None
                    else:
                        print ("ConnectInputs() : %s prev tx already used at %s" %
                               (self.get_hash(out_type='hex')[:6], str(prev_txindex.l_spend[prev_out.index])))
                        return None

                # Mark outpoints as spent
                prev_txindex.l_spend[prev_out.index] = this_txpos

                # write back
                if f_block:
                    txdb.update_txindex(prev_out.hash_tx, prev_txindex)
                elif f_miner:
                    test_pool[prev_out.hash_tx] = prev_txindex
                value_in += tx_prev.l_out[prev_out.index].value  # PyTxOut.value
                # for end
                pass

            # Tally transaction fees  #value_in 是所有in的和，getvalueout是所有out的和
            tx_fee = value_in - self.get_value_out()  # 注意这里会抛异常  # TODO 注意异常什么时候被处理
            if tx_fee < 0:
                print ("ConnectInputs() : %s nTxFee < 0" % self.get_hash(out_type='hex')[:6])
                return None
            if tx_fee < min_fee:
                return None
            fees += tx_fee
            # if end
            pass
        if f_block:
            # Add transaction to disk index
            txdb.add_txindex(self, this_txpos, height)
        elif f_miner:
            # Add transaction to test pool
            test_pool[self.get_hash()] = PyTxIndex(PyDiskTxPos(1, 1, 1), len(self.l_out))

        return fees

    def client_connect_inputs(self):
        """
        只是检查当前的Tx是否合法(sign && in/out value)，并不会进行存储活动，相当于connect_input f_miner f_block都为false
        但是 该函数查找的是 mapTransactions
        :return:
        """
        if self.is_coinbase():
            return False

        # Take over previous transactions' spent pointers
        with ctx.dictTransactionsLock:
            value_in = 0
            for i in range(len(self.l_in)):
                # Get prev tx from single transactions in memory
                prev_out = self.l_in[i].prev_out
                tx_prev = ctx.dictTransactions.get(prev_out.hash_tx)
                if tx_prev is None:
                    return False
                if prev_out.index >= len(tx_prev.l_out):
                    return False

                # Verify signature
                if not verify_signature(tx_prev, self, i):
                    print ("ConnectInputs() : VerifySignature failed")
                    return False

                value_in += tx_prev.l_out[prev_out.index].value

            if self.get_value_out() > value_in:
                return False

        return True

    def accept_transaction(self, txdb=None, check_inputs=True, missing_inputs=None):
        """
        判断是否接受本tx,如果成功,会加入到mapTransactions中,返回True,失败返回False\n
        chech_inputs为True时会检查本tx的合法性(包含script value fee)
        :param txdb:
        :type txdb: PyTxDB
        :param check_inputs:
        :type check_inputs: bool
        :param missing_inputs: None 或一个 list,如果为None,不产生任何作用,如果是一个list,会修改第0个元素为True & False
        :type missing_inputs: list | None
        :return:
        :rtype bool
        """
        if txdb is None:
            txdb = PyTxDB("r")
            need_close = True
        else:
            need_close = False
        if missing_inputs is not None and isinstance(missing_inputs, list) and len(missing_inputs) <= 1:
            if missing_inputs:
                missing_inputs[0] = False
            else:
                missing_inputs.append(False)
        else:
            missing_inputs = [False]
        # Coinbase is only valid in a block, not as a loose transaction
        if self.is_coinbase():
            print ("AcceptTransaction() : coinbase as individual tx")

        if not self.check_transaction():  # 注意这里只是基本的检查，不见
            print ("AcceptTransaction() : CheckTransaction failed")

        # Do we already have it?
        uint256_hash = self.get_hash()
        with ctx.dictTransactionsLock:
            # 这个交易已经存在缓存中了
            if uint256_hash in ctx.dictTransactions:
                if need_close:
                    txdb.close()
                return False
        if check_inputs:
            # 检查这个交易是否已经被存在disk中了
            if txdb.contains_tx(uint256_hash):
                if need_close:
                    txdb.close()
                return False

        # Check for conflicts with in-memory transactions
        tx_old = None
        # 这段逻辑很奇怪，下面这个循环只会执行 i=0的情况，有空查看以后的源码  # TODO 查看更高版本的实现 for accept_transaction
        for i in range(len(self.l_in)):
            outpoint = self.l_in[i].prev_out  # 这里 i 只会 == 1
            inpoint = ctx.dictNextTx.get(outpoint.gethash(), None)
            if inpoint is not None:
                # Allow replacing with a newer version of the same transaction
                if i != 0:
                    if need_close:
                        txdb.close()
                    return False  # ???
                tx_old = inpoint.py_tx  # 这里的py_tx就是 inpoint 在之前所持有的
                if not self.is_newer_than(tx_old):  # 判断当前的这个交易和缓存的哪个更新，只比较
                    if need_close:
                        txdb.close()
                    return False
                for txin in self.l_in:
                    outpoint = txin.prev_out
                    # 这里我觉得比hash就好了吧···,这里比较的应该是根据每个OutPoint从内存中map到了InPoint所持有tx是否相同
                    if (not (outpoint.gethash() in ctx.dictNextTx)) or \
                                    ctx.dictNextTx[outpoint.gethash()].py_tx != tx_old:
                        if need_close:
                            txdb.close()
                        return False
                    # end for
                    pass
                break
                # end if
        # end for
        pass

        # Check against previous transactions
        if check_inputs and \
                        self.connect_inputs(txdb, test_pool=dict(), this_txpos=PyDiskTxPos(1, 1, 1), height=0,
                                            f_block=False, f_miner=False) is None:  # 检查tx的合法性
            missing_inputs[0] = True

            print ("AcceptTransaction() : ConnectInputs failed %s" % hexser_uint256(uint256_hash)[:6])
            if need_close:
                txdb.close()
            return False

        # Store transaction in memory
        with ctx.dictTransactionsLock:
            if tx_old:
                print ("mapTransaction.erase(%s) replacing with new version" % tx_old.get_hash("hex"))
                ctx.dictTransactions.pop(tx_old.get_hash(), None)  # 删除老的本tx相同的tx

            self._add_to_memory_pool()

        # are we sure this is ok when loading transactions or restoring block txes
        # If updated, erase old tx from wallet
        if tx_old:
            erase_from_wallet(tx_old.get_hash())

        print ("AcceptTransaction(): accepted %s" % hexser_uint256(uint256_hash)[:6])
        if need_close:
            txdb.close()
        return True

    # protected
    def _add_to_memory_pool(self):
        with ctx.dictTransactionsLock:
            uint256_hash = self.get_hash()
            ctx.dictTransactions[uint256_hash] = self
            for i in range(len(self.l_in)):
                ctx.dictNextTx[self.l_in[i].prev_out.gethash()] = PyInPoint(self, i)
            ctx.transactionsUpdated += 1

        return True

    # public
    def remove_from_memory_pool(self):
        with ctx.dictTransactionsLock:
            for txin in self.l_in:
                ctx.dictNextTx.pop(txin.prev_out.gethash(), None)
            ctx.dictTransactions.pop(self.get_hash(), None)
            ctx.transactionsUpdated += 1

        return True

    def __str__(self):
        sio = StringIO()
        s = "PyTransaction(hash=%s, ver=%d, l_in.size=%d, l_out.size=%d, nLockTime=%d)\n" % \
            (self.get_hash('hex')[:6], self.version, len(self.l_in), len(self.l_out), self.lock_time)
        sio.write(s)
        for txin in self.l_in:
            s = ("  " + str(txin) + "\n")
            sio.write(s)
        for txout in self.l_out:
            s = ("  " + str(txout) + "\n")
            sio.write(s)
        return sio.getvalue()

    def __eq__(self, other):
        return self.version == other.version and \
               self.lock_time == other.lock_time and \
               self.l_in == other.l_in and \
               self.l_out == other.l_out

    def __ne__(self, other):
        return not self.__eq__(other)

    pass


# db
#
# A txdb record that contains the disk location of a transaction and the
# locations of transactions that spend its outputs.  vSpent is really only
# used as a flag, but having the location is very helpful for debugging.
#
class PyTxDB(db.PyDB):
    DBKEY_BLOCKINDEX = u"blockindex"

    def __init__(self, szmode="r+", f_txn=False):
        super(PyTxDB, self).__init__("blkindex.dat" if not ctx.fClient else None, szmode, f_txn)
        if self.first_init:
            self.write_blockindex_placeholder()

    def __check_client(self):
        assert not ctx.fClient, "client can't use this class!"

    def read_txindex(self, uint256_hash):
        """

        :param uint256_hash:
        :return:
        :rtype PyTxIndex
        """
        self.__check_client()
        return self._read(("tx", uint256_hash), PyTxIndex)  # get value

    def update_txindex(self, uint256_hash, txindex):
        self.__check_client()
        if txindex is None or txindex.is_null():
            return None
        self._write(("tx", uint256_hash), txindex)

    def add_txindex(self, tx, txpos, height):
        self.__check_client()
        tx_hash = tx.get_hash()
        txindex = PyTxIndex(txpos, len(tx.l_out))
        self._write(("tx", tx_hash), txindex)

    def erase_txindex(self, tx):  # 参数是tx, 因为只有 tx 才能提供 hash(key)
        self.__check_client()
        tx_hash = tx.get_hash()
        return self._erase(("tx", tx_hash))

    def contains_tx(self, tx_hash):
        self.__check_client()
        return self._exists(("tx", tx_hash))

    def read_owner_txes(self, uint256_hash, min_height):
        self.__check_client()
        cursor = self._get_cursor()
        if cursor is None:
            return False
        flags = self.DB_SET_RANGE
        # TODO "not impl yet for don't know for cursor and this func is not used in source code"
        raise NotImplementedError(
            "not impl yet for don't know how to use cursor and this func is not used in source code")

    # var is hash or PyOutPoint
    def read_disk_tx(self, var, txret):
        self.__check_client()
        if type(var) is PyOutPoint:
            uint156_hash = var.hash_tx
        elif isinstance(var, int) or isinstance(var, long) or isinstance(var, str) or isinstance(var, bytearray):
            uint156_hash = var
        else:
            raise RuntimeError("var must be hash256 or PyOutPoint")

        txindex = self.read_txindex(uint156_hash)
        if txindex is None:
            return None
        # tx 不从数据库读，从文件中读取
        return txret.read_from_disk(txindex.txpos)

    def write_blockindex_placeholder(self):
        self._write(("blockindex", 0), 'placeholder')

    def write_blockindex(self, block_index):
        """

        :param block_index: Block.PyDiskBlockIndex
        :return: None
        :rtype None
        """
        self._write(("blockindex", block_index.get_block_hash()), block_index)

    def erase_blockindex(self, block_hash):
        return self._erase(("blockindex", block_hash))

    def read_hash_best_chain(self):  # uint256
        ret = self._read("hashBestChain")
        return ret  # 0 if ret is None else ret

    def write_hash_best_chain(self, bestchain_hash):
        return self._write("hashBestChain", bestchain_hash)


# db
class PyWalletDB(db.PyDB):
    DBKEY_NAME = "name"
    DBKEY_TX = "tx"
    DBKEY_KEY = "key"
    DBKEY_DEFAULTKEY = "defaultkey"
    DBKEY_SETTING = "setting"

    DBKEY_SETTING_GEN_COIN = "fGenerateCoins"
    DBKEY_SETTING_TX_FEE = "transactionFee"
    DBKEY_SETTING_ADDR = "addrIncoming"

    def __init__(self, szmode="r+", f_txn=False):
        super(PyWalletDB, self).__init__("wallet.dat", szmode, f_txn)

    def read_name(self, str_addr):
        return self._read((self.DBKEY_NAME, str_addr))

    def write_name(self, str_addr, str_name):
        ctx.dictAddressBook[str_addr] = str_name
        return self._write((self.DBKEY_NAME, str_addr), str_name)

    def erase_name(self, str_addr):
        if str_addr in ctx.dictAddressBook:
            ctx.dictAddressBook.pop(str_addr, None)
        return self._erase((self.DBKEY_NAME, str_addr))

    def read_tx(self, var_hash, cls):  # cls must be PyWalletTx
        return self._read((self.DBKEY_TX, var_hash), cls)

    def write_tx(self, var_hash, wtx):
        return self._write((self.DBKEY_TX, var_hash), wtx)

    def erase_tx(self, var_hash):
        return self._erase((self.DBKEY_TX, var_hash))

    def read_key(self, pubkey):
        return self._read((self.DBKEY_KEY, pubkey))

    def write_key(self, pubkey, prikey):
        return self._write((self.DBKEY_KEY, pubkey), prikey, False)

    def erase_key(self, pubkey):
        return self._erase((self.DBKEY_KEY, pubkey))

    def read_default_key(self):
        return self._read(self.DBKEY_DEFAULTKEY)

    def write_default_key(self, pubkey):
        return self._write(self.DBKEY_DEFAULTKEY, pubkey)

    def read_setting(self, strkey, cls=None):
        ret = self._read((self.DBKEY_SETTING, strkey))
        if ret is None:
            return None
        if cls is not None:
            ins = cls()
            ins.deserialize(ret, SerType.SER_DISK)
            return ins
        return ret

    def write_setting(self, strkey, value):
        if isinstance(value, Serializable):
            value = value.serialize(SerType.SER_DISK)
        return self._write((self.DBKEY_SETTING, strkey), value)

    pass


def erase_from_wallet(uint256_hash):
    with ctx.dictWalletLock:
        ctx.dictWallet.pop(uint256_hash, None)
        with PyWalletDB("w") as walletdb:
            walletdb.erase_tx(uint256_hash)

    pass


def main():
    pass


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import context as ctx
from app.net import net, action as netaction
from app.base import bignum as BN, ui
from app.base.serialize import *
from app.block.tx import tx as Tx
from app.block.utils import util
from app.block.utils.cryptoutil import Hash, Hash160
from app.block.utils.typeutil import *
from app.config import VERSION, MAX_SIZE
from app.utils import timeutil
from app.utils.baseutil import class_params_check


class PyBlock(Serializable):
    def __init__(self):
        # header
        self.version = 1  # int
        # self.type = 0
        # uint256 hashPrevBlock;
        self.hash_prev_block = 0  # 上一个区块的hash uint256
        # uint256 hashMerkleRoot;
        self.hash_merkle_root = 0  # 当前区块的merkleroot hash uint256
        self.time = 0  # uint
        self.bits = 0  # 难度 uint
        self.nonce = 0  # 工作量 uint
        # network and disk
        self.l_tx = list()  # vector<CTransaction> vtx;
        # memory only  就是不进行序列化
        self.l_merkle_tree = list()

    def deserialize(self, f, nType=0, nVersion=VERSION):
        f = wrap_to_StringIO(f)
        self.version = deser_int(f)
        self.hash_prev_block = deser_uint256(f)
        self.hash_merkle_root = deser_uint256(f)
        self.time = deser_uint(f)
        self.bits = deser_uint(f)
        self.nonce = deser_uint(f)
        if not (nType & (SerType.SER_GETHASH | SerType.SER_BLOCKHEADERONLY)):
            self.l_tx = deser_list(f, Tx.PyTransaction, nType=nType, nVersion=nVersion)
        else:
            self.l_tx = list()
        return self

    def serialize(self, nType=0, nVersion=VERSION, header=False):
        s = StringIO()
        s.write(ser_int(self.version))
        s.write(ser_uint256(self.hash_prev_block))
        s.write(ser_uint256(self.hash_merkle_root))
        s.write(ser_uint(self.time))
        s.write(ser_uint(self.bits))
        s.write(ser_uint(self.nonce))
        if header:
            return s.getvalue()
        if not (nType & (SerType.SER_GETHASH | SerType.SER_BLOCKHEADERONLY)):
            s.write(ser_list(self.l_tx, cls=Tx.PyTransaction, nType=nType, nVersion=nVersion))
        return s.getvalue()

    def set_null(self):
        self.version = 1
        self.hash_prev_block = 0  # 上一个区块的hash
        self.hash_merkle_root = 0  # 当前区块的hash
        self.time = 0
        self.bits = 0
        self.nonce = 0  # 工作量
        self.l_tx = list()
        self.l_merkle_tree = list()

    def is_null(self):
        return self.bits == 0

    def get_hash(self, output_type=None):
        return Hash(self.serialize(header=True), out_type=output_type)

    def build_merkle_tree(self):  # return uint256
        # 获得tx的hash的列表
        self.l_merkle_tree = map(lambda tx: tx.get_hash(out_type='str'), self.l_tx)
        size = len(self.l_tx)
        j = 0
        while True:
            if size <= 1:
                break
            for i in range(0, size, 2):
                i2 = min(i + 1, size - 1)
                self.l_merkle_tree.append(Hash(self.l_merkle_tree[j + i],
                                               self.l_merkle_tree[j + i2], out_type='str'))
                pass
            j += size
            size = (size + 1) / 2
        return deser_uint256(self.l_merkle_tree[-1]) if self.l_merkle_tree else 0

    def get_merkle_branch(self, index):
        # 注意这里并不是拿到index指向的交易的分支线，而是拿到指向分支线用于检验的每个node的对偶节点
        if not self.l_merkle_tree:
            self.build_merkle_tree()

        l_merkle_branch = list()
        j = 0  # j 偏移(每一层)
        size = len(self.l_tx)
        while True:
            if size <= 1:
                break
            # index 是该tx在block的位置，index ^ 1 当index是奇数时-1，偶数时+1
            i = min(index ^ 1, size - 1)  # 这里异或1就是为了拿到对偶节点，和check_merkle_branch的 & 对应
            l_merkle_branch.append(deser_uint256(self.l_merkle_tree[j + i]))
            index >>= 1
            j += size
            size = (size + 1) / 2
            pass
        return l_merkle_branch

    @staticmethod
    def check_merkle_branch(tx_hash, l_merkle_branch, index, out_type=None):
        if not isinstance(tx_hash, str):
            tx_hash = ser_uint256(tx_hash)

        if index == -1:
            return 0
        for otherside in l_merkle_branch:
            if index & 1:
                tx_hash = Hash(ser_uint256(otherside), tx_hash, out_type='str')
            else:
                tx_hash = Hash(tx_hash, ser_uint256(otherside), out_type='str')
            index >>= 1
        # tx_hash256 现在就是 root hash
        if out_type == 'str':
            return tx_hash
        elif out_type == 'hex':
            return hexser_uint256(tx_hash, in_type='str')
        return deser_uint256(tx_hash)  # return number format

    def write_to_disk(self, write_txs):
        """
        将当前块写入disk, write_txs 表示写入块的同时是否也同时写入这个块所持有的tx\n
        如果是客户端不需要写入，如果是挖矿者，需要写入\n
        :param write_txs:
        :return: None 表示失败，成功会返回 (file_index, block_pos)
        """
        ret = util.append_block_file()
        if ret is None:
            print ("PyBlock::WriteToDisk() : AppendBlockFile failed")
            return None
        f = ret[0]
        file_index = ret[1]
        if not write_txs:  # 不写入 tx,只写入头部
            f.nType |= SerType.SER_BLOCKHEADERONLY

        # Write index header
        size = f.get_serialize_size(self.serialize(f.nType, f.nVersion))
        f.stream_in(PyFlatData(cfg.MESSAGE_START))
        f.stream_in(size, 'uint')

        block_pos = f.tell()
        f.stream_in(self)
        return file_index, block_pos

    def read_from_disk(self, index, block_pos=0, read_txs=False):
        """

        :param index:   file_index 或者是 PyBlockIndex,当为PyBlockIndex时候 block_pos 没有作用
        :type index: PyBlockIndex | int
        :param block_pos:   只有当index 是 file_index(int)的时候才会起作用，和file_index成对指向文件上的位置
        :type block_pos: int
        :param read_txs:
        :type read_txs: bool  标识只读头部还是把所有的tx都读取出来
        :return:
        :rtype bool
        """
        if isinstance(index, PyBlockIndex):
            block_pos = index.block_pos
            index = index.file_index

        self.set_null()
        # Open history file to read
        filein = util.open_block_file(index, block_pos, "rb")
        if not filein:
            print "PyBlock::ReadFromDisk() : OpenBlockFile failed"
            return False
        if not read_txs:
            filein.nType |= SerType.SER_BLOCKHEADERONLY

        self.deserialize(filein, filein.nType, filein.nVersion)
        filein.close()
        return True

    def __str__(self):
        sio = StringIO()
        s = 'PyBlock(hash=%s, ver=%d, hashPrevBlock=%s, hashMerkleRoot=%s, nTime=%u, nBits=%08x, nNonce=%u, vtx=%d)\n' \
            % (self.get_hash(output_type="hex")[0:14], self.version, hexser_uint256(self.hash_prev_block)[0:14],
               hexser_uint256(self.hash_merkle_root), self.time, self.bits, self.nonce, len(self.l_tx))
        sio.write(s)
        for tx in self.l_tx:
            sio.write("  ")
            s = str(tx)
            sio.write(s)

        s = "\n merkle tree:"
        sio.write(s)
        for mt in self.l_merkle_tree:
            s = "%s  " % hexser_uint256(mt, 'str')[: 6]
            sio.write(s)
        s = "\n"
        sio.write(s)
        return sio.getvalue()

    def get_block_value(self, fees):
        """

        :param fees:
        :return:
        """
        subsidy = cfg.BLOCK_SUBSIDY * cfg.COIN  # 这里就是著名的每个块送50个Btc
        # Subsidy is cut in half every 4 years
        subsidy >>= (ctx.bestHeight / cfg.HALVE_BLOCK_NUM)  # 210000是大约4年的区块数目，/ 是向下取整
        return subsidy + fees

    def disconnect_block(self, txdb, block_index):
        """
        disconnectblock 并不是删除在本地存储的区块，而是删除这个区块持有的tx的索引 txindex\n
        以及修改上一个区块的 next 信息，注意这里没有更改 mapBlockIndex
        :param txdb:
        :param block_index:
        :return:
        """
        # Disconnect in reverse order
        for tx in reversed(self.l_tx):
            if not tx.disconnect_inputs(txdb):
                return False

        # Update block index on disk without changing it in memory.
        # The memory index structure will be changed after the db commits.   TODO 发现这个修改memory的地方
        prev_index = block_index.prev_index
        if prev_index:
            index = PyDiskBlockIndex(prev_index)
            index.hash_next = 0
            txdb.write_blockindex(index)
        return True

    def connect_block(self, txdb, block_index):
        #  issue here: it doesn't know the version
        txpos = block_index.block_pos + (PyBlock().serialize_size(SerType.SER_DISK) - 1) \
                + GetSizeOfCompactSize(len(self.l_tx))

        dict_unused = dict()
        fees = 0
        for tx in self.l_tx:
            this_txpos = Tx.PyDiskTxPos(block_index.file_index, block_index.block_pos, txpos)
            txpos += tx.serialize_size(SerType.SER_DISK)

            ret = tx.connect_inputs(txdb, dict_unused, this_txpos, block_index.height, True, False)
            if ret is None:
                return False
            fees += ret  # 每个tx的 手续费
        # l_tx[0] 是创立区块的 coinbase tx ,这里是其他节点是否接受这个区块的检验(防止有人对初创交易作假)
        if self.l_tx[0].get_value_out() > self.get_block_value(fees):
            return False
        # 到这步表示这个块的有效性检验通过了，可以存起来
        # Update block index on disk without changing it in memory.
        # The memory index structure will be changed after the db commits.
        if block_index.prev_index:
            blockindex_prev = PyDiskBlockIndex(block_index.prev_index)
            blockindex_prev.hash_next = block_index.get_block_hash()
            txdb.write_blockindex(blockindex_prev)  # 这是是update 表示接受了区块后把本地的上一个区块指向改成这个块

        # Watch for transactions paying to me
        for tx in self.l_tx:  # 检查本tx关联的tx是否有out是指向自己的，是有加入wallet
            add_to_wallet_if_mine(tx, self)
        return True

    def add_to_blockindex(self, file_index, block_pos):
        """
        file_index和block_pos 是一个已经存储在本地但是还未建立索引的区块\n
        这个新的block块已经被验证是合法的并已经被保存到了本地，这里是需要验证\n
        其是否符合链接到上一个块，也就是是否应该在本地建立对于这个块的索引index \n
        :param file_index: 新区块的 file_index
        :param block_pos:  新区块的 block_pos
        :return: True 表示添加block index 成功，False表示失败
        :rtype bool
        """
        block_hash = self.get_hash()
        if block_hash in ctx.dictBlockIndex:
            print ("AddToBlockIndex() : %s already exists" % hexser_uint256(block_hash)[:14])
            return False
        # Construct new block index object
        index_new = PyBlockIndex(file_index, block_pos, self)  # index_new 是本地区块的索引
        index_new.hash_block = block_hash  # 其实不是很明白为什么不在传入Block的时候就构造hash_block
        ctx.dictBlockIndex[block_hash] = index_new  # 实际上对 mapBlockIndex 的修改只有这里
        # 也就是说 mapBlockIndex会存储所有已经存在硬盘上的block所构造的index，
        # 但是不保证这个index的有效性，这个index会缺少 next 信息，孤立块还会缺少 height 和 prev_index 信息

        # 这里是很精妙的，因为要是是收到更超前的块或者是已分叉很多的(出现博弈)，
        # 会因为找不到hash而跳过这步，而在下面的判断heigh的地方直接跳过不保存这个块的index,但是block块却是已经存在的
        # 当之后重组织以后如果之前存下来但是没建立index的区块又是合法的了，那么这里就可以又重新建立block的索引
        # 如果是同一个前置块的 区块，那么这个区块就是同时产生的不同块，他们的高度是相等的
        index_prev = ctx.dictBlockIndex.get(self.hash_prev_block, None)
        if index_prev is not None:  # 跳过这个判断的话就是孤立块
            # 更新 index 的 prev 信息 和 height 信息
            index_new.prev_index = index_prev  # 注意这里只把当前的new的prev修改为 找到的prev,但是不修改prev的next为目前的new`
            index_new.height = index_prev.height + 1  # 总之这里严格遵守 下一个块的高度是前一个块+1，注意这里和bestchain没有任何关系

        txdb = Tx.PyTxDB(f_txn=True)
        txdb.txn_begin()  # 开启数据库事务
        txdb.write_blockindex(PyDiskBlockIndex(index_new))
        # new best
        if index_new.height > ctx.bestHeight:  # 这里相当关键，蕴含了bitcoin的哲学，涉及什么时候达到共识链
            if ctx.indexGenesisBlock is None and block_hash == ctx.hashGenesisBlock:  # 这个块是初创块
                # 我认为这是一条硬性规定，表示初创块必须是唯一的，硬编码进入了代码中 block_hash == ctx.hashGenesisBlock
                ctx.indexGenesisBlock = index_new
                txdb.write_hash_best_chain(block_hash)
            elif self.hash_prev_block == ctx.hashBestChain:
                # Adding to current best branch
                if not self.connect_block(txdb, index_new):  # 添加块失败
                    txdb.txn_abort()
                    txdb.close()
                    index_new.erase_block_from_disk()
                    ctx.dictBlockIndex.pop(index_new.get_block_hash(), None)  # equal to del but no exception
                    print ("AddToBlockIndex() : ConnectBlock failed")
                    return False
                txdb.write_hash_best_chain(block_hash)  # write best chain
                txdb.txn_commit()  # ?? 为什么这里要commit
                index_new.prev_index.next_index = index_new  # index_new.prev_index == 目前最末尾的块
                # Delete redundant memory transactions
                for tx in self.l_tx:
                    tx.remove_from_memory_pool()
            else:
                # New best branch
                if not reorganize(txdb, index_new):  # 这里会进行best chain 的重组
                    txdb.txn_abort()
                    txdb.close()
                    print ("AddToBlockIndex() : Reorganize failed")
                    return False

            # New best link
            ctx.hashBestChain = block_hash
            ctx.indexBest = index_new
            ctx.bestHeight = ctx.indexBest.height
            ctx.transactionsUpdated += 1
            # 从这里就修正了目前本地认可的 bestchain
            print ("AddToBlockIndex: new best=%s  height=%d" % (hexser_uint256(ctx.hashBestChain)[:14], ctx.bestHeight))

        txdb.txn_commit()
        txdb.close()

        # Relay wallet transactions that haven't gotten in yet
        if id(index_new) == id(ctx.indexBest):
            relay_wallet_transaction()
            pass

        ui.mainframe_repaint()
        return True

    def check_block(self):
        """
        检查本块的有效性\n
        1.会验证交易总数大小，序列化后的交易所占空间大小\n
        2.检查区块时间， 2小时之外的区块会被抛弃\n
        3.检查交易：第一笔交易必须是coinbase, 后面的交易都必须验证通过\n
        4.检查工作量是否满足要求\n
        5.检查 merkle tree 的 root hash 是否正确\n
        :return: True 表示 5条都满足，其中一旦出错就返回 False
        """
        # These are checks that are independent of context
        # that can be verified before saving an orphan block.
        # size limits
        if len(self.l_tx) == 0 or len(self.l_tx) > MAX_SIZE or len(self.serialize(nType=SerType.SER_DISK)) > MAX_SIZE:
            # TODO add log
            print "CheckBlock() : size limits failed"
            return False
        # check timestamp
        if self.time > timeutil.get_adjusted_time() + cfg.CHECK_BLOCK_TIME_EXPIRED_TIME:  # 2 * 60 * 60:
            print "CheckBlock() : block timestamp too far in the future"
            return False
        # First transaction must be coinbase, the rest must not be
        if not self.l_tx[0].is_coinbase():
            print "CheckBlock() : first tx is not coinbase"
            return False
        for i in range(1, len(self.l_tx)):
            if self.l_tx[i].is_coinbase():
                print "CheckBlock() : more than one coinbase for index %d" % i
                return False
        # check txs
        for i in range(1, len(self.l_tx)):
            if not self.l_tx[i].check_transaction():
                print "CheckBlock() : CheckTransaction failed for tx index:%d" % i
                return False
        # Check proof of work matches claimed amount
        # bits_uint256 = BN.uint256_from_compact(self.bits)
        compact = BN.PyBigNum.set_compact(self.bits)
        if compact > ctx.proofOfWorkLimit:
            # proofOfWorkLimit init is 00 FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
            print "CheckBlock() : nBits below minimum work"
            return False
        if self.get_hash() > compact.get_uint256():
            print "CheckBlock() : hash doesn't match nBits"
            return False

        if self.hash_merkle_root != self.build_merkle_tree():
            print "CheckBlock() : hashMerkleRoot mismatch"
            return False
        return True

    def accept_block(self):
        """

        :return:
        """
        # Check for duplicate
        block_hash = self.get_hash()
        if block_hash in ctx.dictBlockIndex:
            print "AcceptBlock() : block already in mapBlockIndex"
            return False

        # Get prev block index
        index_prev = ctx.dictBlockIndex.get(self.hash_prev_block, None)
        if index_prev is None:
            "AcceptBlock() : prev block not found"
            return False
        pass

        # Check timestamp against prev
        if self.time <= index_prev.get_median_time_past():  # 当前的时间要大于向前数5个块的块时间
            print ("AcceptBlock() : block's timestamp is too early")
            return False

        # Check proof of work
        if self.bits != get_next_work_required(index_prev):
            print ("AcceptBlock() : incorrect proof of work")
            return False

        # Write block to history file
        ret = self.write_to_disk(not ctx.fClient)
        if ret is None:
            print ("AcceptBlock() : WriteToDisk failed")
            return False
        file_index = ret[0]
        block_pos = ret[1]
        # 此时获取的 file_index 和 block_pos 是一个已经写入硬盘，已经验证块本身是合法的
        # 会在 checkblock 后调用，但是此时的块file_index和block_pos 还未被和之前的块链在一起
        if not self.add_to_blockindex(file_index, block_pos):
            print ("AcceptBlock() : AddToBlockIndex failed")
            return False

        if ctx.hashBestChain == block_hash:
            netaction.relay_inventory(net.PyInv(net.MsgType.MSG_BLOCK, block_hash))

        return True

    pass


# #
#  The block chain is a tree shaped structure starting with the
#  genesis block at the root, with each block potentially having multiple
#  candidates to be the next block.  pprev and pnext link a path through the
#  main/longest chain.  A blockindex may have multiple pprev pointing back
#  to it, but pnext will only point forward to the longest branch, or will
#  be null if the block is not part of the longest chain.
#
class PyBlockIndex(object):
    medianTimeSpan = 11

    # @class_params_check(int, int, PyBlock)
    def __init__(self, nfile=0, block_pos=0, py_block=None):
        """
        注意 传入的 py_block 并不构造blockindex的 hash_block \n
        :param nfile:
        :param block_pos:
        :param py_block:
        """
        self.hash_block = 0  # uint256
        self.prev_index = None  # PyBlockIndex
        self.next_index = None  # PyBlockIndex
        self.file_index = nfile  # uint
        self.block_pos = block_pos  # uint
        self.height = 0  # int
        # block header
        if py_block is not None:
            self.version = py_block.version  # int
            self.hash_merkle_root = py_block.hash_merkle_root  # uint256
            self.time = py_block.time  # uint
            self.bits = py_block.bits  # uint
            self.nonce = py_block.nonce  # uint
        else:
            self.version = 0
            self.hash_merkle_root = 0  # uint256
            self.time = 0
            self.bits = 0
            self.nonce = 0

    def is_in_main_chain(self):
        return self.next_index or (id(self) == id(ctx.indexBest))

    def erase_block_from_disk(self):
        file_out = util.open_block_file(self.file_index, self.block_pos, "rb+")
        if file_out is None:
            return False
        # Overwrite with empty null block
        block = PyBlock()
        block.set_null()
        file_out.stream_in(block.serialize(file_out.nType, file_out.nVersion))  # override data
        return True

    def init(self, block_index):
        assert isinstance(block_index, PyBlockIndex), "not the same type for PyBlockIndex"
        self.hash_block = block_index.hash_block
        self.prev_index = block_index.prev_index
        self.next_index = block_index.next_index
        self.file_index = block_index.file_index
        self.block_pos = block_index.block_pos
        self.height = block_index.height
        # header
        self.version = block_index.version
        self.hash_merkle_root = block_index.hash_merkle_root  # uint256
        self.time = block_index.time
        self.bits = block_index.bits
        self.nonce = block_index.nonce

    def get_block_hash(self, output_type=None):
        if output_type == 'str':
            return ser_uint256(self.hash_block)
        elif output_type == 'hex':
            return hexser_uint256(self.hash_block)
        return self.hash_block

    def get_median_time_past(self):
        """
        从当前区块的向前找11个区块并记录它们的区块时间，并取出位于排序中位数的时间\n
        对于11这个数字来说，中位数就是5，也就是从当前块(把当前块看作0)向前数第5个块的时间(如果是链确实按顺序排列)\n
        :return:
        """
        block_index = self
        times = list()
        for i in range(PyBlockIndex.medianTimeSpan):
            if block_index is None:
                break
            times.append(block_index.time)
            block_index = block_index.prev_index
        times.sort()  # = sorted(times)
        return times[len(times) / 2]

    def get_median_time(self):
        block_index = self
        for i in range(PyBlockIndex.medianTimeSpan / 2):
            if block_index.next_index is None:
                return self.time
            block_index = block_index.next_index
        return block_index.get_median_time_past()

    def __str__(self):
        return "PyBlockIndex(nprev=%s, pnext=%s, nFile=%d, nBlockPos=%-6d nHeight=%d, merkle=%s, hashBlock=%s)" % \
               (self.prev_index.get_block_hash(output_type='hex')[:6] if self.prev_index else 'None',
                self.next_index.get_block_hash(output_type='hex')[:6] if self.next_index else 'None',
                self.file_index, self.block_pos, self.height,
                hexser_uint256(self.hash_merkle_root)[:6],
                self.get_block_hash(output_type='hex')[:14])
        pass

    pass


#
#  Used to marshal pointers into hashes for db storage.
#
class PyDiskBlockIndex(PyBlockIndex, Serializable):
    @class_params_check(PyBlockIndex)
    def __init__(self, block_index=None):
        super(PyDiskBlockIndex, self).__init__()
        if block_index is not None:
            super(PyDiskBlockIndex, self).init(block_index)
            self.hash_prev = self.prev_index.get_block_hash() if self.prev_index else 0
            self.hash_next = self.next_index.get_block_hash() if self.next_index else 0
        else:
            self.hash_prev = 0  # uint256
            self.hash_next = 0  # uint256

    def deserialize(self, f, nType=0, nVersion=VERSION):
        f = wrap_to_StringIO(f)
        if not (nType & SerType.SER_GETHASH):
            nVersion = deser_int(f)
        self.hash_next = deser_uint256(f)
        self.file_index = deser_uint(f)
        self.block_pos = deser_uint(f)
        self.height = deser_int(f)
        # block header
        self.version = deser_int(f)
        self.hash_prev = deser_uint256(f)
        self.hash_merkle_root = deser_uint256(f)
        self.time = deser_uint(f)
        self.bits = deser_uint(f)
        self.nonce = deser_uint(f)
        return self

    def serialize(self, nType=0, nVersion=VERSION):
        s = StringIO()
        if not (nType & SerType.SER_GETHASH):
            s.write(ser_int(nVersion))
        s.write(ser_uint256(self.hash_next))
        s.write(ser_uint(self.file_index))
        s.write(ser_uint(self.block_pos))
        s.write(ser_int(self.height))
        # block header
        s.write(ser_int(self.version))
        s.write(ser_uint256(self.hash_prev))
        s.write(ser_uint256(self.hash_merkle_root))
        s.write(ser_uint(self.time))
        s.write(ser_uint(self.bits))
        s.write(ser_uint(self.nonce))
        return s.getvalue()

    def get_block_hash(self, output_type=None):
        b = PyBlock()
        b.version = self.version
        b.hash_prev_block = self.hash_prev
        b.hash_merkle_root = self.hash_merkle_root
        b.time = self.time
        b.bits = self.bits
        b.nonce = self.nonce
        return b.get_hash(output_type=output_type)

    def __str__(self):
        s = "CDiskBlockIndex("
        s += super(PyDiskBlockIndex, self).__str__()
        s += "\n                hashBlock=%s, hashPrev=%s, hashNext=%s)" % \
             (self.get_block_hash('hex'),
              hexser_uint256(self.hash_prev)[:14],
              hexser_uint256(self.hash_next)[:14])
        return s

    pass


#
#  Describes a place in the block chain to another node such that if the
#  other node doesn't have the same branch, it can find a recent common trunk.
#  The further back it is, the further before the fork it may be.
#
class PyBlockLocator(Serializable):
    def __init__(self, block_index=None):
        self.l_have = list()  # vector<uint256>
        if block_index is not None:
            if isinstance(block_index, int) or isinstance(block_index, long):
                block_index = ctx.dictBlockIndex.get(block_index, None)
            elif not isinstance(block_index, PyBlockIndex):
                raise RuntimeError("params blockIndex must be Block hash or class PyBlockIndex")
            self.set(block_index)
        pass

    def deserialize(self, f, nType=0, nVersion=VERSION):
        f = wrap_to_StringIO(f)
        if not (nType & SerType.SER_GETHASH):
            nVersion = deser_int(f)
        self.l_have = deser_uint256_list(f)
        return self

    def serialize(self, nType=0, nVersion=VERSION):
        s = StringIO()
        if not (nType & SerType.SER_GETHASH):
            s.write(ser_int(nVersion))
        s.write(ser_uint256_list(self.l_have))
        return s.getvalue()

    @class_params_check(PyBlockIndex)
    def set(self, block_index):
        if block_index is None:
            return
        self.l_have = list()
        step = 1
        while block_index:
            self.l_have.append(block_index.get_block_hash())
            for i in range(step):
                if block_index is None:
                    break
                block_index = block_index.prev_index
            if len(self.l_have) > 10:
                step *= 2
        self.l_have.append(ctx.hashGenesisBlock)

    def get_block_index(self):
        # Find the first block the caller has in the main chain
        for uint256_hash in self.l_have:
            block_index = ctx.dictBlockIndex.get(uint256_hash, None)
            if block_index is not None:
                if block_index.is_in_main_chain():
                    return block_index
        return ctx.indexGenesisBlock

    def get_block_hash(self):
        # Find the first block the caller has in the main chain
        for uint256_hash in self.l_have:
            block_index = ctx.dictBlockIndex.get(uint256_hash, None)
            if block_index is not None:
                if block_index.is_in_main_chain():
                    return uint256_hash
        return ctx.hashGenesisBlock

    def get_height(self):
        block_index = self.get_block_index()
        if block_index is None:
            return 0
        return block_index.height

    pass


###
##  Tx
###
class PyMerkleTx(Tx.PyTransaction):
    @class_params_check(Tx.PyTransaction)
    def __init__(self, py_tx=None):
        super(PyMerkleTx, self).__init__()
        self.hash_block = 0  # uint256 # 当前的tx所在的block的 hash
        self.merkle_branch = list()  # vector<uint256>  # 当前的tx所关联的 merkle branch(对称)节点(tx)信息
        self.index = -1  # int  # 当前的tx在block中的index
        self.merkle_verified = False
        # uint256 hashBlock;
        # vector<uint256> vMerkleBranch;
        # int nIndex;
        if py_tx is not None:
            super(PyMerkleTx, self).init(py_tx)

    def init(self, merkle_tx):
        assert isinstance(merkle_tx, PyMerkleTx), "param must be PyMerkleTx class"
        super(PyMerkleTx, self).init(merkle_tx)
        self.hash_block = merkle_tx.hash_block
        self.merkle_branch = merkle_tx.merkle_branch
        self.index = merkle_tx.index
        self.merkle_verified = merkle_tx.merkle_verified
        pass

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        f = wrap_to_StringIO(f)
        super(PyMerkleTx, self).deserialize(f, nType, nVersion)
        self.hash_block = deser_uint256(f)
        self.merkle_branch = deser_uint256_list(f)
        self.index = deser_int(f)
        return self

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        s = StringIO()
        s.write(super(PyMerkleTx, self).serialize(nType, nVersion))
        s.write(ser_uint256(self.hash_block))
        s.write(ser_uint256_list(self.merkle_branch))
        s.write(ser_int(self.index))
        return s.getvalue()

    def get_credit(self):
        # Must wait until coinbase is safely deep enough in the chain before valuing it
        if self.is_coinbase() and self.get_blocks_to_maturity() > 0:
            return 0
        return super(PyMerkleTx, self).get_credit()

    def set_merkle_branch(self, block=None):
        """
        可以根据传入的block或者自己父类的tx的信息填充PyMerkleTx关于 \n
        hash_block, merkle_branch, index 的信息 \n
        返回当前tx所在的block距离最新block的长度(当前block的陈旧度indexBest.height - block.height + 1)\n
        即距离最新的block的 深度 depth\n
        :param block:
        :return:
        """
        if ctx.fClient:
            # 如果是在客户端的情况下，那么set block 是不会起作用的
            if self.hash_block == 0:
                return 0
        else:

            if block is None:
                # 如果没有传入block，那么就从该merkleTx(父PyTx)的hash查找 Txindex并根据txindex查找block
                txdb = Tx.PyTxDB()
                txindex = txdb.read_txindex(self.get_hash())
                txdb.close()
                if txindex is None:
                    return 0
                block_tmp = PyBlock()
                if not block_tmp.read_from_disk(txindex.txpos.file_index, txindex.txpos.block_pos, True):
                    return 0
                block = block_tmp
            # update the tx's hashblock
            self.hash_block = block.get_hash()
            # Locate the transaction
            self.index = 0
            while True:
                if self.index >= len(block.l_tx):
                    break

                if super(PyMerkleTx, self).__eq__(block.l_tx[self.index]):
                    break
                self.index += 1
            # 把block中的 tx 全部找过来但是没有找到
            if self.index == len(block.l_tx):
                self.merkle_branch = []
                self.index = -1
                # TODO add log!
                print "ERROR: set_mkerkle_branch() : couldn't find tx in block"
                return 0
            self.merkle_branch = block.get_merkle_branch(self.index)
            # endif
            pass

        # Is the tx in a block that's in the main chain
        block_index = ctx.dictBlockIndex.get(self.hash_block, None)  # 根据blockhash得到blockindex
        if block_index is None:
            return 0
        if not block_index.is_in_main_chain():
            return 0
        return ctx.indexBest.height - block_index.height + 1

    def get_depth_in_main_chain(self):
        if self.hash_block == 0 or self.index == -1:
            return 0
        # Find the block it claims to be in
        block_index = ctx.dictBlockIndex.get(self.hash_block, None)
        if block_index is None:
            return 0
        if not block_index or not block_index.is_in_main_chain():
            return 0

        # Make sure the merkle branch connects to this block
        if not self.merkle_verified:
            tx_ser = Tx.PyTransaction.serialize(self, nType=SerType.SER_GETHASH, nVersion=cfg.VERSION)
            tx_hash = Hash(tx_ser, out_type='str')
            if PyBlock.check_merkle_branch(tx_hash, self.merkle_branch, self.index) \
                    != block_index.hash_merkle_root:
                return 0
            self.merkle_verified = True
        assert ctx.indexBest is not None, "indexBest must be inited first!"
        return ctx.indexBest.height - block_index.height + 1

    def is_in_main_chain(self):
        return self.get_depth_in_main_chain() > 0

    def get_blocks_to_maturity(self):
        if not self.is_coinbase():
            return 0
        # return max(0, cfg.COINBASE_MATURITY + 20 - self.get_depth_in_main_chain())
        return max(0, cfg.COINBASE_MATURITY - self.get_depth_in_main_chain())

    def accept_transaction(self, txdb=None, check_inputs=True, missing_inputs=None):
        if ctx.fClient:
            if not self.is_in_main_chain() and not self.client_connect_inputs():
                return False
            return super(PyMerkleTx, self).accept_transaction(txdb, False)
        else:
            return super(PyMerkleTx, self).accept_transaction(txdb, check_inputs)

    pass


#
#  A transaction with a bunch of additional info that only the owner cares
#  about.  It includes any unrecorded transactions needed to link it back
#  to the block chain.
#
class PyWalletTx(PyMerkleTx):
    def __init__(self, tx=None):
        super(PyWalletTx, self).__init__()
        self.list_tx_prev = list()  # vector<PyMerkleTx>  # 采用广度遍历的方式，找到当前tx的在3个区块内的所有前置tx，这里叫做 supporting tx
        self.dict_value = dict()  # map<string,string>
        self.list_order_form = list()  # vector<pair<string,string>>  pair<label, value>  label if from product.list_order_from<label, control>
        self.time_received_is_tx_time = 0  # uint
        self.time_received = 0  # time received by this node uint
        self.from_me = 0  # char
        self.spent = 0  # char

        # memory only
        self.time_displayed = 0

        if tx is not None:
            if isinstance(tx, PyMerkleTx):
                super(PyWalletTx, self).init(tx)
            elif isinstance(tx, Tx.PyTransaction):
                super(PyMerkleTx, self).init(tx)
        pass

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        f = wrap_to_StringIO(f)
        super(PyWalletTx, self).deserialize(f, nType, nVersion)
        nVersion = self.version
        self.list_tx_prev = deser_list(f, PyMerkleTx, nType=nType, nVersion=nVersion)  # vector<PyMerkleTx>
        self.dict_value = deser_str_dict(f)  # map<string,string>
        self.list_order_form = deser_strpair_list(f)  # vector<pair<string,string>>
        self.time_received_is_tx_time = deser_uint(f)  # uint
        if not (nType & SerType.SER_GETHASH):
            self.time_received = deser_uint(f)  # uint
        self.from_me = deser_char(f)  # char
        self.spent = deser_char(f)  # char
        return self

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        s = StringIO()
        s.write(super(PyWalletTx, self).serialize(nType, nVersion))
        nVersion = self.version
        s.write(ser_list(self.list_tx_prev, cls=PyMerkleTx, nType=nType, nVersion=nVersion))  # vector<PyMerkleTx>
        s.write(ser_str_dict(self.dict_value))  # map<string,string>
        s.write(ser_strpair_list(self.list_order_form))  # vector<pair<string,string>>
        s.write(ser_uint(self.time_received_is_tx_time))  # uint
        if not (nType & SerType.SER_GETHASH):
            s.write(ser_uint(self.time_received))  # uint
        s.write(ser_char(self.from_me))  # char
        s.write(ser_char(self.spent))  # char
        return s.getvalue()

    def write_to_disk(self):
        with Tx.PyWalletDB() as walletdb:
            walletdb.write_tx(self.get_hash(), self)

    def get_tx_time(self):
        if not self.time_received_is_tx_time and self.hash_block != 0:
            # If we did not receive the transaction directly, we rely on the block's
            # time to figure out when it happened.  We use the median over a range
            #  of blocks to try to filter out inaccurate block times.
            block_index = ctx.dictBlockIndex.get(self.hash_block)
            if block_index is not None:
                return block_index.get_median_time_past()
        return self.time_received

    def add_supporting_transactions(self, txdb):
        self.list_tx_prev = list()
        # 当前tx所在的block比较新，没超过目前block的三个(copy_depth = 3)
        if self.set_merkle_branch() < cfg.COPY_DEPTH:
            # work_queue 是该tx的所有 In 的 tx 的 hash list(queue)
            work_queue = [txin.prev_out.hash_tx for txin in self.l_in]

            # This critsect is OK because txdb is already open
            # with ctx.dictWalletLock:  # TODO useless lock
            d_wallet_prev = dict()
            s_already_done = set()
            for tx_hash in work_queue:  # 改成 队列 pop 可读性更强一点
                if tx_hash in s_already_done:
                    continue
                s_already_done.add(tx_hash)

                wallettx_prev = None  # PyWalletTx()
                if tx_hash in ctx.dictWallet:
                    wallettx_prev = ctx.dictWallet[tx_hash]
                    for tx_prev in wallettx_prev.list_tx_prev:
                        d_wallet_prev[tx_prev.get_hash()] = tx_prev
                elif tx_hash in d_wallet_prev:
                    wallettx_prev = d_wallet_prev[tx_hash]
                elif not ctx.fClient and txdb.read_disk_tx(tx_hash, wallettx_prev):
                    # 注意这里从disk中应该只能读取中PyTx 的信息，而其继承类 PyMerkleTx 和 PyWalletTx都应该都不出
                    pass
                else:
                    print ("ERROR: AddSupportingTransactions() : unsupported transaction")
                    continue
                depth = wallettx_prev.set_merkle_branch()  # 这里也起到从tx填充 merkletx 的作用
                # 填充 tx_prev 注意这里的tx_prev是当前tx所关联的多级tx(不只是本tx的in的wallettx,的是包括这些in的in及以上)，直到3个block的深度的tx
                self.list_tx_prev.append(wallettx_prev)
                # 这里是广度遍历，只要关联的前置tx在3个区块内，就放入队列
                if depth < cfg.COPY_DEPTH:
                    for txin in wallettx_prev.l_in:
                        work_queue.append(txin.prev_out.hash_tx)  # 这个tx的block比较新，继续跟前面的
                # end for
                pass
            # pass  # end critsect
            pass  # end if
        self.list_tx_prev = self.list_tx_prev[::-1]
        pass  # end func

    def accept_wallet_transaction(self, txdb=None, check_inputs=True):
        if txdb is None:
            txdb = Tx.PyTxDB("r")
        with ctx.dictTransactionsLock:
            for merkletx in self.list_tx_prev:
                if not merkletx.is_coinbase():
                    tx_hash = merkletx.get_hash()
                    if not (tx_hash in ctx.dictTransactions) and not txdb.contains_tx(tx_hash):
                        merkletx.accept_transaction(txdb, check_inputs)

            if not self.is_coinbase():
                return self.accept_transaction(txdb, check_inputs)

        return True

    # 传播 wallet tx
    def relay_wallet_transaction(self, txdb=None):
        if txdb is None:
            txdb = Tx.PyTxDB("r")
        for merkletx in self.list_tx_prev:
            if not merkletx.is_coinbase():
                tx_hash = merkletx.get_hash()
                if not txdb.contains_tx(tx_hash):
                    # pure_tx = Tx.PyTransaction()
                    # pure_tx.init(self)
                    pure_tx = deepcopy(self)
                    netaction.relay_message(net.PyInv(net.MsgType.MSG_TX, tx_hash), pure_tx)
        if not self.is_coinbase():
            tx_hash = self.get_hash()
            if not txdb.contains_tx(tx_hash):
                print ("Relaying wtx %s" % hexser_uint256(tx_hash))
                # pure_tx = Tx.PyTransaction()
                # pure_tx.init(self)
                pure_tx = deepcopy(self)
                netaction.relay_message(net.PyInv(net.MsgType.MSG_TX, tx_hash), pure_tx)
        pass

    # end class
    pass


class PyWalletExtDB(Tx.PyWalletDB):
    def __init__(self, szmode="r+", f_txn=False):
        super(PyWalletExtDB, self).__init__(szmode, f_txn)

    def load_wallet(self):
        default_key = ''

        with ctx.dictKeysLock:
            with ctx.dictWalletLock:
                ret = self.read_datas(types=
                                      [self.DBKEY_NAME, (self.DBKEY_TX, PyWalletTx),
                                       self.DBKEY_KEY, self.DBKEY_DEFAULTKEY, self.DBKEY_SETTING])
                if ret is None:
                    return None
                for key, value in ret:
                    if isinstance(key, (list, tuple)):
                        str_type = key[0]
                    else:
                        str_type = key
                    if str_type == self.DBKEY_NAME:
                        addr = key[1]
                        ctx.dictAddressBook[addr] = value
                    elif str_type == self.DBKEY_TX:
                        tx_hash = key[1]  # num format
                        ctx.dictWallet[tx_hash] = value
                        if value.get_hash() != tx_hash:
                            print ("Error in wallet.dat, hash mismatch")
                    elif str_type == self.DBKEY_KEY:
                        pubkey = key[1]
                        prikey = value
                        ctx.dictKeys[pubkey] = prikey
                        ctx.dictPubKeys[Hash160(pubkey, out_type='str')] = pubkey
                    elif str_type == self.DBKEY_DEFAULTKEY:
                        default_key = value
                    elif str_type == self.DBKEY_SETTING:
                        str_key = key[1]
                        if str_key == self.DBKEY_SETTING_GEN_COIN:
                            ctx.fGenerateCoins = bool(value)
                        elif str_key == self.DBKEY_SETTING_TX_FEE:
                            ctx.transactionFee = float(value)
                        elif str_key == self.DBKEY_SETTING_ADDR:
                            ins = net.PyAddress()
                            ins.deserialize(value, nType=SerType.SER_DISK)
                            ctx.addrIncoming = ins

        return default_key

    pass


class PyTxExtDB(Tx.PyTxDB):
    def __init__(self, szmode="r+", f_txn=False):
        super(PyTxExtDB, self).__init__(szmode, f_txn)

    def load_blockindex(self):  # cls must be PyDiskBlockIndex
        ret = self.read_datas(key=(self.DBKEY_BLOCKINDEX, 0),
                              types=[(self.DBKEY_BLOCKINDEX, PyDiskBlockIndex)],
                              flags=self.DB_SET_RANGE)
        if ret is None:
            ret = []
        for key, value in ret:
            disk_index = value  # disk_index : PyDiskBlockIndex
            index_new = insert_blockindex(disk_index.get_block_hash())  # index_new : PyBlockIndex
            index_new.prev_index = insert_blockindex(disk_index.hash_prev)
            index_new.next_index = insert_blockindex(disk_index.hash_next)
            index_new.file_index = disk_index.file_index
            index_new.block_pos = disk_index.block_pos
            index_new.height = disk_index.height
            index_new.version = disk_index.version
            index_new.hash_merkle_root = disk_index.hash_merkle_root
            index_new.time = disk_index.time
            index_new.bits = disk_index.bits
            index_new.nonce = disk_index.nonce

            # Watch for genesis block and best block
            if ctx.indexGenesisBlock is None and disk_index.get_block_hash('hex') == ctx.hashGenesisBlock:
                ctx.indexGenesisBlock = index_new  # 默认为存储的第一个块就是 genesisBlock
        hash_best_chain = self.read_hash_best_chain()
        if hash_best_chain is None:
            if ctx.indexGenesisBlock is None:
                return True
            print ("TxDB::LoadBlockIndex() : hashBestChain not found")
            return False

        ctx.hashBestChain = hash_best_chain

        index = ctx.dictBlockIndex.get(hash_best_chain, None)
        if index is None:
            print ("TxDB::LoadBlockIndex() : blockindex for hashBestChain not found")
            return False

        ctx.indexBest = index
        ctx.bestHeight = index.height
        print ("LoadBlockIndex(): hashBestChain=%s  height=%d\n" % (hexser_uint256(hash_best_chain)[:14],
                                                                    index.height))
        return True

    pass


# action
def relay_wallet_transaction():
    # 小于 10 分钟就返回
    now = timeutil.get_time()
    if now - ctx.lastTime < cfg.RELAY_TX_SPAN:
        return
    ctx.lastTime = now

    # Rebroadcast any of our txes that aren't in a block yet
    print ("RelayWalletTransactions()")
    txdb = Tx.PyTxDB("r")

    with ctx.dictWalletLock:
        # Sort them in chronological order
        wtxs = sorted(ctx.dictWallet.values(), key=lambda wtx: wtx.time_received)
        [wtx.relay_wallet_transaction(txdb) for wtx in wtxs]
    txdb.close()
    pass


def get_next_work_required(index_last):
    """

    :param index_last:
    :type index_last: PyBlockIndex
    :return:
    """
    target_timespan = cfg.TARGET_TIMESPAN
    target_spacing = cfg.TARGET_SPACING
    interval = target_timespan / target_spacing  # 每两次更改的高度间隔

    # genesis block:
    if index_last is None:
        return ctx.proofOfWorkLimit.get_compact()

    # Only change once per interval
    if (index_last.height + 1) % interval != 0:
        return index_last.bits

    # Go back by what we want to be 14 days worth of blocks
    index_first = index_last
    for _ in range(interval - 1):
        if index_first is None:
            break
        index_first = index_first.prev_index
    assert index_first, "error the block chain is not long enough or this block is orphan block"

    # Limit adjustment step
    actual_timespan = index_last.time - index_first.time
    print ("  nActualTimespan = %d  before bounds" % actual_timespan)
    if actual_timespan < target_timespan / 4:
        actual_timespan = target_timespan / 4
    if actual_timespan > target_timespan * 4:
        actual_timespan = target_timespan * 4

    # retarget
    bn_new = BN.PyBigNum.set_compact(index_last.bits)
    bn_new *= actual_timespan
    bn_new /= target_timespan  # equal to  >> or << 2
    # bn_bew = bn_new * (actual_timespan/target_timespan)
    # bn_new is long
    if bn_new > ctx.proofOfWorkLimit:  # 限制最低难度要求
        bn_new = ctx.proofOfWorkLimit
    bn_new = BN.PyBigNum(bn_new)
    # debug print
    print ("\n\n\nGetNextWorkRequired RETARGET *****")
    print ("nTargetTimespan = %d    nActualTimespan = %d\n" % (target_timespan, actual_timespan))
    print ("Before: %08x  %s" % (index_last.bits, BN.PyBigNum.set_compact(index_last.bits).get_uint256(out_type="hex")))
    print ("After:  %08x  %s\n" % (bn_new.get_compact(), bn_new.get_uint256(out_type="hex")))

    return bn_new.get_compact()


# mapWallet
def add_to_wallet(wtx_in):
    """

    :param wtx_in:
    :type wtx_in: Tx.PyWalletTx
    :return:
    """
    tx_hash = wtx_in.get_hash()
    with ctx.dictWalletLock:
        # Inserts only if not already there, returns tx inserted or tx found
        inserted_new = False
        wtx = ctx.dictWallet.get(tx_hash, None)  # 注意这里是引用
        if wtx is None:  # 如果不在缓存里面
            wtx_in.time_received = timeutil.get_adjusted_time()  # 这里的 received_time 不管是自己节点产生的还是收到的都会有这个赋值，区别在与自己一产生这个就会记录，而矿工则是真正收到
            # ctx.dictWallet[tx_hash] = wtx_in
            inserted_new = True
            wtx = wtx_in

        ## debug print
        print ("AddToWallet %s  %s" % (hexser_uint256(tx_hash), "new" if inserted_new else "update"))

        if not inserted_new:  # update
            updated = False
            if wtx_in.hash_block != 0 and wtx_in.hash_block != wtx.hash_block:
                wtx.hash_block = wtx_in.hash_block
                updated = True
            if wtx_in.index != -1 and \
                    (wtx_in.merkle_branch != wtx.merkle_branch or wtx_in.index != wtx.index):
                wtx.merkle_branch = wtx_in.merkle_branch
                wtx.index = wtx_in.index
                updated = True
            if wtx_in.from_me and wtx_in.from_me != wtx.from_me:  # 只有from_me 是 True 才会更新
                wtx.from_me = wtx_in.from_me
                updated = True
            if wtx_in.spent and wtx_in.spent != wtx.spent:  # 只有被标记为被花费才会更新
                wtx.spent = wtx_in.spent
                updated = True
            if wtx_in.time_received != wtx.time_received:
                wtx.time_received = wtx_in.time_received
                updated = True
            if not updated:  # 表示和本地存储的一个样
                return True

        # Write to disk
        wtx.write_to_disk()
        ctx.dictWallet[tx_hash] = wtx  # update

        # Notify UI
        ctx.listWalletUpdated.append((tx_hash, inserted_new))
        return True


def add_to_wallet_if_mine(tx, block=None):
    """
    如果该tx的out是指向自己的(地址)，那么就把这个tx添加到wallet中\n
    :param tx:
    :type tx: Tx.PyTransaction
    :param block:
    :type block: PyBlock | None
    :return:
    """
    if tx.is_mine() or (tx.get_hash() in ctx.dictWallet):
        wtx = PyWalletTx(tx)  # wtx == WalletTx
        # Get merkle branch if transaction was found in a block
        if block:
            wtx.set_merkle_branch(block)
        return add_to_wallet(wtx)
    return True


def reorganize(txdb, index_new):
    """
    当发现区块的prev不是目前的本地保留的hash_best_chain(出现分叉),\n
    那么就调用该函数重新整理block的链接关系
    :param txdb:
    :type txdb: PyTxDB
    :param index_new: 发现分叉(异常)的区块
    :type index_new: PyBlockIndex
    :return:
    """
    print ("*** REORGANIZE ***")
    # Find the fork
    fork_index = ctx.indexBest  # 目前bestchain的index 指向的分叉
    longer_index = index_new  # index_new 的height一定大于 indexBest的height(应该只大于1)

    # 退到两个指针都指向同一个块 比较指针就足够了 blockindex 没有重载过 ==
    # while fork_index != longer_index:
    while id(fork_index) != id(longer_index):
        fork_index = fork_index.prev_index
        if fork_index is None:
            print ("Reorganize() : pfork->pprev is null")
            return False
        while longer_index.height > fork_index.height:  # longer_index退到和fork_index相同的高度
            longer_index = longer_index.prev_index
            if longer_index is None:  # 遇到了孤儿块
                print ("Reorganize() : plonger->pprev is null")
                return False

    # List of what to disconnect
    disconnet = list()
    index = ctx.indexBest
    while id(index) != id(fork_index):
        disconnet.append(index)
        index = index.prev_index
    # List of what to connect
    connect = list()
    index = index_new
    while id(index) != id(fork_index):
        connect.append(index)  # 这里是反向添加的
        index = index.prev_index
    connect = connect[::-1]  # 把 connect 按照正向的顺序排列

    # Disconnect shorter branch
    resurrect = list()
    for index in disconnet:
        block = PyBlock()
        if not block.read_from_disk(index.file_index, index.block_pos, True):
            print ("Reorganize() : ReadFromDisk for disconnect failed")
            return False
        if not block.disconnect_block(txdb, index):
            print ("Reorganize() : DisconnectBlock failed")
            return False

        # Queue memory transactions to resurrect
        for tx in block.l_tx:  # 暂存下废弃区块的所有交易
            if not tx.is_coinbase():
                resurrect.append(tx)

    # Connect longer branch
    delete = list()
    connect_size = len(connect)
    for i in range(connect_size):
        index = connect[i]
        block = PyBlock()
        if not block.read_from_disk(index.file_index, index.block_pos, True):
            print ("Reorganize() : ReadFromDisk for disconnect failed")
            return False
        if not block.connect_block(txdb, index):
            # Invalid block, delete the rest of this branch
            txdb.txn_abort()
            for j in range(i, connect_size):
                index = connect[j]
                index.erase_block_from_disk(index.get_block_hash())
                ctx.dictBlockIndex.pop(index.get_block_hash(), None)
            print ("Reorganize() : ConnectBlock failed")
            return False
        # Queue memory transactions to delete
        for tx in block.l_tx:
            delete.append(tx)
    txdb.write_hash_best_chain(index_new.get_block_hash())

    # Commit now because resurrecting could take some time
    txdb.txn_commit()

    # Disconnect shorter branch
    for index in disconnet:
        if index.prev_index:
            index.prev_index.next_index = None

    # Connect longer branch
    for index in connect:
        if index.prev_index:
            index.prev_index.next_index = index

    # Resurrect memory transactions that were in the disconnected branch
    for tx in resurrect:
        tx.accept_transaction(txdb, False)

    # Delete redundant memory transactions that are in the connected branch
    for tx in delete:
        tx.remove_from_memory_pool()

    return True


def insert_blockindex(block_hash):
    """
    针对 传入的 block hash 向 mapBlockIndex 插入一个空的 PyBlockIndex。\n
    若已存在于 mapBlockIndex 中则返回已经有的那个
    :param block_hash:
    :return:
    :rtype PyBlockIndex
    """
    if block_hash == 0:
        return None
    # Return existing
    block_index = ctx.dictBlockIndex.get(block_hash, None)
    if block_index is not None:
        return block_index

    # Create new
    block_index = PyBlockIndex()  # 注意这个index是空的，不起任何作用
    block_index.hash_block = block_hash
    ctx.dictBlockIndex[block_hash] = block_index
    return block_index


def get_orphan_root(block):
    """

    :param block:
    :type block: PyBlock
    :return:
    :rtype: long
    """
    # Work back to the first block in the orphan chain
    while block.hash_prev_block in ctx.dictOrphanBlocks:
        block = ctx.dictOrphanBlocksByPrev[block.hash_prev_block]
    return block.get_hash()


def main():
    print PyBlock().serialize_size(SerType.SER_DISK)
    b = PyBlock()
    b.hash_prev_block = b.get_hash()
    b.hash_merkle_root = b.get_hash()
    print b.serialize_size(SerType.SER_DISK)

    b = PyBlock()
    b.hash_prev_block = b.get_hash()
    b.hash_prev_block = b.get_hash()
    b.time = 33242
    b.bits = 2345642
    b.nonce = 123453
    print b.serialize_size(SerType.SER_DISK)

    pass


if __name__ == '__main__':
    main()

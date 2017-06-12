#!/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii
import threading
import collections

from app.base.bignum import PyBigNum

from app.base.serialize import deser_uint256
from app.block.key import PyKey
from app import config as cfg

### global state
fClient = False

# thread
listfThreadRunning = [False] * 10


def localServices():
    return 0 if fClient else cfg.NODE_NETWORK


_s = b''
for i in range(32):
    _s += b'\xff'
_s = _s[:30] + b'\x00\x00\x00\x00'  # _s = ~uint256(0) >> 32
proofOfWorkLimit = PyBigNum(_s)  # init
# proofOfWorkLimit : 00 FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
# print proofOfWorkLimit.gethexvch()

mainLock = threading.RLock()

## block
dictBlockIndex = dict()  # <block_hash uint256, PyBlockIndex>
genesis_hexstr = "2e72d19b7558bd6ec869e5601c3613cc7a6b3f24118773d7aaaa3c285493fdfc"  # bit:0x1f00ffff, nonce:87401
hashGenesisBlock = deser_uint256(binascii.unhexlify(genesis_hexstr))
indexGenesisBlock = None
bestHeight = -1  # int 最长链的高度
hashBestChain = 0  # uint256  # 目前本地最长链的 最后一个块的hash
indexBest = None  # PyBlockIndex  # 目前本地最长链的 index

dictOrphanBlocks = dict()  # dict<utin256, PyBlock>
dictOrphanBlocksByPrev = collections.defaultdict(list)  # dict<utin256, list<PyBlock>>
dictOrphanTransactions = dict()  # dict<uint256, PyDataStream>
dictOrphanTransactionsByPrev = collections.defaultdict(list)  # dict<uint256, list<PyDataStream>>

## Tx
dictTransactionsLock = threading.RLock()
dictTransactions = dict()  # <tx_hash uint256, PyTx>
transactionsUpdated = 0  # unsigned int nTransactionsUpdated = 0;
dictNextTx = dict()  # <COutPoint.gethash(), CInPoint> mapNextTx;

# wallet
dictWallet = dict()  # <tx_hash uint256, PyWalletTx>
dictWalletLock = threading.RLock()
listWalletUpdated = list()  # vector<pair<uint256, bool> >
# keys
dictKeys = dict()  # <pubkey str, prikey str> 存储本地所有密钥对
dictPubKeys = dict()  # <hash160 for pubkey str, pubkey str>  存储本地 所有密钥的公钥hash(不是地址)和公钥对
dictKeysLock = threading.RLock()
keyUser = PyKey()

# market
dictProducts = dict()  # dict<uint256, PyProduct>
dictProductsLock = threading.RLock()
dictMyProducts = dict()  # dict<uint256, PyProduct>
# addr
dictAddressBook = dict()  # <string addr, string name>  地址和tag的映射
dictAddresses = dict()  # dict<str(bytearray), PyAddress>
dictAddressesLock = threading.RLock()
# net
hlistenSocket = None
addrProxy = None
nodeLocalHost = None
fShutdown = False
listNodes = list()  # list<PyNode>
listNodesLock = threading.RLock()
dictRelay = dict()  # dict<PyInv, PyDataStream>
listRelayExpiration = collections.deque()  # deque<(int64, PyInv)>
dictRelayLock = threading.RLock()
dictAlreadyAskedFor = dict()  # dict<PyInv, int64>
# db
db_mutex = threading.Lock()

# time
timeOffset = 0

lastTime = 0

# test
dropMessagesTest = 0
# settings
transactionFee = 0
fGenerateCoins = 0
addrIncoming = None

# ui
frameMain = None

listWorkThreads = list()
dictBuff = dict()

# debug
fDebug = False


def main():
    pass


if __name__ == '__main__':
    main()

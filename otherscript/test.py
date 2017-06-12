#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import binascii

from app import config as cfg, context as ctx
from app.base import bignum as BN, serialize
from app.block.key import PyKey  # , CKey
from app.block.tx import script as Script
from app.block.tx import tx as Tx
from app.block import block as Block, action as blkaction
from app.block.utils import cryptoutil
from app.base.bignum import PyBigNum

from app.utils import timeutil


def genesis_block():
    timestamp = "The Times 22/Mar/2017 Chancellor on brink of second bailout for banks"
    tx_new = Tx.PyTransaction()
    txin = Tx.PyTxIn()
    init_nbits = 0x1f00ffff
    sig = Script.PyScript().append(init_nbits).append_num(4).extend(timestamp)
    # script << nbits << extra_nonce
    txin.script_sig = sig
    txout = Tx.PyTxOut()
    txout.value = 50 * cfg.COIN
    # scriptPubKey << OP_DUP << OP_HASH160 << hash160 << OP_EQUALVERIFY << OP_CHECKSIG;   Hash160(pubkey)  # txNew.vout[0].scriptPubKey << key.GetPubKey() << OP_CHECKSIG;
    # txNew.vout[0].scriptPubKey = CScript() << CBigNum("0x5F1DF16B2B704C8A578D0BBAF74D385CDE12C11EE50455F3C438EF4C3FBCF649B6DE611FEAE06279A60939E028A8D65C10B73071A6F16719274855FEB0FD8A6704") << OP_CHECKSIG;
    txout.script_pubkey = Script.PyScript().extend(binascii.unhexlify(cfg.GENESIS_PUBKEY)) \
        .append(Script.OpCodeType.OP_CHECKSIG)

    tx_new.l_in.append(txin)
    tx_new.l_out.append(txout)
    block = Block.PyBlock()
    block.l_tx.append(tx_new)
    block.hash_prev_block = 0
    block.hash_merkle_root = block.build_merkle_tree()
    block.version = 1
    block.time = 1490092537
    # block.bits = 0x2000ffff  #
    block.bits = init_nbits  # nonce:45164 hash:2e72d19b7558bd6ec869e5601c3613cc7a6b3f24118773d7aaaa3c285493fdfc
    # block.bits = 0x1e00ffff  # nonce:xxx (cast almost 5 min)
    block.nonce = 0
    hash_target = BN.PyBigNum.set_compact(block.bits).get_uint256()
    target_hex = serialize.hexser_uint256(hash_target)
    # target_hex = long(hash_target)
    time1 = timeutil.get_time()
    print 'start time:', time1
    while True:
        block_hash = cryptoutil.Hash(block.serialize())
        print 'nonce:', block.nonce
        print 'now hash:'
        print serialize.hexser_uint256(block_hash)
        # print long(block_hash)
        print 'target'
        print target_hex
        if block_hash <= hash_target:
            print 'current nonce:'
            print block.nonce
            print binascii.hexlify(serialize.ser_uint256(block.get_hash()))
            print block.get_hash('hex')
            print long(hash_target)
            break
        block.nonce += 1
    time2 = timeutil.get_time()
    print 'end time:', time2
    diff = time2 - time1
    print ("%d:%d" % (diff / 60, diff % 60))


def test_block():
    timestamp = "The Times 22/Mar/2017 Chancellor on brink of second bailout for banks"
    tx_new = Tx.PyTransaction()
    txin = Tx.PyTxIn()
    init_nbits = 0x1f00ffff
    sig = Script.PyScript().append(init_nbits).append_num(4).extend(timestamp)
    # script << nbits << extra_nonce
    txin.script_sig = sig
    txout = Tx.PyTxOut()
    txout.value = 50 * cfg.COIN
    txout.script_pubkey = Script.PyScript().extend(binascii.unhexlify(cfg.GENESIS_PUBKEY)) \
        .append(Script.OpCodeType.OP_CHECKSIG)

    tx_new.l_in.append(txin)
    tx_new.l_out.append(txout)
    block = Block.PyBlock()
    block.l_tx.append(tx_new)
    block.hash_prev_block = 0
    block.hash_merkle_root = block.build_merkle_tree()
    block.version = 1
    block.time = 1490092537
    block.bits = init_nbits
    block.nonce = 87401

    print block.get_hash('hex')


def testkey():
    hex_secret = '73679658857c2734417c6c017b07edbb2a0e0d191e26c4f488eb8696fca2ba8b'
    hex_pubkey = '049d467dc1c98764995e058874725bc9ec7361fd0dd9a778418baae45004191547e8314f527ed9ce09a2d48fe78237a18e7b893afa28a4106720a2608b716b498e'
    hex_prikey = '30820113020101042073679658857c2734417c6c017b07edbb2a0e0d191e26c4f488eb8696fca2ba8ba081a53081a2020101302c06072a8648ce3d0101022100fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f300604010004010704410479be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8022100fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141020101a144034200049d467dc1c98764995e058874725bc9ec7361fd0dd9a778418baae45004191547e8314f527ed9ce09a2d48fe78237a18e7b893afa28a4106720a2608b716b498e'

    # hex_pubkey = '' + \
    #             'a0dc65ffca799873cbea0ac274015b9526505daaaed385155425f7337704883e'
    # hex_prikey = '308201130201010420' + \
    #              'a0dc65ffca799873cbea0ac274015b9526505daaaed385155425f7337704883e' + \
    #              'a081a53081a2020101302c06072a8648ce3d0101022100' + \
    #              'fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f' + \
    #              '300604010004010704410479be667ef9dcbbac55a06295ce870b07029bfcdb2d' + \
    #              'ce28d959f2815b16f81798483ada7726a3c4655da4fbfc0e1108a8fd17b448a6' + \
    #              '8554199c47d08ffb10d4b8022100' + \
    #              'fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141' + \
    #              '020101a14403420004' + \
    #              '0791dc70b75aa995213244ad3f4886d74d61ccd3ef658243fcad14c9ccee2b0a' + \
    #              'a762fbc6ac0921b8f17025bb8458b92794ae87a133894d70d7995fc0b6b5ab90'

    pubkey = binascii.unhexlify(hex_pubkey)
    # pubkey = hex_pubkey.decode('hex')
    prikey = binascii.unhexlify(hex_prikey)

    print 'source pubkey ,len:', len(pubkey)
    print repr(pubkey)
    print '============='
    print 'source prikey ,len:', len(prikey)
    print repr(prikey)
    print '============='
    print '============='

    # k = CKey()
    # # k.generate(prikey)
    # # k.set_pubkey(pubkey)
    # # print 'ret',k.set_prikey(prikey)
    # # k.generate(binascii.unhexlify('73679658857c2734417c6c017b07edbb2a0e0d191e26c4f488eb8696fca2ba8b'))
    #
    # k.generate(binascii.unhexlify(hex_secret))
    #
    # # print binascii.hexlify(k.get_pubkey())
    # # print binascii.hexlify(k.get_prikey())
    #
    # k.set_pubkey(pubkey)
    # k.set_privkey(prikey)
    #
    #
    # hash = 'Hello, world!'
    # print(k.verify(hash, k.sign(hash)))

    content = 'Hello, world!'

    k2 = PyKey()
    k2.set_pubkey(pubkey)
    k2.set_prikey(prikey)
    print(k2.verify(content, k2.sign(content, True), True))
    pass


def test_txdb():
    txdb = Tx.PyTxDB()
    ret = txdb.read_datas(key=(txdb.DBKEY_BLOCKINDEX, 0),
                          types=[(txdb.DBKEY_BLOCKINDEX, Block.PyDiskBlockIndex)],
                          flags=txdb.DB_SET_RANGE)
    # ret = txdb.read_datas()
    if ret is not None:
        for i in ret:
            print i[0]
    pass


def test_nbits():
    n = PyBigNum.set_compact(0x1f00ffff)
    print serialize.hexser_uint256(n)

    n = PyBigNum.set_compact(0x1d00ffff)
    print serialize.hexser_uint256(n)

    n = PyBigNum(ctx.proofOfWorkLimit)
    print serialize.hexser_uint256(n)
    print serialize.hexser_uint256(PyBigNum.set_compact(n.get_compact()))
    pass


def test_walletdb():
    blkaction.load_wallet()
    for pub, pri in ctx.dictKeys.iteritems():
        print binascii.hexlify(pub)
        print binascii.hexlify(pri)

    print "======="

    for pub, name in ctx.dictPubKeys.iteritems():
        print binascii.hexlify(pub)
        print name
    pass

import types

def test_txn():
    txdb = Tx.PyTxDB(f_txn=True)
    txdb.txn_begin()
    print '123'
    txdb.txn_commit()
    pass


def test_walletdb2():
    # blkaction.load_wallet()
    # print 'load wallet'
    txdb = Tx.PyTxDB("r")
    a = 67279034089938845637059334169987720265371418128753427043266396123319347216136
    print 'modify a'
    ret = txdb.read_txindex(a)
    print ret
    ret = txdb.read_datas()
    for key, value in ret:
        print key
    pass


def main():
    # testkey()
    # genesis_block()
    # print serialize.hexser_uint256(45446052107428226851845234835161094494226001609113020460000898252038)
    # test_txdb()

    # test_block()
    # test_nbits()
    # test_walletdb()
    # test_walletdb2()
    test_txn()
    pass


if __name__ == '__main__':
    main()

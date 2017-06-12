#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import binascii

from app import context as ctx, config as cfg
from app.block import block as Block
from app.block import action as blkaction
from app.block.tx import tx as Tx
from app.block.key import action as keyaction, PyKey
from app.db.db import PyDBInit
from app.net import net as Net


def test_walletdb():
    # blkaction.load_wallet()
    wallet_db = Block.PyWalletExtDB("cr")
    default_key = wallet_db.load_wallet()
    print 'default key:'
    print binascii.hexlify(default_key)
    print '===============keys==========='
    for pubkey, prikey in ctx.dictKeys.iteritems():
        print binascii.hexlify(pubkey)
        print binascii.hexlify(prikey)
        print '====='
    pass


def test_walletdb2(exit=False):
    # blkaction.load_wallet()
    with Block.PyWalletExtDB("cr") as walletdb:
        return walletdb.load_wallet()
        # if exit:
        #     return

    print 'opened:', walletdb.open
    print 'dbinv:', PyDBInit.db_map
    print 'default key:'
    print binascii.hexlify(default_key)
    print '===============keys==========='
    for pubkey, prikey in ctx.dictKeys.iteritems():
        print binascii.hexlify(pubkey)
        print binascii.hexlify(prikey)
        print '====='
    pass


def test_walletdb3():
    print test_walletdb2(True)
    print 'dbinv:', PyDBInit.db_map


def add_genesis_key_to_walletdb():
    hex_pubkey = '049d467dc1c98764995e058874725bc9ec7361fd0dd9a778418baae45004191547e8314f527ed9ce09a2d48fe78237a18e7b893afa28a4106720a2608b716b498e'
    hex_prikey = '30820113020101042073679658857c2734417c6c017b07edbb2a0e0d191e26c4f488eb8696fca2ba8ba081a53081a2020101302c06072a8648ce3d0101022100fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f300604010004010704410479be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8022100fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141020101a144034200049d467dc1c98764995e058874725bc9ec7361fd0dd9a778418baae45004191547e8314f527ed9ce09a2d48fe78237a18e7b893afa28a4106720a2608b716b498e'
    assert hex_pubkey == cfg.GENESIS_PUBKEY, "provided pubkey not equal to config_pubkey"

    pubkey = binascii.unhexlify(hex_pubkey)
    prikey = binascii.unhexlify(hex_prikey)

    k = PyKey()
    k.set_pubkey(pubkey)
    k.set_prikey(prikey)
    # test sig
    content = "hello coin"
    verify = k.verify(content, k.sign(content, True), True)
    print verify
    assert verify, 'prikey not match the pubkey'
    # keyaction.add_key(k, "cr+")
    # keyaction.set_address_book_name(keyaction.pubkey_to_addr(pubkey), "Genesis Addr", "cr+")
    pass


def add_new_address():
    Net.add_address(Net.PyAddrDB("cr+"), Net.PyAddress("192.168.1.50", 8333, services_in=cfg.NODE_NETWORK))


def test_db():
    txdb = Tx.PyTxDB()
    print 'read successful'
    txdb.close()
    print 'end txdb'
    pass


def main():
    # add_genesis_key_to_walletdb()
    # test_walletdb2()
    # test_db()
    add_new_address()
    pass


if __name__ == '__main__':
    main()

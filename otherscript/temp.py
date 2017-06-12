#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import binascii

from app import context as ctx, config as cfg

from app.block.tx.script import *
from app.block.tx import tx as Tx
from app.block import block as Block, action as blkaction


def test_script():

    blkaction.load_wallet()

    timestamp = "The Times 22/Mar/2017 Chancellor on brink of second bailout for banks"
    tx_new = Tx.PyTransaction()
    txin = Tx.PyTxIn()
    init_nbits = 0x1f00ffff
    sig = PyScript().append(init_nbits).append_num(4).extend(timestamp)
    # script << nbits << extra_nonce
    txin.script_sig = sig
    txout = Tx.PyTxOut()
    txout.value = 50 * cfg.COIN
    # scriptPubKey << OP_DUP << OP_HASH160 << hash160 << OP_EQUALVERIFY << OP_CHECKSIG;   Hash160(pubkey)  # txNew.vout[0].scriptPubKey << key.GetPubKey() << OP_CHECKSIG;
    # txNew.vout[0].scriptPubKey = CScript() << CBigNum("0x5F1DF16B2B704C8A578D0BBAF74D385CDE12C11EE50455F3C438EF4C3FBCF649B6DE611FEAE06279A60939E028A8D65C10B73071A6F16719274855FEB0FD8A6704") << OP_CHECKSIG;
    txout.script_pubkey = PyScript().extend(binascii.unhexlify(cfg.GENESIS_PUBKEY)) \
        .append(OpCodeType.OP_CHECKSIG)

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

    Block.add_to_wallet_if_mine(tx_new, block)
    pass


def main():
    # s = PyScript().op_init([OpCodeType.OP_PUBKEY, OpCodeType.OP_CHECKSIG])
    # print str(s)
    test_script()
    pass


if __name__ == '__main__':
    main()

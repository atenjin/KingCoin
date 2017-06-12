#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import binascii
import copy

from app.block.tx import tx as Tx, script as Script
from app import config as cfg


def copytx():
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

    tx = copy.deepcopy(tx_new)

    l1 = list()
    # l1.append(txout)
    # l1.append(txin)
    # copy.deepcopy(l1)
    # s = copy.deepcopy(txout.script_pubkey)
    # print txout.script_pubkey
    # print s
    pass


def main():
    copytx()
    pass


if __name__ == '__main__':
    main()

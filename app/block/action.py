#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import binascii

from app import context as ctx, config as cfg
from app.block.key import action as keyaction
from app.block.tx import tx as Tx, script as Script
from app.block import block as Block
from app.base import serialize
from app.net import base as netbase


def load_wallet():
    wallet_db = Block.PyWalletExtDB("cr")
    default_key = wallet_db.load_wallet()
    if default_key is None:
        wallet_db.close()
        return False

    if default_key in ctx.dictKeys:
        # Set keyUser
        ctx.keyUser.set_pubkey(default_key)
        ctx.keyUser.set_prikey(ctx.dictKeys[default_key])
    else:
        # Create new keyUser and set as default key
        ctx.keyUser.make_new_key()
        pub_key = ctx.keyUser.get_pubkey()
        keyaction.add_key(ctx.keyUser)
        keyaction.set_address_book_name(keyaction.pubkey_to_addr(pub_key), "Your Addr")
        wallet_db.write_default_key(pub_key)
    wallet_db.close()
    return True


def load_blockindex():
    # Load block index
    txdb = Block.PyTxExtDB("cr")
    if not txdb.load_blockindex():
        txdb.close()
        return False

    txdb.close()

    # Init with genesis block
    if not ctx.dictBlockIndex:  # dictBlockIndex is empty()
        if not cfg.ALLOW_NEW:
            return False
        # Genesis block !
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
        block.bits = init_nbits
        block.nonce = 45164
        assert block.get_hash() == ctx.hashGenesisBlock, "genesis block hash not equal to block.get_hash()"
        # start new block file
        ret = block.write_to_disk(not ctx.fClient)
        if ret is None:
            print ("LoadBlockIndex() : writing genesis block to disk failed")
            return False
        file_index = ret[0]
        block_pos = ret[1]
        if not block.add_to_blockindex(file_index, block_pos):
            print ("LoadBlockIndex() : genesis block not accepted")
            return False

        load_genesis_tx(tx_new, block)
        pass  # end if
    return True


def load_genesis_tx(tx, block):
    # txdb = Block.PyTxExtDB()
    # txindex = txdb.read_txindex(tx_hash)
    # txdb.close()
    # tx.connect_inputs(txdb, dict())
    Block.add_to_wallet_if_mine(tx, block)
    pass


def process_block(node_from, block):
    """

    :param node_from:
    :param block:
    :type block: Block.PyBlock
    :return:
    """
    # Check for duplicate
    block_hash = block.get_hash()
    if block_hash in ctx.dictBlockIndex:
        print ("ProcessBlock() : already have block %d %s" % (ctx.dictBlockIndex[block_hash].height,
                                                              serialize.hexser_uint256(block_hash)))
        return False
    if block_hash in ctx.dictOrphanBlocks:
        print ("ProcessBlock() : already have block (orphan) %s" % serialize.hexser_uint256(block_hash))
        return False

    # Preliminary checks
    if not block.check_block():
        del block
        print ("ProcessBlock() : CheckBlock FAILED")
        return False

    # If don't already have its previous block, shunt it off to holding area until we get it
    if block.hash_prev_block not in ctx.dictBlockIndex:
        print ("ProcessBlock: ORPHAN BLOCK, prev=%s" % serialize.hexser_uint256(block.hash_prev_block)[:14])
        ctx.dictOrphanBlocks[block_hash] = block
        ctx.dictOrphanBlocksByPrev[block_hash] = block
        # Ask this guy to fill in what we're missing
        if node_from:
            node_from.push_message(netbase.COMMAND_GETBLOCKS,
                                   Block.PyBlockLocator(ctx.indexBest),
                                   (Block.get_orphan_root(block), "uint256"))
        return True

    # store to disk
    if not block.accept_block():
        del block
        print("ProcessBlock() : AcceptBlock FAILED")
        return False

    del block

    # Recursively process any orphan blocks that depended on this one
    work_queue = list()
    work_queue.append(block_hash)
    for hash_prev in iter(work_queue):
        for block_orphan in ctx.dictOrphanBlocksByPrev[hash_prev]:
            if block_orphan.accept_block():
                work_queue.append(block_orphan.get_hash())
            ctx.dictOrphanBlocks.pop(block_orphan.get_hash(), None)
            del block_orphan
        ctx.dictOrphanBlocksByPrev.pop(hash_prev, None)
    print ("ProcessBlock: ACCEPTED\n")
    return True


def reaccept_wallet_txs():
    # Reaccept any txes of ours that aren't already in a block
    txdb = Tx.PyTxDB("r")
    with ctx.dictWalletLock:
        for tx_hash, wtx in ctx.dictWallet.iteritems():
            if not wtx.is_coinbase() and not txdb.contains_tx(wtx.get_hash()):
                wtx.accept_wallet_transaction(txdb, False)
    txdb.close()


def main():
    pass


if __name__ == '__main__':
    main()

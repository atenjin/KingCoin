#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import copy

from app.block import key as Key, block as Block, action as blkaction
from app.block.tx import tx as Tx, script as Script
from app.base import bignum as BN, serialize
from app import context as ctx, config as cfg
from app.utils import timeutil
from app.block.utils import cryptoutil

from app.block.key import action as kaction


# def format_hash_blocks(s, padding):
#     blocks = 1 + ((len(s) + 8) / 64)
#     end = 64 * blocks  # end = 64 + (len(s) + 8)
#     padding[0] = b'\x80'
#     bits = len(s) * 8
#     end -= len(s)
#     padding[end - 1] = serialize.ser_uchar((bits >> 0) & 0xFF)
#     padding[end - 2] = serialize.ser_uchar((bits >> 8) & 0xFF)
#     padding[end - 3] = serialize.ser_uchar((bits >> 16) & 0xFF)
#     padding[end - 4] = serialize.ser_uchar((bits >> 24) & 0xFF)
#     return blocks


def block_sha256(data, blocks):
    for i in range(blocks):
        cryptoutil.Sha256(data[i * 16 * 4:], output_type="str")
    pass


def bitcoin_miner(t):
    """

    :param t:
    :type t: ExitedThread
    :return:
    """
    print "Miner started"
    # TODO add thread priority  THREAD_PRIORITY_LOWEST
    key = Key.PyKey()
    key.make_new_key()

    extra_nonce = 0
    while ctx.fGenerateCoins:
        timeutil.sleep_msec(50)  # 50 ms
        t.check_self_shutdown()
        if t.exit:
            break
        # while len(ctx.listNodes) == 0:
        #     timeutil.sleep_msec(1000)
        #     t.check_self_shutdown()
        #     if t.exit:
        #         return True

        transactions_updated_last = ctx.transactionsUpdated
        index_prev = ctx.indexBest
        bits = Block.get_next_work_required(index_prev)

        # create coinbase tx
        tx_new = Tx.PyTransaction()
        tx_in = Tx.PyTxIn()
        tx_in.prev_out.set_null()
        extra_nonce += 1
        tx_in.script_sig.append(bits).append(extra_nonce)
        tx_new.l_in.append(tx_in)
        tx_out = Tx.PyTxOut()
        tx_out.script_pubkey.extend(key.get_pubkey()).append(Script.OpCodeType.OP_CHECKSIG)
        tx_new.l_out.append(tx_out)

        # create new block
        block = Block.PyBlock()

        # Add our coinbase tx as first transaction
        block.l_tx.append(tx_new)

        # Collect the latest transactions into the block
        fees = 0
        with ctx.mainLock:
            with ctx.dictTransactionsLock:
                txdb = Tx.PyTxDB("r")
                test_pool = dict()  # map<uint256, PyTxIndex>
                flag_already_added = [False] * len(ctx.dictTransactions)
                found_something = True
                block_size = 0
                while found_something and block_size < cfg.MAX_SIZE / 2:  # block_size < 2MB/2 = 1MB
                    found_something = False
                    n = 0
                    for tx_hash, tx in ctx.dictTransactions.iteritems():
                        if flag_already_added[n]:
                            continue
                        if tx.is_coinbase() or not tx.is_final():
                            continue
                        # Transaction fee requirements, mainly only needed for flood control
                        # Under 10K (about 80 inputs) is free for first 100 transactions
                        # Base rate is 0.01 per KB
                        min_fee = tx.get_min_fee(len(block.l_tx) < 100)  # 100 个交易内的打折，之后的不打折
                        tmp_test_pool = copy.deepcopy(test_pool)  # 防止下面执行出错对test_pool产生干扰
                        ret = tx.connect_inputs(txdb, tmp_test_pool, Tx.PyDiskTxPos(1, 1, 1), 0, False, True, min_fee)
                        if ret is None:
                            continue
                        fees += ret  # 累积交易费
                        test_pool = tmp_test_pool

                        block.l_tx.append(tx)
                        block_size += tx.serialize_size(serialize.SerType.SER_NETWORK)
                        flag_already_added[n] = True
                        found_something = True  # 这是为了跳出外层 while
                        n += 1
                        # end for
                        pass
                    pass  # end while
                txdb.close()
                pass
        # end critical_block
        pass
        block.bits = bits
        block.l_tx[0].l_out[0].value = block.get_block_value(fees)
        print ("\n\nRunning Miner with %d transactions in block" % len(block.l_tx))

        # Prebuild hash buffer
        class Unnamed1(serialize.Serializable):
            class Unnamed2(serialize.Serializable):
                def __init__(self):
                    self.version = 0
                    self.hash_prev_block = 0
                    self.hash_merkle_root = 0
                    self.time = 0
                    self.bits = 0
                    self.nonce = 0

                def serialize(self, nType=0, nVersion=cfg.VERSION):
                    s = b''
                    s += serialize.ser_int(self.version)
                    s += serialize.ser_uint256(self.hash_prev_block)
                    s += serialize.ser_uint256(self.hash_merkle_root)
                    s += serialize.ser_uint(self.time)
                    s += serialize.ser_uint(self.bits)
                    s += serialize.ser_uint(self.nonce)
                    return s

            def __init__(self):
                self.block = Unnamed1.Unnamed2()
                self.padding0 = ['\x00'] * 64
                self.hash1 = 0
                self.padding1 = ['\x00'] * 64

        tmp = Unnamed1()
        tmp.block.version = block.version
        tmp.block.hash_prev_block = block.hash_prev_block = (index_prev.get_block_hash() if index_prev else 0)
        tmp.block.hash_merkle_root = block.hash_merkle_root = block.build_merkle_tree()
        tmp.block.time = block.time = max((index_prev.get_median_time_past() + 1 if index_prev else 0),
                                          timeutil.get_adjusted_time())
        tmp.block.bits = block.bits = bits  # difficulty
        tmp.block.nonce = block.nonce = 1  # 从1 开始计算

        # blocks0 = format_hash_blocks(tmp.block.serialize(), tmp.padding0)
        # blocks1 = format_hash_blocks(serialize.ser_uint256(tmp.hash1), tmp.padding1)

        # search
        start = timeutil.get_time()
        block_hash = 0
        hash_target = BN.PyBigNum.set_compact(block.bits).get_uint256()

        while True:
            if t.exit:
                break
            # use local sha256
            block_hash = cryptoutil.Hash(tmp.block.serialize())

            if block_hash <= hash_target:
                block.nonce = tmp.block.nonce
                assert block_hash == block.get_hash()
                # debug print
                print ("Miner:")
                print ("proof-of-work found  \n  hash: %s  \ntarget: %s\n" % (serialize.hexser_uint256(block_hash),
                                                                              serialize.hexser_uint256(hash_target)))
                print str(block)

                # TODO  setthreadpriority  THREAD_PRIORITY_NORMAL
                with ctx.mainLock:
                    # save key
                    kaction.add_key(key)

                    key.make_new_key()
                    # Process this block the same as if we had received it from another node
                    if not blkaction.process_block(None, block):
                        print ("ERROR in CoinMiner, ProcessBlock, block not accepted")
                    else:
                        print ("miner a block, waiting for relay")

                # TODO ADD THREAD_PRIORITY_LOWEST
                timeutil.sleep_msec(500)
                break

            # Update nTime every few seconds
            tmp.block.nonce += 1
            if tmp.block.nonce & 0x3FFFF == 0:
                # checkforshutdown
                if tmp.block.nonce == 0:
                    break
                if id(index_prev) != id(ctx.indexBest):
                    break
                if ctx.transactionsUpdated != transactions_updated_last and (timeutil.get_time() - start > 60):
                    break
                if not ctx.fGenerateCoins:
                    break
                tmp.block.time = block.time = max((index_prev.get_median_time_past() + 1), timeutil.get_adjusted_time())
            pass  # end nonce loop
        pass  # end whole loop
    return True


SHA256InitState = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]


def main():
    pass


if __name__ == '__main__':
    main()

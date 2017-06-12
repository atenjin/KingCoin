#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

from app import context as ctx, config as cfg
from app.net import net, base, action as netaction
from app.utils import timeutil, baseutil
from app.block.key import action as keyaction
from app.block.tx import tx as Tx, script
from app.block import block as Block, txaction, action as blockaction
from app.base import serialize
from app.market import market


def already_have(txdb, inv):
    """

    :param txdb:
    :type txdb: Tx.PyTxDB
    :param inv:
    :type inv: net.PyInv
    :return:
    """
    t = inv.msg_type
    if t == net.MsgType.MSG_TX:
        return inv.msg_hash in ctx.dictTransactions or txdb.contains_tx(inv.msg_hash)
    elif t == net.MsgType.MSG_BLOCK:
        return inv.msg_hash in ctx.dictBlockIndex or inv.msg_hash in ctx.dictOrphanBlocks
    elif t == net.MsgType.MSG_REVIEW:
        return True
    elif t == net.MsgType.MSG_PRODUCT:
        return inv.msg_hash in ctx.dictProducts
    return True


def process_messages(node_from, t):  # 注意是 messages
    """

    :param node_from:
    :type node_from: net.PyNode
    :param t:
    :type t: ExitedThread
    :return:
    """
    recv = node_from.recv
    if len(recv) == 0:
        return True
    print ("ProcessMessages(%d bytes)" % len(recv))
    #
    # Message format
    #  (4) message start
    #  (12) command
    #  (4) size
    #  (x) data
    #
    while True:
        if ctx.fShutdown:
            return True

        # Scan for message start
        s = recv.unread_str()
        start = s.find(cfg.MESSAGE_START)
        if start == -1:  # not found
            start = recv.end_index()
        else:
            start += recv.tell()
        if recv.end_index() - start < net.PYMESSAGEHADER_SIZE:
            if len(recv) > net.PYMESSAGEHADER_SIZE:
                print ("\n\nPROCESSMESSAGE MESSAGESTART NOT FOUND\n")
                recv.erase(recv.begin_index(), recv.end_index() - net.PYMESSAGEHADER_SIZE)
            break
        if start - recv.begin_index() > 0:
            print ("\n\nPROCESSMESSAGE SKIPPED %d BYTES\n" % (start - recv.begin_index()))
        recv.erase(recv.begin_index(), start)  # 0, 0

        recv_copy = recv.copy()
        # read header
        hdr = recv.stream_out(cls=net.PyMessageHeader)
        if not hdr.is_valid():
            print ("\n\nPROCESSMESSAGE: ERRORS IN HEADER %s\n\n" % hdr.get_command())
            timeutil.sleep_msec(1000)
            continue
        command = hdr.get_command()

        # message size
        message_size = hdr.message_size
        if message_size > len(recv):
            # Rewind and wait for rest of message
            print ("MESSAGE-BREAK 2\n")
            node_from.recv = recv_copy  # recover
            timeutil.sleep_msec(100)
            break
        # Copy message to its own buffer
        msg = serialize.PyDataStream(s=recv.raw_read_buf(recv.begin_index(), message_size), nType=recv.nType,
                                     nVersion=recv.nVersion)
        recv.ignore(message_size)

        # Process message
        ret = False
        try:
            t.check_self_shutdown()
            with ctx.mainLock:
                ret = process_message(node_from, command, msg)
            # print 'debug sleep'
            # timeutil.sleep_msec(1000)
            # print 'debug sleep'
            t.check_self_shutdown()
        except Exception, e:
            print (str(e))
            print ("ProcessMessage()")
            traceback.print_exc()
        if not ret:
            print ("ProcessMessage(%s, %d bytes) from %s to %s FAILED" % (command, message_size,
                                                                          str(node_from.addr), str(net.addrLocalHost)))
        node_from.recv.compact()
    return True


dictReuseKey = dict()  # dict<uint, list<uchar>>


def process_message(node_from, command, recv):
    """

    :param node_from:
    :type node_from: net.PyNode
    :param command:
    :param recv:
    :type recv: serialize.PyDataStream
    :return:
    :rtype bool
    """
    global dictReuseKey
    print ("received: %-12s (%d bytes)  " % (command, len(recv)))
    buf = list()
    for i in range(min(len(recv), 25)):
        buf.append("%02x " % (bytearray(recv[i])[0] & 0xff))
    print "".join(buf)
    print ("")
    if ctx.dropMessagesTest > 0 and baseutil.get_rand(ctx.dropMessagesTest) == 0:  # 这难吧··
        print ("dropmessages DROPPING RECV MESSAGE\n")  # 应该是模拟随机丢弃消息
        return True

    if command == base.COMMAND_VERSION:
        # Can only do this once
        if node_from.nVersion != 0:
            return False
        node_from.nVersion = recv.stream_out(out_type="int")  # int
        node_from.services = recv.stream_out(out_type="uint64")  # uint64
        time = recv.stream_out(out_type="int64")  # int64
        addr_me = recv.stream_out(cls=net.PyAddress)
        if node_from.nVersion == 0:
            return False

        node_from.send.nVersion = min(node_from.nVersion, cfg.VERSION)
        node_from.recv.nVersion = min(node_from.nVersion, cfg.VERSION)

        node_from.f_client = not (node_from.services & cfg.NODE_NETWORK)
        if node_from.f_client:
            node_from.send.nType |= serialize.SerType.SER_BLOCKHEADERONLY
            node_from.recv.nType |= serialize.SerType.SER_BLOCKHEADERONLY

        timeutil.add_time_data(node_from.addr.ip, time)

        # Ask the first connected node for block updates
        global fAskedForBlocks
        if not fAskedForBlocks and not node_from.f_client:
            fAskedForBlocks = True
            node_from.push_message(base.COMMAND_GETBLOCKS,
                                   Block.PyBlockLocator(ctx.indexBest), (0, "uint256"))
        print ("version addrMe = %s\n" % str(addr_me))
    elif node_from.nVersion == 0:
        # Must have a version message before anything else
        return False
    elif command == base.COMMAND_ADDR:
        list_addr = recv.stream_out(out_type="list", cls=net.PyAddress)  # list<PyAddress>
        # Store the new addresses
        addrdb = net.PyAddrDB()
        for addr in list_addr:
            if ctx.fShutdown:
                return True
            if net.add_address(addrdb, addr):
                # Put on lists to send to other nodes
                node_from.set_addr_known.add(addr)
                with ctx.listNodesLock:
                    if addr not in node_from.set_addr_known:
                        node_from.list_addr_to_send.append(addr)
        addrdb.close()
    elif command == base.COMMAND_INV:
        list_inv = recv.stream_out("list", net.PyInv)
        txdb = Tx.PyTxDB("r")
        for inv in list_inv:
            if ctx.fShutdown:
                return True
            node_from.add_inventory_known(inv)

            f_already_have = already_have(txdb, inv)
            print ("  got inventory: %s  %s\n" % (str(inv), "have" if f_already_have else "new"))

            if not f_already_have:
                node_from.ask_for(inv)
            elif inv.msg_type == net.MsgType.MSG_BLOCK and inv.msg_hash in ctx.dictOrphanBlocks:
                node_from.push_message(base.COMMAND_GETBLOCKS,
                                       Block.PyBlockLocator(ctx.indexBest),
                                       (Block.get_orphan_root(ctx.dictOrphanBlocks[inv.msg_hash]), "uint256"))
        txdb.close()
    elif command == base.COMMAND_GETDATA:
        list_inv = recv.stream_out("list", net.PyInv)
        for inv in list_inv:
            if ctx.fShutdown:
                return True
            print ("received getdata for: %s\n" % str(inv))

            if inv.msg_type == net.MsgType.MSG_BLOCK:
                # Send block from disk
                block_index = ctx.dictBlockIndex.get(inv.msg_hash, None)
                if block_index is not None:
                    ## could optimize this to send header straight from blockindex for client
                    block = Block.PyBlock()
                    block.read_from_disk(block_index, read_txs=(not node_from.f_client))  # index, block_pos=0
                    node_from.push_message(base.COMMAND_BLOCK, block)
            elif inv.is_known_type():
                #  Send stream from relay memory
                with ctx.dictRelayLock:
                    data = ctx.dictRelay.get(inv, None)  # data:PyDataStream
                    if data is not None:
                        node_from.push_message(inv.get_command(), data)
    elif command == base.COMMAND_GETBLOCKS:
        locator = recv.stream_out(cls=Block.PyBlockLocator)
        hash_stop = recv.stream_out(out_type="uint256")

        # Find the first block the caller has in the main chain
        index = locator.get_block_index()

        # Send the rest of the chain
        if index:
            index = index.next_index

        print ("getblocks %d to %s\n" %
               (index.height if index else -1, serialize.hexser_uint256(hash_stop)[:14]))

        while index:
            if index.get_block_hash() == hash_stop:
                print ("  getblocks stopping at %d %s" % (index.height, index.get_block_hash(output_type='hex')[:14]))
                break

            # Bypass setInventoryKnown in case an inventory message got lost
            with node_from.inventory_lock:
                inv = net.PyInv(net.MsgType.MSG_BLOCK, index.get_block_hash())

                if inv not in node_from.set_inventory_know2:
                    node_from.set_inventory_know2.add(inv)
                    node_from.set_inventory_know.discard(inv)  # not throw exception
                    node_from.list_inventory_to_send.append(inv)

            index = index.next_index
            pass  # end loop
    elif command == base.COMMAND_TX:
        list_work_queue = list()  # hash256 list
        msg = recv.copy()
        tx = recv.stream_out(cls=Tx.PyTransaction)

        inv = net.PyInv(net.MsgType.MSG_TX, tx.get_hash())
        node_from.add_inventory_known(inv)

        f_missing_inputs = [False]
        if tx.accept_transaction(check_inputs=True, missing_inputs=f_missing_inputs):
            Block.add_to_wallet_if_mine(tx, None)
            netaction.relay_message(inv, msg)
            ctx.dictAlreadyAskedFor.pop(inv, None)  # delete from dict
            list_work_queue.append(inv.msg_hash)

            # Recursively process any orphan transactions that depended on this one
            for hash_prev in iter(list_work_queue):
                for msg in ctx.dictOrphanBlocksByPrev[hash_prev]:  # list<PyDataStrem>
                    tx = msg.stream_out(cls=Tx.PyTransaction)
                    inv = net.PyInv(net.MsgType.MSG_TX, tx.get_hash())

                    if tx.accept_transaction(check_inputs=True):
                        print ("   accepted orphan tx %s" % serialize.hexser_uint256(inv.msg_hash))
                        Block.add_to_wallet_if_mine(tx, None)
                        netaction.relay_message(inv, msg)
                        ctx.dictAlreadyAskedFor.pop(inv, None)  # delete from dict
                        list_work_queue.append(inv.msg_hash)
                pass  # end for list_work_queue loop
            for tx_hash in list_work_queue:
                txaction.erase_orphan_tx(tx_hash)
        elif f_missing_inputs[0]:  # f_missing_inputs will chang in accept_transaction()
            print ("storing orphan tx %s" % serialize.hexser_uint256(inv.msg_hash)[:6])
            txaction.add_orphan_tx(msg)
    elif command == base.COMMAND_REVIEW:
        msg = recv.copy()
        review = recv.stream_out(cls=market.PyReview)

        inv = net.PyInv(net.MsgType.MSG_REVIEW, review.get_hash())
        node_from.add_inventory_known(inv)

        if review.accept_review():
            # Relay the original message as-is in case it's a higher version than we know how to parse
            netaction.relay_message(inv, msg)
            ctx.dictAlreadyAskedFor.pop(inv, None)  # del from dict
    elif command == base.COMMAND_BLOCK:
        block = recv.stream_out(cls=Block.PyBlock)
        ## debug print
        print ("received block: \n%s" % str(block))

        inv = net.PyInv(net.MsgType.MSG_BLOCK, block.get_hash())
        node_from.add_inventory_known(inv)

        if blockaction.process_block(node_from, block):
            ctx.dictAlreadyAskedFor.pop(inv, None)
    elif command == base.COMMAND_GETADDR:
        node_from.list_addr_to_send = list()
        ## need to expand the time range if not enough found
        since = timeutil.get_adjusted_time() - cfg.COMMAND_GETADDR_SPAN_TIME  # in the last hour
        with ctx.dictAddressesLock:
            for addr in iter(ctx.dictAddresses.itervalues()):
                if ctx.fShutdown:
                    return
                if addr.time > since:
                    node_from.list_addr_to_send.append(addr)
    elif command == base.COMMAND_CHECKORDER:
        hash_reply = recv.stream_out(out_type="uint256")
        order = recv.stream_out(cls=Block.PyWalletTx)
        # todo: we have a chance to check the order here
        #
        # Keep giving the same key to the same ip until they use it
        if node_from.addr.ip is not dictReuseKey:
            dictReuseKey[node_from.addr.ip] = keyaction.generate_new_key()  # generate pubkey : str

        # Send back approval of order and pubkey to use
        script_pubkey = script.PyScript()
        script_pubkey.extend(dictReuseKey[node_from.addr.ip]).append(script.OpCodeType.OP_CHECKSIG)
        node_from.push_message(base.COMMAND_REPLY, (hash_reply, "uint256"), (0, "int"),
                               (script_pubkey.get_str(), "str"))
    elif command == base.COMMAND_SUBMITORDER:
        hash_reply = recv.stream_out(out_type="uint256")
        wtx_new = recv.stream_out(cls=Block.PyWalletTx)

        # Broadcast
        if not wtx_new.accept_wallet_transaction():
            node_from.push_message(base.COMMAND_REPLY, (hash_reply, "uint256"), (1, "int"))
            print ("submitorder AcceptWalletTransaction() failed, returning error 1")
            return False
        wtx_new.time_received_is_tx_time = 1
        Block.add_to_wallet(wtx_new)
        wtx_new.relay_wallet_transaction()
        dictReuseKey.pop(node_from.addr.ip, None)

        # Send back confirmation
        node_from.push_message(base.COMMAND_REPLY, (hash_reply, "uint256"), (0, "int"))
    elif command == base.COMMAND_REPLY:
        hash_reply = recv.stream_out(out_type="uint256")
        # code_reply = recv.stream_out(out_type="int")
        with node_from.dict_requests_lock:
            tracker = node_from.dict_requests.get(hash_reply, None)
            if tracker is not None:
                tracker.func(tracker.param, recv)  # recv contain code_reply(0 or 1)
    else:
        #  Ignore unknown commands for extensibility
        print ("ProcessMessage(%s) : Ignored unknown message" % command)

    if len(recv) != 0:
        print ("ProcessMessage(%s) : %d extra bytes" % (command, len(recv)))
    return True


fAskedForBlocks = False


def send_messages(node_to, t, ignore=False):
    """

    :param node_to:
    :type node_to: net.PyNode
    :param t:
    :type t: ExitedThread
    :return:
    """
    t.check_self_shutdown()
    with ctx.mainLock:
        #  Don't send anything until we get their version message
        if node_to.nVersion == 0:
            return True

        # Message: addr
        list_addr_to_send = [addr for addr in node_to.list_addr_to_send if addr not in node_to.set_addr_known]
        del node_to.list_addr_to_send[:]
        if list_addr_to_send:
            node_to.push_message(base.COMMAND_ADDR, list_addr_to_send, ignore=ignore)

        # Message: inventory
        list_inventory_to_send = list()
        with node_to.inventory_lock:
            for inv in node_to.list_inventory_to_send:
                if inv not in node_to.set_inventory_know:
                    node_to.set_inventory_know.add(inv)
                    list_inventory_to_send.append(inv)

            del node_to.list_inventory_to_send[:]  # clear element in node.list_inventory_to_send, not local var
            node_to.set_inventory_know2.clear()  # 注意这里clear的是 2

        if list_inventory_to_send:
            node_to.push_message(base.COMMAND_INV, list_inventory_to_send, ignore=ignore)

        # Message: getdata
        now = timeutil.get_time() * 1000000  # usec
        txdb = Tx.PyTxDB("r")
        list_ask_for = list()
        dict_ask_for = node_to.dict_ask_for.items()  # node_to.dict_ask_for is dict
        dict_ask_for.sort(key=lambda x: x[0])  # sort by key(time:int64)
        for time, invs in dict_ask_for:
            if time > now:
                break
            for inv in invs:
                print ("sending getdata: %s" % str(inv))
                if not already_have(txdb, inv):
                    list_ask_for.append(inv)
            node_to.dict_ask_for.pop(time, None)
        if list_ask_for:
            node_to.push_message(base.COMMAND_GETDATA, list_ask_for, ignore=ignore)

        txdb.close()
        pass  # end end critical
    return True


def main():
    pass


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import socket
import collections
import select
import traceback

from app import context as ctx, config as cfg
from app.base import ui
from app.utils import baseutil, timeutil
from app.net import base as netbase, net, message, action as netaction
from app.block import miner


def check_for_shutdown(t):
    """

    :param t:
    :type t: ExitedThread
    :return:
    """
    n = t.n
    if ctx.fShutdown:
        if n != -1:
            ctx.listfThreadRunning[n] = False
            t.exit = True


class ExitedThread(threading.Thread):
    def __init__(self, arg, n):
        super(ExitedThread, self).__init__()
        self.exit = False
        self.arg = arg
        self.n = n

    def run(self):
        self.thread_handler(self.arg, self.n)
        pass

    def thread_handler(self, arg, n):
        # global LoopsNum
        # if LoopsNum <= 0:
        #     if LoopsNum <= 0:
        #         LoopsNum = baseutil.get_rand(5)
        #         self.thread_handler(arg, n)
        #         return
        while True:
            check_for_shutdown(self)
            if self.exit:
                break
            ctx.listfThreadRunning[n] = True
            try:
                self.thread_handler2(arg)
            except Exception, e:
                print ("ThreadSocketHandler()")
                print (e)
                traceback.print_exc()
            ctx.listfThreadRunning[n] = False

            timeutil.sleep_msec(5000)
            pass

    def thread_handler2(self, arg):
        raise NotImplementedError("must impl this func")

    def check_self_shutdown(self):
        check_for_shutdown(self)

    def try_exit(self):
        self.exit = True
        ctx.listfThreadRunning[self.n] = False
        pass

    pass


LoopsNum = 0


class SocketThread(ExitedThread):
    def __init__(self, arg):
        super(SocketThread, self).__init__(arg, n=0)

    def thread_handler2(self, arg):
        self.thread_socket_handler2(arg)

    def thread_socket_handler2(self, hlisten_socket):
        print ("ThreadSocketHandler started")
        list_nodes_disconnected = list()  # list<PyNode>
        prev_node_count = 0
        while True:  # this is a dead loop
            if self.exit:
                break
            #
            # Disconnect nodes
            #
            with ctx.listNodesLock:
                # Disconnect duplicate connections
                dict_first = dict()  # dict<str(ip), PyNode>
                for node in ctx.listNodes:
                    if node.f_disconnect:
                        continue
                    ip = node.addr.ip
                    node_extra = dict_first.get(ip, None)
                    if (node_extra is not None) and netbase.ip2uint(ip) > netbase.ip2uint(net.addrLocalHost.ip):
                        # In case two nodes connect to each other at once,
                        # the lower ip disconnects its outbound connection
                        if node_extra.get_ref_count() > (1 if node_extra.f_network_node else 0):
                            node_extra, node = node, node_extra  # swap
                        if node_extra.get_ref_count() <= (1 if node_extra.f_network_node else 0):
                            print (
                                "(%d nodes) disconnecting duplicate: %s" % (len(ctx.listNodes), str(node_extra.addr)))
                            if node_extra.f_network_node and not node.f_network_node:
                                node.add_ref()
                                # swap
                                node_extra.f_network_node, node.f_network_node = node.f_network_node, node_extra.f_network_node
                                node_extra.release()
                            node_extra.f_disconnect = True
                    dict_first[ip] = node

                # Disconnect unused nodes
                list_nodes_copy = ctx.listNodes[:]  # copy
                for node in list_nodes_copy:
                    if node.ready_to_disconnect() and len(node.recv) == 0 and len(node.send) == 0:
                        # remove from vNodes
                        ctx.listNodes.remove(node)
                        node.disconnect()

                        # hold in disconnected pool until all refs are released
                        node.release_time = max(node.release_time, timeutil.get_time() + 5 * 60)  # 5 min
                        if node.f_network_node:
                            node.release()
                        list_nodes_disconnected.append(node)
                pass

                # Delete disconnected nodes
                list_nodes_disconnected_copy = list_nodes_disconnected[:]
                for node in list_nodes_disconnected_copy:
                    # wait until threads are done using it
                    if node.get_ref_count() <= 0:
                        f_delete = False
                        if not node.send_lock.locked():
                            with node.send_lock:
                                if not node.recv_lock.locked():
                                    with node.recv_lock:
                                        if not node.dict_requests_lock.locked():
                                            with node.dict_requests_lock:
                                                if not node.inventory_lock.locked():
                                                    with node.inventory_lock:
                                                        f_delete = True
                        if f_delete:
                            list_nodes_disconnected.remove(node)
                            del node  # release node obj
                    pass
                pass
            pass  # end with critical
            if len(ctx.listNodes) != prev_node_count:  # prev_node_count init is 0
                prev_node_count = len(ctx.listNodes)
                # TODO 检查跨线程是否有效
                ui.mainframe_repaint()
            pass  # end if

            #
            # Find which sockets have data to receive
            #
            set_recv = set()
            set_send = set()
            set_recv.add(hlisten_socket)
            # hsocket_max = listen_socket
            with ctx.listNodesLock:
                for node in ctx.listNodes:
                    set_recv.add(node.hsocket)
                    # hsocket_max = max(hsocket_max, node.hsocket)
                    if not node.send_lock.locked():
                        with node.send_lock:
                            if len(node.send) != 0:
                                set_send.add(node.hsocket)

            ctx.listfThreadRunning[self.n] = False

            recv_readable, send_writable, exceptional = select.select(set_recv, set_send, set_recv,
                                                                      1)  # timeout = 1  source code is 0.05

            ctx.listfThreadRunning[self.n] = True
            check_for_shutdown(self)
            if self.exit:
                break

            ## debug print
            # for node in ctx.listNodes:
            #     print ("list_recv = %-5d" % len(node.recv))            #     print ("list_send = %-5d" % len(node.send))
            # print ("")

            #
            # Accept new connections
            #
            if hlisten_socket in recv_readable:
                hsocket, addr = hlisten_socket.accept()
                pyaddr = net.PyAddress(addr[0], addr[1])

                print "accepted connection from %s" % str(pyaddr)
                hsocket.setblocking(False)
                node = net.PyNode(hsocket, pyaddr, True)
                node.add_ref()
                with ctx.listNodesLock:
                    ctx.listNodes.append(node)

            #
            # Service each socket
            #
            with ctx.listNodesLock:
                list_nodes_copy = ctx.listNodes[:]
            for node in list_nodes_copy:
                check_for_shutdown(self)
                if self.exit:
                    break
                hsocket = node.hsocket

                # Receive
                if hsocket in recv_readable:
                    if not node.recv_lock.locked():
                        with node.recv_lock:
                            # typical socket buffer is 8K-64K
                            buf_size = 0x10000
                            d = ''
                            try:
                                d = hsocket.recv(buf_size)
                                if d:
                                    node.recv.write(d)
                                else:
                                    if not node.f_disconnect:
                                        print ("recv: socket closed")
                                    node.f_disconnect = True
                            except socket.errno:
                                # socket closed gracefully
                                if not node.f_disconnect:
                                    print ("recv: socket closed")
                                node.f_disconnect = True
                            except Exception, e:
                                print (e)
                                traceback.print_exc()
                                if not node.f_disconnect:
                                    print ("recv: socket failed")
                                node.f_disconnect = True
                    pass  # end lock
                pass  # end if for receive
                # send
                if hsocket in send_writable:
                    if not node.send_lock.locked():
                        with node.send_lock:
                            size = len(node.send)
                            if size != 0:
                                send_data = node.send[0:]
                                nbytes = hsocket.send(send_data)
                                if nbytes > 0:
                                    start = node.send.begin_index()
                                    node.send.erase(start, start + nbytes)
                                elif nbytes == 0:
                                    if node.ready_to_disconnect():
                                        node.send.clear()
                                else:
                                    print ("send error %d:" % nbytes)
                                    if node.ready_to_disconnect():
                                        node.send.clear()
                            pass  # end lock
                if hsocket in exceptional:
                    print ("node.hsocket: socket closed or something wrong, try to close this node")
                    node.f_disconnect = True
                    with node.recv_lock:
                        node.recv.clear()
                    with node.send_lock:
                        node.send.clear()
                pass  # end if for send
            pass  # end for receive and send for listnodes

            timeutil.sleep_msec(10)

        for node in ctx.listNodes:
            node.disconnect()
        del ctx.listNodes[:]
        pass  # end loop

    pass  # end SocketThread class


class OpenConnectionsThread(ExitedThread):
    def __init__(self, arg=None):
        super(OpenConnectionsThread, self).__init__(arg, n=1)

    def thread_handler2(self, arg):
        self.thread_open_connections2(arg)

    def thread_open_connections2(self, arg):
        """

        :param arg:  arg is useless
        :return:
        """
        print ("ThreadOpenConnections started")

        # Initiate network connections
        max_connections = cfg.MAX_CONNECTIONS  # 一直保持不超过15个节点的连接
        while True:
            if self.exit:
                break

            ctx.listfThreadRunning[self.n] = False
            timeutil.sleep_msec(500)
            while len(ctx.listNodes) >= max_connections or len(ctx.listNodes) >= len(ctx.dictAddresses):
                check_for_shutdown(self)
                if self.exit:
                    return True
                timeutil.sleep_msec(2000)  # 手动sleep ...

            ctx.listfThreadRunning[self.n] = True
            check_for_shutdown(self)
            if self.exit:
                break
            # Make a list of unique class C's
            ip_C_mask = 0xFFFFFF00  # 0x00FFFFFF  C类ip 掩码 0xffffff00
            list_ip_C = list()
            with ctx.dictAddressesLock:
                prev = 0
                dict_addrs = ctx.dictAddresses.items()
                dict_addrs.sort(key=lambda item: netbase.ip2uint(item[1].ip))  # 对持有的ip进行排序
                for _, addr in dict_addrs:
                    if not addr.is_ipv4():
                        continue
                    ip_C = netbase.ip2uint(addr.ip) & ip_C_mask
                    if ip_C != prev:
                        prev = ip_C
                        list_ip_C.append(ip_C)
            #
            # The IP selection process is designed to limit vulnerability to address flooding.
            # Any class C (a.b.c.?) has an equal chance of being chosen, then an IP is
            # chosen within the class C.  An attacker may be able to allocate many IPs, but
            # they would normally be concentrated in blocks of class C's.  They can hog the
            # attention within their class C, but not the whole IP address space overall.
            # A lone node in a class C will get as much attention as someone holding all 255
            # IPs in another class C.
            #
            f_success = False
            limit = len(list_ip_C)
            while not f_success and limit > 0:
                limit -= 1
                # Choose a random class C
                ip_C = list_ip_C[int(baseutil.get_rand(len(list_ip_C)))]
                # Organize all addresses in the class C by IP
                dict_IP = collections.defaultdict(list)
                with ctx.dictAddressesLock:
                    delay = (30 * 60) << len(ctx.listNodes)
                    if delay > 8 * 60 * 60:
                        delay = 8 * 60 * 60
                    lower = net.PyAddress(netbase.uint2ip(ip_C), 0).get_key()
                    upper = net.PyAddress(netbase.uint2ip(ip_C | (0xffffffff - ip_C_mask)), 0xFFFF).get_key()
                    for key, addr in dict_addrs:
                        if key < lower:
                            continue
                        if key > upper:
                            break
                        randomizer = addr.last_failed * netbase.ip2uint(addr.ip) * 7777 % 20000
                        if timeutil.get_time() - addr.last_failed > delay * randomizer / 10000:
                            dict_IP[addr.ip].append(addr)
                    pass  # end critical block
                if len(dict_IP) == 0:
                    break  # jump out loop
                # Choose a random IP in the class C
                keyiter = dict_IP.iterkeys()
                key = next(keyiter)
                for _ in range(baseutil.get_rand(len(dict_IP) - 1)):
                    key = next(keyiter)
                for addr_conn in dict_IP[key]:  # value is a list for addrs
                    if addr_conn.ip == net.addrLocalHost.ip or not addr_conn.is_ipv4() or \
                            netaction.find_node(addr_conn.ip):
                        continue
                    node = netaction.connect_node(addr_conn)
                    if node is None:
                        continue
                    node.f_network_node = True
                    if net.addrLocalHost.is_routable():
                        # Advertise our address
                        list_addr_to_send = [net.addrLocalHost]
                        node.push_message(netbase.COMMAND_ADDR, (list_addr_to_send, "list"))

                    # Get as many addresses as we can
                    node.push_message(netbase.COMMAND_GETADDR)

                    #  Subscribe our local subscription list
                    hops = 0
                    for channel in ctx.nodeLocalHost.listf_subscribe:
                        if channel:
                            node.push_message(netbase.COMMAND_SUBSCRIBE, (channel, "uint"), (hops, "uint"))
                    f_success = True
                    break
                    pass  # end for in ips
                pass  # end while for check f_success
            pass  # no possible to jump this dead loop unless raise any exception

    pass  # end OpenConnectionsThread class


class MessageThread(ExitedThread):
    def __init__(self, arg=None):
        super(MessageThread, self).__init__(arg, n=2)

    def thread_handler2(self, arg):
        self.thread_message_handler2(arg)

    def thread_message_handler2(self, arg):
        print ("ThreadMessageHandler started")
        # TODO set thread priority THREAD_PRIORITY_BELOW_NORMAL
        while True:
            if self.exit:
                break
            # Poll the connected nodes for messages
            with ctx.listNodesLock:
                list_nodes_copy = ctx.listNodes[:]
            for node in list_nodes_copy:
                node.add_ref()

                # Receive messages
                if not node.recv_lock.locked():
                    with node.recv_lock:
                        message.process_messages(node, self)
                # Send messages
                if not node.send_lock.locked():
                    with node.send_lock:
                        message.send_messages(node, self, ignore=True)
                node.release()

            # Wait and allow messages to bunch up
            ctx.listfThreadRunning[self.n] = False
            timeutil.sleep_msec(1000)
            ctx.listfThreadRunning[self.n] = True
            check_for_shutdown(self)
            if self.exit:
                break
            pass  # end dead loop
        pass

    pass  # end MessageThread class


class CoinMinerThread(ExitedThread):
    def __init__(self, arg=None):
        super(CoinMinerThread, self).__init__(arg, n=3)

    def thread_handler2(self, arg):
        self.thread_bitcoin_miner(arg)

    def thread_bitcoin_miner(self, arg):
        ctx.listfThreadRunning[self.n] = True
        check_for_shutdown(self)
        try:
            ret = miner.bitcoin_miner(self)
            print ("Miner returned %s\n\n" % "true" if ret else"false")
        except Exception, e:
            print ("Miner()")
            print (e)
            traceback.print_exc()
        ctx.listfThreadRunning[self.n] = False

    pass  # end BitcoinMinerThread class


def main():
    pass


if __name__ == '__main__':
    main()

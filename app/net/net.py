#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import socket
import threading
from collections import defaultdict

from app import context as ctx
from app.base.serialize import *
from app.net import base
from app.utils import timeutil, baseutil
from app.market import action as mkaction
from app.db import db, dbserialize

IPv4 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff'


class MsgType(IntEnum):
    MSG_TX = 1  # start from 1  and 0 mark to "ERROR"
    MSG_BLOCK = 2
    MSG_REVIEW = 3
    MSG_PRODUCT = 4
    MSG_TABLE = 5


TypeNameList = ["ERROR", "tx", "block", "review", "product", "table"]
TypeName = {TypeNameList[0]: 0,
            TypeNameList[1]: MsgType.MSG_TX,
            TypeNameList[2]: MsgType.MSG_BLOCK,
            TypeNameList[3]: MsgType.MSG_REVIEW,
            TypeNameList[4]: MsgType.MSG_PRODUCT,
            TypeNameList[5]: MsgType.MSG_TABLE}

PYMESSAGEHADER_SIZE = 20


class PyMessageHeader(Serializable):
    def __init__(self, command=None, message_size=0xFFFFFFFF):
        self.message_start = cfg.MESSAGE_START
        if command is None:
            self.command = bytearray(cfg.MESSAGE_HEADER_COMMAND_SIZE)
            self.command[1] = b'\x01'
        else:
            self.command = command[: cfg.MESSAGE_HEADER_COMMAND_SIZE]
        self.message_size = message_size  # uint default is unsigned int (-1)

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        s = StringIO()
        s.write(ser_flatdata(self.message_start, len(cfg.MESSAGE_START)))
        s.write(ser_flatdata(str(self.command), cfg.MESSAGE_HEADER_COMMAND_SIZE))
        s.write(ser_uint(self.message_size))
        return s.getvalue()

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        f = wrap_to_StringIO(f)
        self.message_start = deser_flatdata(f, len(cfg.MESSAGE_START))
        self.command = bytearray(deser_flatdata(f, cfg.MESSAGE_HEADER_COMMAND_SIZE))
        self.message_size = deser_uint(f)
        return self

    def get_command(self):
        if self.command[cfg.MESSAGE_HEADER_COMMAND_SIZE - 1] == 0:
            return str(self.command[:self.command.index(b'\00')])
        else:
            return str(self.command)

    def is_valid(self):
        # Check start string
        if self.message_start != cfg.MESSAGE_START:
            return False
        # Must be all zeros after the first zero
        # if self.command.count('\x00') >= 2:
        #     return False

        # Check the command string for errors
        # for p in self.command:
        #     if p < 0x20 or p > 0x7E:  # prevent attacks
        #         return False
        for i, p in enumerate(self.command):
            if p == 0:
                if i + 1 > cfg.MESSAGE_SIZE:
                    break

                for p2 in self.command[i + 1:]:
                    if p2 != 0:
                        return False
                break
            elif p < 0x20 or p > 0x7E:  # prevent attacks
                return False

        # Message size
        if self.message_size > cfg.MESSAGE_SIZE:
            print "PyMessageHeader::IsValid() : nMessageSize too large %d" % self.message_size
            return False
        return True

    pass


class PyAddress(Serializable):
    def __init__(self, ip_in='0.0.0.0', port_in=cfg.DEFAULT_PORT, services_in=0):
        self.services = services_in
        self.reserved = IPv4
        if isinstance(ip_in, tuple):
            ip_in = ip_in[0]
            port_in = ip_in[1]

        self.ip = ip_in  # str  transform to int
        self.port = int(port_in)  # local type , transform to s
        # disk only
        self.time = timeutil.get_adjusted_time()
        # memory only
        self.last_failed = 0
        pass

    def get_ip(self, out=None):
        return base.ip2uint(self.ip) if out == 'uint' else self.ip

    def get_port(self, out='ushort'):
        return self.port if out == 'ushort' else str(self.port)

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        s = StringIO()
        if nType & SerType.SER_DISK:
            s.write(ser_int(nVersion))
            s.write(ser_uint(self.time))
        s.write(ser_uint64(self.services))
        s.write(ser_flatdata(self.reserved, len(IPv4)))
        s.write(ser_uint(base.ip2uint(self.ip)))
        s.write(ser_ushort(self.port))
        return s.getvalue()

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        f = wrap_to_StringIO(f)
        if nType & SerType.SER_DISK:
            nVersion = deser_int(f)
            self.time = deser_uint(f)
        self.services = deser_uint64(f)
        self.reserved = deser_flatdata(f, len(IPv4))
        self.ip = base.uint2ip(deser_uint(f))
        self.port = deser_ushort(f)
        return self

    def __eq__(self, other):
        return self.reserved == other.reserved and self.ip == other.ip and self.port == other.port

    def get_key(self):
        ss = PyDataStream()
        ss.stream_in(PyFlatData(self.reserved)). \
            stream_in(base.ip2uint(self.ip), in_type='uint'). \
            stream_in(self.port, in_type='ushort')
        return str(ss)

    def get_sockaddrinfo(self):
        return socket.getaddrinfo(self.ip, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)

    def get_sockaddr(self):
        return self.ip, self.port

    def is_ipv4(self):
        return str(self.reserved[:len(IPv4)]) == IPv4

    def get_byte(self, n):
        """
        ip = 192.168.1.2 => list = a[2,1,168,192], return int(a[n])
        :param n:
        :return:
        """
        ret = self.ip.split('.')
        if len(ret) != 4:
            raise RuntimeError("ip str parser error!")
        ret = ret[::-1]
        return int(ret[n])

    def is_routable(self):
        # byte3 = self.get_byte(3)
        # return not (byte3 == 10 or byte3 == 192 or self.get_byte(2) == 168)
        return True

    def __str__(self):
        return self.ip + ':' + str(self.port)

    pass


# inv => inventory
class PyInv(Serializable):
    def __init__(self, type_in=0, hash_in=0):
        """

        :param type_in:
        :type type_in: str | int | MsgType
        :param hash_in:  uint256
        """
        if type(type_in) == str:
            if not type_in in TypeName:
                raise KeyError("PyInv::PyInv(string, uint256) : unknown type %s" % type_in)
            self.msg_type = TypeName[type_in]
        self.msg_type = type_in
        self.msg_hash = hash_in
        pass

    def __hash__(self):
        return hash(self.serialize())

    def __eq__(self, other):
        return self.msg_type == other.msg_type and self.msg_hash == other.msg_hash

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        s = StringIO()
        s.write(ser_int(self.msg_type))
        s.write(ser_uint256(self.msg_hash))
        return s.getvalue()

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        f = wrap_to_StringIO(f)
        self.msg_type = deser_int(f)
        self.msg_hash = deser_uint256(f)
        return self

    def is_known_type(self):
        return MsgType.MSG_TX <= self.msg_type <= MsgType.MSG_TABLE

    def get_command(self):
        if not self.is_known_type():
            raise RuntimeError("PyInv::GetCommand() : type=%d unknown type" % self.msg_type)
        return TypeNameList[self.msg_type]

    def __str__(self):
        return "%s %s" % (self.get_command(), hexser_uint256(self.msg_hash)[:14])

    pass


class PyRequestTracker(object):
    def __init__(self, func=None, param_in=None):
        self.func = func  # func receive func(param, PyDataStrem)
        self.param = param_in

    def is_null(self):
        return self.func is None

    pass


class PyNode(object):
    lastTime = 0

    def __init__(self, socket_in, addr_in, f_inbound_in=False):
        """

        :param socket_in:
        :param addr_in:
        :type addr_in: PyAddress
        :param f_inbound_in:
        """
        self.services = 0  # uint64
        self.hsocket = socket_in
        self.send = PyDataStream(nType=SerType.SER_NETWORK)
        self.recv = PyDataStream(nType=SerType.SER_NETWORK)
        self.send_lock = threading.Lock()
        self.recv_lock = threading.Lock()
        self.push_pos = -1
        self.addr = addr_in
        self.nVersion = 0
        self.f_client = False
        self.f_inbound = f_inbound_in
        self.f_network_node = False
        self.f_disconnect = False
        self._ref_count = 0

        self.release_time = 0
        self.dict_requests = dict()
        self.dict_requests_lock = threading.Lock()

        # flood
        self.list_addr_to_send = list()  # list<PyAddress>
        self.set_addr_known = set()  # set<PyAddress>

        # inventory based relay
        self.set_inventory_know = set()  # set<PyInv>
        self.set_inventory_know2 = set()  # set<PyInv>
        self.list_inventory_to_send = list()  # list<PyInv>
        self.inventory_lock = threading.Lock()
        self.dict_ask_for = defaultdict(list)

        # publish and subscription
        self.listf_subscribe = [False] * 256  # list()  # list<bool>

        # Push a version message
        ## when NTP implemented, change to just nTime = GetAdjustedTime()
        time = timeutil.get_adjusted_time() if self.f_inbound else timeutil.get_time()
        self.push_message(base.COMMAND_VERSION,  # command
                          (cfg.VERSION, "int"), (ctx.localServices(), "uint64"),  # objs
                          (time, 'int64'), (self.addr, "Serializable"))  # objs
        pass

    def __del__(self):
        if self.hsocket is not None:
            try:
                self.hsocket.close()
            except socket.error as msg:
                print 'socket error!'
                print msg
            finally:
                self.hsocket = None
        pass

    def get_ref_count(self):
        return max(self._ref_count, 0) + (1 if timeutil.get_time() < self.release_time else 0)

    def ready_to_disconnect(self):
        return self.f_disconnect or self.get_ref_count() <= 0

    def add_ref(self, timeout=0):
        if timeout != 0:
            self.release_time = max(self.release_time, timeutil.get_time() + timeout)
        else:
            self._ref_count += 1

    def release(self):
        self._ref_count -= 1

    def add_inventory_known(self, inv):
        with self.inventory_lock:
            self.set_inventory_know.add(inv)

    def push_inventory(self, inv):
        with self.inventory_lock:
            if inv not in self.set_inventory_know:
                self.list_inventory_to_send.append(inv)

    def ask_for(self, inv):
        # We're using mapAskFor as a priority queue,
        # the key is the earliest time the request can be sent
        request_time = ctx.dictAlreadyAskedFor.pop(inv, 0)
        print ("askfor %s  %d" % (str(inv), request_time))
        # Make sure not to reuse time indexes to keep things in the same order
        PyNode.lastTime += 1
        now = max((timeutil.get_time() - 1) * 1000000, PyNode.lastTime)  # um
        PyNode.lastTime = now
        # Each retry is 2 minutes after the last
        request_time = max(request_time + 2 * 60 * 1000000, now)  # um 微秒
        self.dict_ask_for[request_time].append(inv)
        ctx.dictAlreadyAskedFor[inv] = request_time

    def begin_message(self, command, ignore=False):
        if not ignore:
            self.send_lock.acquire()
        if self.push_pos != -1:
            self.abort_message(ignore)
        self.push_pos = len(self.send)
        self.send.stream_in(PyMessageHeader(command, 0), in_type="Serializable")
        print ("sending: %-12s from begin_message" % command)

    def abort_message(self, ignore=False):
        if self.push_pos == -1:
            return

        self.send.erase(self.push_pos)
        self.push_pos = -1
        if not ignore:
            self.send_lock.release()
        print ("(aborted)")

    def end_message(self, ignore=False):
        if ctx.dropMessagesTest > 0 and (baseutil.get_rand(ctx.dropMessagesTest) == 0):
            print ("dropmessages DROPPING SEND MESSAGE")
            self.abort_message()
            return

        if self.push_pos == -1:
            return

        # Patch in the size
        size = len(self.send) - self.push_pos - PyMessageHeader().serialize_size()
        # 16 is offsetof(CMessageHeader, nMessageSize), equal to write from struct CMessageHeader.nMessageSize
        self.send.raw_write(ser_uint(size), self.push_pos + 16)
        # self.send.raw_write(ser_uint(size), 16)
        print ("(%d bytes)  " % size)

        self.push_pos = -1
        if not ignore:
            self.send_lock.release()

    def end_message_abort_if_empty(self, ignore=False):
        if self.push_pos == -1:
            return
        size = len(self.send) - self.push_pos - PyMessageHeader().serialize_size()
        if size > 0:
            self.end_message(ignore)
        else:
            self.abort_message(ignore)

    def get_message_command(self):
        if self.push_pos == -1:
            return ""
        return self.send.raw_read(self.push_pos, 4)  # 4 is offsetof(CMessageHeader, pchCommand)

    def push_message(self, command, *objs, **params):
        """
        objs is tuple for (obj, in_type)
        :param command:
        :param objs: tuple for (obj, in_type='str')
        :return:
        """
        ignore = params.get("ignore", False)

        try:
            self.begin_message(command, ignore)
            for obj in objs:
                if isinstance(obj, tuple) and len(obj) == 2:
                    self.send.stream_in(obj[0], obj[1])
                else:
                    self.send.stream_in(obj)

            self.end_message(ignore)
        except Exception, e:
            self.abort_message(ignore)
            raise RuntimeError("push_message error " + e.message)

    def push_request(self, command, func, param, *objs):
        hash_reply = ser_uint256(baseutil.rand_bytes(32))  # 32 is for uint256
        with self.dict_requests_lock:
            self.dict_requests[hash_reply] = PyRequestTracker(func, param)

        self.push_message(command, (hash_reply, "uint256"), *objs)
        pass

    def is_subscribed(self, channel):
        if channel >= len(self.listf_subscribe):
            return False
        return self.listf_subscribe[channel]

    def subscribe(self, channel, hops):
        if channel >= len(self.listf_subscribe):
            return
        if not any_subscribed(channel):
            # Relay subscribe
            with ctx.listNodesLock:
                for node in ctx.listNodes:
                    if id(node) != id(self):
                        node.push_message(base.COMMAND_SUBSCRIBE, (channel, "uint"), (hops, "uint"))
        self.listf_subscribe[channel] = True

    def cancel_subscribe(self, channel):
        if channel >= len(self.listf_subscribe):
            return

        # Prevent from relaying cancel if wasn't subscribed
        if self.listf_subscribe[channel] is False:
            return
        self.listf_subscribe[channel] = True
        if not any_subscribed(channel):
            # Relay subscription cancel
            with ctx.listNodesLock:
                for node in ctx.listNodes:
                    if id(node) != id(self):
                        node.push_message("sub-cancel", (channel, "uint"))

    def disconnect(self):
        print ("disconnecting node %s" % str(self.addr))
        self.hsocket.close()
        self.hsocket = None
        # All of a nodes broadcasts and subscriptions are automatically torn down
        # when it goes down, so a node has to stay up to keep its broadcast going.
        with ctx.dictProductsLock:
            for product in ctx.dictProducts.itervalues():
                advert_remove_source(self, MsgType.MSG_PRODUCT, 0, product)

        # Cancel subscriptions
        for channel, flag in enumerate(self.listf_subscribe):
            if flag:
                self.cancel_subscribe(channel)

    pass


class PyAddrDB(db.PyDB):
    def __init__(self, szmode="r+", f_txn=False):
        super(PyAddrDB, self).__init__("addr.dat", szmode, f_txn)

    def write_address(self, addr):
        self._write(("addr", addr.get_key()), addr)

    def load_addresses(self):
        with ctx.dictAddressesLock:
            # Load user provided addresses
            try:
                filein = dbserialize.PyAutoFile("addr.txt", "rt")
            except IOError, e:
                filein = None
                print e
            if filein:
                try:
                    with filein as f:
                        for line in f:
                            data = line.split(" ")
                            if len(data) != 2:
                                continue
                            # TODO  check addr format
                            add_address(self, PyAddress(data[0], int(data[1]), services_in=cfg.NODE_NETWORK))
                except RuntimeError, e:
                    print str(e)

            # get cursor
            cursor = self._get_cursor()
            if cursor is None:
                return False
            while True:
                ret = self.read_at_cursor(cursor)
                if ret is None:
                    break
                sskey = dbserialize.DataStream()
                sskey.deserialize(ret[0], nType=SerType.SER_DISK, nVersion=db.PyDB.Version)
                k = sskey.get_data()

                if isinstance(k, (tuple, list)) and len(k) == 2:
                    if k[0] == "addr":
                        addr = PyAddress()
                        addr.deserialize(ret[1], nType=SerType.SER_DISK, nVersion=db.PyDB.Version)
                        ctx.dictAddresses[addr.get_key()] = addr
                pass

            # debug print
            print ("mapAddresses:")
            for value in ctx.dictAddresses.itervalues():
                print str(value)
            print "-----"
        return True

    pass


def add_address(addrdb, addr):
    """

    :param addrdb:
    :type addrdb: PyAddrDB
    :param addr:
    :type addr: PyAddress
    :return:
    :rtype bool
    """
    if not addr.is_routable():
        return False
    if addr.ip == addrLocalHost.ip:
        return False
    with ctx.dictAddressesLock:
        old_addr = ctx.dictAddresses.get(addr.get_key(), None)
        if old_addr is None:
            # New address
            ctx.dictAddresses[addr.get_key()] = addr
            addrdb.write_address(addr)
            return True
        else:
            if (old_addr.services | addr.services) != old_addr.services:
                # Services have been added
                old_addr.services |= addr.services
                addrdb.write_address(old_addr)
                return True
    return False


nodeLocalHost = PyNode(None, PyAddress("127.0.0.1", services_in=ctx.localServices()))
addrLocalHost = PyAddress("0.0.0.0", cfg.DEFAULT_PORT, ctx.localServices())
ctx.nodeLocalHost = nodeLocalHost


#
# Subscription methods for the broadcast and subscription system.
# Channel numbers are message numbers, i.e. MSG_TABLE and MSG_PRODUCT.
#
# The subscription system uses a meet-in-the-middle strategy.
# With 100,000 nodes, if senders broadcast to 1000 random nodes and receivers
# subscribe to 1000 random nodes, 99.995% (1 - 0.99^1000) of messages will get through.
#
def any_subscribed(channel):
    if ctx.nodeLocalHost.is_subscribed(channel):
        return True
    with ctx.listNodesLock:
        for node in ctx.listNodes:
            if node.is_subscribed(channel):
                return True
    return False


#
# Templates for the publish and subscription system.
# The object being published as T& obj needs to have:
#   a set<unsigned int> setSources member
#   specializations of AdvertInsert and AdvertErase
# Currently implemented for CTable and CProduct.
#
def advert_start_publish(node_from, channel, hops, obj):
    """

    :param node_from:
    :type node_from: PyNode
    :param channel:
    :param hops:
    :param obj: PyProduct
    :return:
    """
    # Add to sources
    obj.set_sources.add(base.ip2uint(node_from.addr.ip))  # set_sources is set for uint
    if mkaction.advert_insert(obj) is False:
        return

    with ctx.listNodesLock:
        for node in ctx.listNodes:
            if id(node) != id(node_from) and (hops < cfg.PUBLISH_HOPS or node.is_subscribed(channel)):
                node.push_message("publish", (channel, "uint"), (hops, "uint"), (obj, "Serializable"))

    pass


def advert_stop_publish(node_from, channel, hops, obj):
    obj_hash = obj.get_hash()  # uint256
    with ctx.listNodesLock:
        for node in ctx.listNodes:
            if id(node) != id(node_from) and (hops < cfg.PUBLISH_HOPS or node.is_subscribed(channel)):
                node.push_message("pub-cancel", (channel, "uint"), (hops, "uint"), (obj_hash, "uint256"))
    mkaction.advert_erase(obj)


def advert_remove_source(node_from, channel, hops, obj):
    # Remove a source
    obj.set_sources.remove(base.ip2uint(node_from.addr.ip))  # set_sources is set for uint

    # If no longer supported by any sources, cancel it
    if len(obj.set_sources) == 0:
        advert_stop_publish(node_from, channel, hops, obj)
    pass


def main():
    print (base.ip2uint('127.0.0.1'))
    print TypeName.keys()
    print TypeNameList
    # command = '123456789012'
    # print "sending: %-12s " % command
    # print (PyMessageHeader().serialize_size())
    pass


if __name__ == '__main__':
    main()

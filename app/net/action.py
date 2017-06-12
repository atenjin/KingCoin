#!/usr/bin/env python  
# -*- coding: utf-8 -*-
from app import context as ctx, config as cfg
from app.net import net, base as netbase
from app.utils import timeutil, util
from app.base import serialize


def load_addresses():
    with net.PyAddrDB("cr+") as addrdb:
        return addrdb.load_addresses()


def find_node(addr_or_ip):
    with ctx.listNodesLock:
        if isinstance(addr_or_ip, net.PyAddress):
            for node in ctx.listNodes:
                if node.addr == addr_or_ip:
                    return node
        elif isinstance(addr_or_ip, str):
            for node in ctx.listNodes:
                if node.addr.ip == addr_or_ip:
                    return node
    return None


def connect_node(addr_conn, timeout=0):
    """

    :param addr_conn:
    :type addr_conn: PyAddress
    :param timeout:
    :return:
    :rtype net.PyNode
    """
    if addr_conn.ip == net.addrLocalHost.ip:
        return None
    # Look for an existing connection
    node = find_node(addr_conn.ip)
    if node:
        if timeout != 0:
            node.add_ref(timeout)
        else:
            node.add_ref()
        return node

    # debug
    print ("trying %s" % str(addr_conn))
    # connect
    # hsocket = socket.socket()  # (socket.AF_INET, socket.SOCK_STREAM)
    # The error indicator is 0 if the operation succeeded, otherwise the value of the errno variable
    hsocket = netbase.connect_socket(addr_conn)
    if hsocket is not None:
        # debug print
        print "connected %s" % str(addr_conn)

        # add node
        node = net.PyNode(hsocket, addr_conn, False)
        if timeout != 0:
            node.add_ref(timeout)
        else:
            node.add_ref()

        with ctx.listNodesLock:
            ctx.listNodes.append(node)
        with ctx.dictAddressesLock:
            ctx.dictAddresses[addr_conn.get_key()].last_failed = 0
        return node
    else:  # connect failed
        with ctx.dictAddressesLock:
            ctx.dictAddresses[addr_conn.get_key()].last_failed = timeutil.get_time()
        return None
    pass


def relay_inventory(inv):
    """
    向持有的所有的node发送 存货 inv
    :param inv:
    :return:
    """
    # Put on lists to offer to the other nodes
    with ctx.listNodesLock:
        for node in ctx.listNodes:
            node.push_inventory(inv)
    pass


def relay_message(inv, obj):
    if isinstance(obj, serialize.PyDataStream):
        ss = obj
    elif isinstance(obj, serialize.Serializable):
        ss = serialize.PyDataStream(nType=serialize.SerType.SER_NETWORK)
        ss.stream_in(obj, in_type="Serializable")
    else:
        raise TypeError("relay_message can only relay Serializable class and PyDataStream")

    with ctx.dictRelayLock:
        # Expire old relay messages
        while len(ctx.listRelayExpiration) != 0 and ctx.listRelayExpiration[0][0] < timeutil.get_time():
            relay_tuple = ctx.listRelayExpiration.popleft()  # relay_tuple = (time ,PyInv)
            ctx.dictRelay.pop(relay_tuple[1])  # dictRelay = dict<PyInv, PyDataStream>
        # Save original serialized message so newer versions are preserved
        ctx.dictRelay[inv] = ss
        ctx.listRelayExpiration.append((timeutil.get_time() + cfg.INV_EXPIRED_TIME, inv))  # 当前时间加上 15 min
    relay_inventory(inv)
    pass


def get_my_extrenal_IP():
    # addr = net.PyAddress("72.233.89.199", 80)
    # use own impl
    return util.external_IP()


def abandon_requests(func, param):
    # If the dialog might get closed before the reply comes back,
    # call this in the destructor so it doesn't get called after it's deleted.
    with ctx.listNodesLock:
        for node in ctx.listNodes:
            with node.dict_requests_lock:
                for key, tracker in node.dict_requests.items():
                    if tracker.func == func and tracker.param == param:
                        node.dict_requests.pop(key, None)
    pass


def main():
    list_addr_to_send = [net.addrLocalHost, net.addrLocalHost]
    s = serialize.PyDataStream()
    s.stream_in(list_addr_to_send).stream_in(net.PyAddress("123.123.123.123", 9090))
    print ((s.stream_out("list", (net.PyAddress))))
    print (str(s.stream_out(cls=net.PyAddress)))
    pass


if __name__ == '__main__':
    main()

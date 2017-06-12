#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import socket
import struct

from app import context as ctx
from app.base import serialize

COMMAND_VERSION = "version"
COMMAND_GETBLOCKS = "getblocks"
COMMAND_ADDR = "addr"
COMMAND_INV = "inv"
COMMAND_GETDATA = "getdata"
COMMAND_BLOCK = "block"
COMMAND_TX = "tx"
COMMAND_REVIEW = "review"
COMMAND_GETADDR = "getaddr"
COMMAND_CHECKORDER = "checkorder"
COMMAND_REPLY = "reply"
COMMAND_SUBMITORDER = "submitorder"
COMMAND_GETDETAILS = "getdetails"
COMMAND_SUBSCRIBE = "subscribe"


def ip2uint(addr):
    try:
        return struct.unpack("!I", socket.inet_aton(addr))[0]
    except:
        return 0


def uint2ip(addr):
    try:
        return socket.inet_ntoa(struct.pack("!I", addr))
    except:
        return '0.0.0.0'


class Timeval(object):
    def __init__(self, tv_sec=0, tv_usec=0):
        self.tv_sec = tv_sec
        self.tv_usec = tv_usec


def connect_socket(addr_conn):
    """

    :param addr_conn:
    :type addr_conn: net.PyAddress
    :return:
    """
    hsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)  # family, type, proto

    f_routable = addr_conn.is_routable()
    f_proxy = (ctx.addrProxy is not None) and f_routable
    addr = ctx.addrProxy.get_sockaddr() if f_proxy else addr_conn.get_sockaddr()
    # The error indicator is 0 if the operation succeeded, otherwise the value of the errno variable
    if hsocket.connect_ex(addr) != 0:
        hsocket.close()
        return None

    if f_proxy:
        print ("Proxy connecting to %s\n Proxy is: %s" % (str(addr_conn), str(ctx.addrProxy)))
        socks4IP = bytearray(b"\4\1\0\0\0\0\0\0user")
        socks4IP[2:4] = serialize.ser_ushort(addr_conn.port)
        socks4IP[4:8] = serialize.ser_uint(ip2uint(addr_conn.ip))
        socks4 = str(socks4IP)
        size = len(socks4)

        ret = hsocket.send(socks4, 0)
        if ret != size:
            hsocket.close()
            print "Error sending to proxy"
            return None

        ret = hsocket.recv(8, 0)

        if ret[1] != b'\x5a':
            hsocket.close("Proxy returned error %d" % ret[1])

        print "Proxy connection established %s " % str(addr_conn)
    return hsocket


def socket_send(hsocket, data_str):
    if data_str.find('PONG') != 0:
        print ("Sending: %s" % data_str)
    str_len = len(data_str)
    totalsend = 0
    while totalsend < str_len:
        sent = hsocket.send(data_str[totalsend:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsend = totalsend + sent


def main():
    pass


if __name__ == '__main__':
    main()

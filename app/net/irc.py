#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import threading
import socket
from StringIO import StringIO
import os

from app import config as cfg, context as ctx
from app.base import serialize
from app.block.key import keyutil
from app.net import net, base
from app.utils import timeutil

fRestrartIRCSeed = False


def recv_line(hsocket):
    str_line = ''
    while True:
        c = bytearray(1)
        try:
            nbytes = hsocket.recv_into(c, 1)
            if nbytes > 0:
                if c == '\n':
                    continue
                if c == '\r':
                    return str_line

                str_line += str(c)
            elif nbytes <= 0:
                if str_line:
                    return str_line
                print("IRC socket closed")
                return None
        except socket.error as msg:
            print(msg)
            print("IRC recv failed: %d" % msg.errno)
            return None

        pass  # end loop


def recv_line_IRC(hsocket):
    while True:
        str_line = recv_line(hsocket)

        if str_line is not None:
            if ctx.fShutdown:
                return None
            words = str_line.split(' ')
            if unicode(words[0]) == u'PING':
                str_line = str_line[0] + '0' + str_line[2:] + '\r'
                try:
                    base.socket_send(hsocket, str_line)
                except RuntimeError, e:
                    print(timeutil.get_strftime(), e)
                continue

        return str_line


def recv_until(hsocket, *szs):
    while True:
        str_line = recv_line_IRC(hsocket)
        if str_line is None:
            return False
        print("IRC %s" % str_line)

        for sz in szs:
            if sz and str_line.find(sz) != -1:
                return True

    pass


def encode_address(addr):
    ip = base.ip2uint(addr.ip)
    port = addr.port
    s = serialize.ser_uint(ip) + serialize.ser_ushort(port)
    print(repr(s))
    return 'u' + keyutil.base58CheckEncode(s)


def decode_address(s):
    ret = keyutil.base58CheckDecode(s[1:])
    if ret is None:
        return None
    if len(ret) != 6:  # sizeof (uint) + sizeof(ushort)
        return None
    addr = net.PyAddress()
    s_io = StringIO(ret)
    addr.ip = base.uint2ip(serialize.deser_uint(s_io))
    addr.port = serialize.deser_ushort(s_io)
    return addr


class IRCSeedThread(threading.Thread):
    def __init__(self, arg=None):
        super(IRCSeedThread, self).__init__()
        self.arg = arg

    def run(self):
        self.thread_IRC_seed(self.arg)
        pass

    def thread_IRC_seed(self, arg=None):
        while True:
            irc_ip = socket.gethostbyname(cfg.IRC_URL)
            addr_conn = net.PyAddress(irc_ip, cfg.IRC_PORT)
            hsocket = base.connect_socket(addr_conn)
            if hsocket is None:
                print("IRC connect failed")
                return

            if not recv_until(hsocket, "Found your hostname", "using your IP address instead",
                              "Couldn't look up your hostname"):
                hsocket.close()
                return
            str_my_name = encode_address(net.addrLocalHost)
            if not net.addrLocalHost.is_routable():
                str_my_name = keyutil.base58CheckEncode(os.urandom(6))

            base.socket_send(hsocket, ("NICK %s\r" % str_my_name))
            base.socket_send(hsocket, ("USER %s 8 * : %s\r" % (str_my_name, str_my_name)))

            if not recv_until(hsocket, " 004 "):
                hsocket.close()
                return

            timeutil.sleep_msec(500)

            base.socket_send(hsocket, "JOIN #%s\r" % cfg.IRC_CHANNEL)
            base.socket_send(hsocket, "WHO #%s\r" % cfg.IRC_CHANNEL)

            global fRestrartIRCSeed
            while not fRestrartIRCSeed:
                str_line = recv_line_IRC(hsocket)
                if ctx.fShutdown or str_line is None:
                    hsocket.close()
                    return

                if len(str_line) == 0 or str_line[0] != ':':
                    continue
                print("IRC line:(%s)" % str_line)
                words = str_line.split(' ')
                if len(words) < 2:
                    continue

                sz_name = '\x00'
                if words[1] == "352" and len(words) >= 8:
                    sz_name = words[7]
                    print("GOT WHO: [%s]  " % sz_name)
                if words[1] == "JOIN":
                    # :username!username@50000007.F000000B.90000002.IP JOIN :#channelname
                    sz_name = words[0][1:]
                    i = sz_name.find('!')
                    if i > 0:
                        sz_name = sz_name[:i]
                    print("GOT JOIN: [%s]  " % sz_name)

                if sz_name[0] == 'u':
                    addr = decode_address(sz_name)
                    if addr is not None:
                        with net.PyAddrDB() as addrdb:
                            if net.add_address(addrdb, addr):
                                print("store new address! ")
                        print(str(addr))
                    else:
                        print("meet 'u' prdix, buf decode failed, for %s" % sz_name)
                else:
                    print("decode failed")
                pass  # end loop

            fRestrartIRCSeed = False
            hsocket.close()
            pass
        pass


def main():
    pass


if __name__ == '__main__':
    addr = net.PyAddress("192.168.100.1", 8080)
    s = encode_address(addr)
    print(len(s))

    addr = net.PyAddress("0.0.0.0", 0)
    s = encode_address(addr)
    print(len(s))

    print(str(decode_address(s)))

    # get local host ip
    hostname, aliaslist, ipaddrlist = socket.gethostbyname_ex(socket.gethostname())
    net.addrLocalHost = net.PyAddress(ipaddrlist[-1], cfg.DEFAULT_PORT, ctx.localServices())

    IRCSeedThread(None).thread_IRC_seed(None)
    t = IRCSeedThread(None)
    t.start()

    t.join()
    main()

#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import socket
from app import context as ctx, config as cfg
from app.net import net, irc
from app.utils import timeutil
from app import thread


def get_local_ip():
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((cfg.TEST_IP_TARGET_URL, 80))
        ret = s.getsockname()[0]
        # add ip format check?
    except Exception, e:
        ret = '127.0.0.1'
    finally:
        if s is not None:
            s.close()
    return ret


def start_node():
    # sockets startup
    # ...

    # get local host ip
    # hostname, aliaslist, ipaddrlist = socket.gethostbyname_ex(socket.gethostname())
    # TODO check for local_ip
    # net.addrLocalHost = net.PyAddress(ipaddrlist[-1], cfg.DEFAULT_PORT, ctx.localServices())
    net.addrLocalHost = net.PyAddress(get_local_ip(), cfg.DEFAULT_PORT, ctx.localServices())

    # Create socket for listening for incoming connections
    try:
        hlisten_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        ctx.hlistenSocket= hlisten_socket
    except socket.error as msg:
        print (msg)
        print (
            "Error: Couldn't set properties on socket for incoming connections (ioctlsocket returned error %d)" % msg.errno)
        return False

    # Set to nonblocking, incoming connections will also inherit this
    # socket.oct
    hlisten_socket.setblocking(False)
    hlisten_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind & listen
    try:
        hlisten_socket.bind((net.addrLocalHost.ip, net.addrLocalHost.port))
        hlisten_socket.listen(socket.SOMAXCONN)
    except socket.error as msg:
        hlisten_socket.close()
        print (msg)
        print ("Error: Unable to bind to port %d on this computer or "
               "listening for incoming connections failed(returned error %d)" % (net.addrLocalHost.port, msg.errno))
        return False

    # Get our external IP address for incoming connections
    if ctx.addrIncoming is not None and ctx.addrIncoming.ip is not '0.0.0.0':
        net.addrLocalHost.ip = ctx.addrIncoming.ip

    # TODO check for external IP is current for real use
    # external_ip = util.extrenal_IP()
    # if external_ip is not None:
    #     net.addrLocalHost.ip = external_ip
    #     ctx.addrIncoming = net.addrLocalHost
    #     Block.PyWalletDB().write_setting("addrIncoming", ctx.addrIncoming)

    # start thread
    # Get addresses from IRC and advertise ours
    # irc_t = irc.IRCSeedThread(None)
    # irc_t.start()
    # ctx.listWorkThreads.append((irc_t, "irc_thread"))

    socket_t = thread.SocketThread(hlisten_socket)
    socket_t.start()
    ctx.listWorkThreads.append((socket_t, "socket_thread"))

    connections_t = thread.OpenConnectionsThread(None)
    connections_t.start()
    ctx.listWorkThreads.append((connections_t, "connections_thread"))

    message_t = thread.MessageThread(None)
    message_t.start()
    ctx.listWorkThreads.append((message_t, "message_thread"))

    return True


def stop_node():
    print ("StopNode()")
    ctx.fShutdown = True
    ctx.transactionsUpdated += 1
    while ctx.listfThreadRunning.count(True):
        timeutil.sleep_msec(10)
    timeutil.sleep_msec(50)
    # sockets shutdown ?
    return True


def main():
    pass


if __name__ == '__main__':
    main()

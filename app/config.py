#!/usr/bin/env python  
# -*- coding: utf-8 -*-
from os import sep
from app.utils.baseutil import get_app_dir

SYMBOL = 'kingcoin'
VERSION = 101
DBVERSION = VERSION

NID_secp256k1 = 714
SECRET_SIZE = 32
PRIVATE_KEY_SIZE = 279
PUBLIC_KEY_SIZE = 65
PUBLIC_KEY_COMPRESSED_SIZE = 33
SIGNATURE_SIZE = 72

ADDRESSVERSION = chr(0)  # "\x00"  # 注意这里只能使用 byte 的表示方法

MAX_SIZE = 0x02000000  # 2MB
COIN = 100000000  # 1亿
CENT = 1000000
# COINBASE_MATURITY = 100
COINBASE_MATURITY = 5

DISCOUNT_FOR_FEE_SIZE = 10000  # <10kB 交易大小

BLOCK_SUBSIDY = 50
HALVE_BLOCK_NUM = 210000

CHECK_BLOCK_TIME_EXPIRED_TIME = 2 * 60 * 60  # 换个命名吧··
RELAY_TX_SPAN = 10 * 60

TARGET_TIMESPAN = 60 * 60  # 1 hour #  14 * 24 * 60 * 60  # two weeks
# TARGET_SPACING = 10 * 60  # 10 分钟一个块
TARGET_SPACING = 5 * 60  # 5 分钟一个块   10 * 60 10分钟一个块
#  interval -> TARGET_TIME_SPAN/TARGET_SPACING = 60*60 / 3*60 => 20 / 1hour
# CONFIRMED_BLOCK_NUM = 6
CONFIRMED_BLOCK_NUM = 3  # 3个确认

COPY_DEPTH = 3

# print 'compact %x' % compact_from_uint256(proofOfWorkLimit)

# COIN = 100000000
MAX_MONEY = 21000000 * COIN

# market
FLOW_THROUGH_RATE = 2

# net
MESSAGE_HEADER_COMMAND_SIZE = 12
MAX_CONNECTIONS = 15
# IRC_URL = "chat.freenode.net"
IRC_URL = "192.168.1.100"
IRC_PORT = 6667
IRC_CHANNEL = 'coin'

TEST_IP_TARGET_URL = 'www.baidu.com'

COMMAND_GETADDR_SPAN_TIME = 60 * 60  # in the last hour

# The message start string is designed to be unlikely to occur in normal data.
# The characters are rarely used upper ascii, not valid as UTF-8, and produce
# a large 4-byte int at any alignment.
MESSAGE_START = b'\xf9\xbe\xb4\xd9'
MESSAGE_SIZE = 0x10000000
DEFAULT_PORT = 8333  # socket.htons(8333)
PUBLISH_HOPS = 5
NODE_NETWORK = 1 << 0

INV_EXPIRED_TIME = 15 * 60

strAppDir = get_app_dir(SYMBOL)
strLogDir = strAppDir + sep + 'database'

GENESIS_PUBKEY = '049d467dc1c98764995e058874725bc9ec7361fd0dd9a778418baae45004191547e8314f527ed9ce09a2d48fe78237a18e7b893afa28a4106720a2608b716b498e'

ALLOW_NEW = True


def block_file_name(file_index):
    return "%s\\blk%04d.dat" % (strAppDir, file_index)


def main():
    print DEFAULT_PORT
    pass


if __name__ == '__main__':
    print strLogDir
    main()

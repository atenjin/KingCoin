#!/usr/bin/env python
# -*- coding: utf-8 -*-
import struct

from app.base.serialize import ser_uint256


# def chr_x(u_num, endian='small', byte_n=-1):
#     assert isinstance(u_num, int) or isinstance(u_num, long)
#     s = b""
#     while True:
#         s += chr(u_num & 0xff)
#         u_num >>= 8
#         if u_num == 0:
#             break
#     if byte_n != -1:
#         if byte_n > len(s):
#             for _ in range(byte_n - len(s)):
#                 s += '\x00'
#     return s[::-1] if endian == 'big' else s
#     pass


# def num_x(s, endian='small'):
#     assert isinstance(s, str) or isinstance(s, bytearray)
#     if isinstance(s, bytearray):
#         s = bytes(s)
#     nbytes = len(s)
#     n = 0
#     l = range(nbytes)
#     if endian == 'big':
#         l = reversed(l)
#     for i in l:
#         n += (int(s[i].encode('hex'), 16) << (nbytes - 1 - i) * 8)
#     return n


def str_from_ushort(u):
    if u < 0:
        u += (0xffff + 1)

    if u > 0xffff:  # 截断
        u &= 0xffff

    return struct.pack("<H", u)


def ushort_from_str(s):
    '''
        :param s: str
        :return: int
    '''
    if len(s) > 2:
        s = s[0:2]
    elif len(s) < 2:
        s += (b'\x00' * (2 - len(s)))

    return struct.unpack("<H", s)[0]


def str_from_uint(u):
    t = u & 0x7FFFFFFF  # 截断 取出31bit
    if -0x7FFFFFFF < u < 0:  # 在正常范围内的负数补上负号
        t |= 0x80000000
    # if u < 0:
    #     u += (0xffffffff + 1)
    #
    # if u > 0xffffffff:  # 截断
    #     u &= 0xffffffff
    return struct.pack("<I", t)


def uint_from_str(s):
    '''
    :param s: str
    :return: int
    '''
    if len(s) > 4:
        s = s[0:4]
    elif len(s) < 4:
        s += (b'\x00' * (4 - len(s)))

    return struct.unpack("<I", s)[0]


def str_from_int(u):
    return struct.pack("<i", u)


def int_from_str(s):
    '''
    :param s: str
    :return: int
    '''
    return struct.unpack("<i", s)[0]


# def uint160_from_str(s):
#     r = 0
#     t = struct.unpack(b"<IIIII", s[:20])
#     for i in range(5):
#         r += t[i] << (i * 32)
#     return r

#
# def uint256_from_str(s):
#     r = 0
#     t = struct.unpack(b"<IIIIIIII", s[:32])
#     for i in range(8):
#         r += t[i] << (i * 32)
#     return r


# def str_from_uint256(uint256, endian='small'):
#     # return ser_uint256(uint256)
#     return chr_x(uint256, endian, byte_n=32)


# def hexstr_from_uint256(u):
#     return ''.join(['%02x' % s for s in str_from_uint256(u)])




def uint256_to_shortstr(u):
    s = "%064x" % (u,)
    return s[:16]


def cast_to_bool(s):
    for i in s:
        if i != b'\x00':
            return True
    return False


def ByteToHex(byteStr):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """

    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #
    #    hex = []
    #    for aChar in byteStr:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()

    return ''.join(["%02X " % ord(x) for x in byteStr]).strip()


# -------------------------------------------------------------------------------

def HexToByte(hexStr):
    """
    Convert a string hex byte values into a byte string. The Hex Byte values may
    or may not be space separated.
    """
    # The list comprehension implementation is fractionally slower in this case
    #
    #    hexStr = ''.join( hexStr.split(" ") )
    #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
    #                                   for i in range(0, len( hexStr ), 2) ] )

    bytes = []

    # hexStr = ''.join(hexStr.split(" "))

    for i in range(0, len(hexStr), 2):
        bytes.append(chr(int(hexStr[i:i + 2], 16)))

    return ''.join(bytes)


def main():


    print repr(cast_to_bool(b'\x00'))
    # print (repr(str_from_num(0xff, 2)))
    o = b'\xfe\xf3\x12'
    # n = num_from_str(o, 'big')
    # print (repr((n >> 8) & 0xFF))

    print (repr(str_from_ushort(258123)))
    print (ushort_from_str(b'\x00\x11'))
    pass


if __name__ == '__main__':
    main()

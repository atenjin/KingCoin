#
# bignum.py
#
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
#

# from __future__ import absolute_import, division, print_function, unicode_literals

import struct
import binascii


# from app.block.utils.typeutil import num_to_uchar


# generic big endian MPI format

def bn_bytes(v, have_ext=False):
    ext = 0
    if have_ext:
        ext = 1
    return ((v.bit_length() + 7) // 8) + ext


def bn2bin(v):
    s = bytearray()
    i = bn_bytes(v)
    while i > 0:
        s.append((v >> ((i - 1) * 8)) & 0xff)
        i -= 1
    return s


def bin2bn(s):
    l = 0
    for ch in s:
        l = (l << 8) | ch
    return l


def bn2mpi(v):
    have_ext = False
    if v.bit_length() > 0:
        have_ext = (v.bit_length() & 0x07) == 0

    neg = False
    if v < 0:
        neg = True
        v = -v

    s = struct.pack(b">I", bn_bytes(v, have_ext))
    ext = bytearray()
    if have_ext:
        ext.append(0)
    v_bin = bn2bin(v)
    if neg:
        if have_ext:
            ext[0] |= 0x80
        else:
            v_bin[0] |= 0x80
    return s + ext + v_bin


def mpi2bn(s):
    if len(s) < 4:
        return None
    s_size = str(s[:4])
    v_len = struct.unpack(b">I", s_size)[0]
    if len(s) != (v_len + 4):
        return None
    if v_len == 0:
        return 0

    v_str = bytearray(s[4:])
    neg = False
    i = v_str[0]
    if i & 0x80:
        neg = True
        i &= ~0x80
        v_str[0] = i

    v = bin2bn(v_str)

    if neg:
        return -v
    return v


# bitcoin-specific little endian format, with implicit size
def mpi2vch(s):
    r = s[4:]  # strip size
    r = r[::-1]  # reverse string, converting BE->LE
    return r


# equal to CBigNum::getvch()
def bn2vch(v):
    assert isinstance(v, int) or isinstance(v, long), "bn2vch must convert a num"
    return str(mpi2vch(bn2mpi(v)))


def vch2mpi(s):
    r = struct.pack(b">I", len(s))  # size
    r += s[::-1]  # reverse string, converting LE->BE
    return r


# equal CBigNum(vector<unsigned int>)
def vch2bn(s):
    assert type(s) is str or isinstance(s, bytearray), "vch2bn must convert a str or bytearray(PyScript)"
    return mpi2bn(vch2mpi(s))


def num_to_uchar(n):
    if n < 0:
        n += 0xff + 1
    if n > 0xff:
        raise RuntimeError("num must is a bytes")
    return struct.pack("B", n)


def invert_vch(s):
    return bytes(bytearray([num_to_uchar(~i) for i in bytearray(s)]))


def _extend_bytes(s1, s2):
    len1 = len(s1)
    len2 = len(s2)
    diff = len1 - len2
    if diff > 0:
        s2 = b'\x00' * diff + s2
    elif diff < 0:
        s1 = b'\x00' * (-diff) + s1
    return s1, s2


def and_vch(s1, s2):
    s1, s2 = _extend_bytes(s1, s2)
    return bytes(bytearray([num_to_uchar(fir & sed) for fir, sed in zip(bytearray(s1), bytearray(s2))]))
    pass


def or_vch(s1, s2):
    s1, s2 = _extend_bytes(s1, s2)
    return bytes(bytearray([num_to_uchar(fir | sed) for fir, sed in zip(bytearray(s1), bytearray(s2))]))
    pass


def xor_vch(s1, s2):
    s1, s2 = _extend_bytes(s1, s2)
    return bytes(bytearray([num_to_uchar(fir ^ sed) for fir, sed in zip(bytearray(s1), bytearray(s2))]))
    pass


vch_false = b'\x00'
vch_zero = b'\x00'
vch_true = b'\x01'

# equal to CBigNum::SetCompact()
# different difficulty 1 value-0x207fffff so without need for negative
# def uint256_from_compact(c):
#     nbytes = (c >> 24) & 0xFF
#     # some thing wrong in this place for negative, for negative
#     offset = nbytes - 3
#     if offset < 0:
#         v = (c & 0xFFFFFF) >> (-8 * offset)
#     else:
#         v = (c & 0xFFFFFF) << (8 * offset)
#     return v


from app.base import serialize


# for negative, but it don't be used  no int256
# def int256_from_compact(c):
#     nbytes = (c >> 24) & 0xFF
#     # high = (c >> 16) & 0xFF
#     v = 0
#     if c & 0x800000:
#         c &= 0xFF7FFFFF
#         v |= 1 << 255
#     # if high >= 0x80:
#     #     high = high - 0x80
#     #     c &= 0xff00ffff
#     #     c |= high << 16
#     #     v |= 1 << 255
#     offset = nbytes - 3
#     if offset < 0:
#         v |= (c & 0xFFFFFF) >> (-8 * offset)
#     else:
#         v |= (c & 0xFFFFFF) << (8 * offset)
#     return v
#
#
# def compact_from_int256(u):
#     negative = False
#     if u & (1 << 255):
#         negative = True
#         u -= (1 << 255)
#     s = chr_x(u, 'big')
#     high = int(s[0].encode('hex'), 16)
#     if high >= 0x80:
#         s = b'\00' + s
#     else:
#         if negative:
#             high += 0x80
#             s = chr(high) + s[1:]
#     nbytes = len(s)  # len of bytes
#     compact = nbytes << 24
#     offset = 0
#     if nbytes < 3:
#         offset = 3 - nbytes
#     compact |= int(s[:3].encode('hex'), 16) << offset * 8
#     return compact


# equal to CBigNum::GetCompact
# def compact_from_uint256(u):
#     """
#
#     :param u:
#     :type u: str
#     :return:
#     """
#     # if isinstance(u, int) or isinstance(u, long):
#     #     u = serialize.ser_uint256(u)
#     if type(u) == PyBigNum:
#         u = u.getvch()
#     nbytes = len(u)  # len of bytes
#     # print(nbytes)
#     compact = nbytes << 24
#     # compact |= int(s[0].encode('hex'), 16) << 16
#     # compact |= int(s[1].encode('hex'), 16) << 8
#     # compact |= int(s[2].encode('hex'), 16) << 0
#     offset = 0
#     if nbytes < 3:
#         offset = 3 - nbytes
#     compact |= int(u[:3].encode('hex'), 16) << offset * 8
#     return compact


class PyBigNum(long):
    def __new__(cls, *args, **kwargs):
        if isinstance(args[0], str) or isinstance(args[0], bytearray):
            num = vch2bn(args[0])
        else:
            num = args[0]
        return super(PyBigNum, cls).__new__(cls, num)

    def getvch(self):
        return bn2vch(self)

    def gethexvch(self, endian='big'):
        s = self.getvch()
        if endian == 'big':
            s = reversed(s)
        return binascii.hexlify(s).strip()  # ''.join(["%02X " % ord(x) for x in s]).strip()

    def getint(self):
        return int(self)

    def getlong(self):
        return long(self)

    @staticmethod
    def set_compact(compact):
        size = compact >> 24
        s = bytearray(4 + size)
        s[0:4] = serialize.ser_uint(size, endian="big")
        if size >= 1:
            s[4] = compact >> 16 & 0xFF
        if size >= 2:
            s[5] = compact >> 8 & 0xFF
        if size >= 3:
            s[6] = compact >> 0 & 0xFF
        ret = mpi2bn(s)
        return PyBigNum(ret)

    def get_compact(self):
        # compact_from_uint256(self.getvch())
        v = bytes(bn2mpi(self))

        # print(len(v))
        size = len(v)
        size -= 4
        compact = size << 24
        if size >= 1:
            compact |= (struct.unpack("B", v[4])[0] << 16)
        if size >= 2:
            compact |= (struct.unpack("B", v[5])[0] << 8)
        if size >= 3:
            compact |= (struct.unpack("B", v[6])[0] << 0)
        return compact

    def get_uint256(self, out_type=None):
        b = bn2mpi(self)
        size = len(b)
        if size < 4:
            return 0
        else:
            b[4] &= 0x7F  # modify num negative
        n = bytearray(32)  # uint256
        i = 0  # 0 -> 28 for n,  empty for last 4 B
        for j in range(size - 1, 3, -1):  # 32 -> 4 for b
            if i >= 32:
                break
            n[i] = b[j]
            i += 1
        if out_type == "str":
            return bytes(n)
        if out_type == "hex":
            return serialize.hexser_uint256(bytes(n), in_type="str")
        return serialize.deser_uint256(bytes(n))

    pass


# class uint256(str):


def main():
    ret = bn2vch(0x10 + 1)
    ret = bn2vch(1000)
    # ret = bn2vch(-0x1)
    ret = bn2vch(0xffffffffffffff)
    print(repr(ret))
    print(type(ret))

    test = b'\x01\xff\xff\x00\x64\x9c\x01'
    print(repr(test))
    print(repr(invert_vch(test)))

    print(repr(_extend_bytes(b'', b'')))
    print(repr(_extend_bytes(b'\x12\x35\57', b'')))
    print(repr(_extend_bytes(b'\x12\x35\57', b'\x12\x35\57\x56\x78')))
    print(repr(_extend_bytes(b'', b'\x12\x35\57\x56\x78')))

    print(repr(and_vch(b'', b'')))
    print(repr(or_vch(b'\x12\x35\57', b'')))
    print(repr(xor_vch(b'\x12\x35\57', b'\x12\x35\57\x56\x78')))
    print(repr(and_vch(b'', b'\x12\x35\57\x56\x78')))
    print(repr(xor_vch(b'\x12\x35\57\x56\x78', b'\x12\x35\57\x56\x78')))

    print("test")
    # print (repr(num_to_uchar(-1)))
    print('========bignum=========')
    # print(repr(BigNum(1).getvch()))
    # print(repr(BigNum(11111111111111111111111).getvch()))
    # print (BigNum(1) < BigNum(2))
    n = PyBigNum(b'\x01\x01\x00')
    print(n)
    print(repr(n.getvch()))
    print("start")
    n = PyBigNum(-2 + 0xFFFFFFFF + 1)
    print(type(n))
    n += PyBigNum(1)
    print(n)
    print(type(n))
    n -= 1
    print(n)
    print(type(n))
    n = -n
    print(n)
    print(type(n))
    n = abs(n)
    print(n)
    print(type(n))
    n >>= 1
    print(n)
    print(type(n))
    n <<= 1
    print(n)
    print(type(n))
    print(n == 0)
    print(n != 0)
    # print(n)
    # print(repr(n.getvch()))
    #
    # n2 = PyBigNum(n.getvch()[:-1])
    # print(n2)
    # print(int(n2))

    # # test case from https://bitcoin.org/en/developer-reference#target-nbits
    # # big end
    # test = b"\x01\x00\x34\x56"
    # test = b"\x01\x12\x34\x56"
    # test = b"\x01\00\x00\x12"
    # test = b"\x02\x00\x80\x00"
    # test = b"\x05\x00\x92\x34"
    # test = b"\x04\x92\x34\x56"
    # test = b"\x04\x12\x34\x56"
    # # uint = deser_uint(StringIO.StringIO(test), 'big')
    # uint = num_x(test, 'big')
    # # small end
    # # test = b"\x00\x38\x03\x05"
    # # uint = num_x(test)
    # r = int256_from_compact(uint)
    # print("bignum:", repr(chr_x(r)))
    # u = compact_from_int256(r)
    # print('compact:%x' % u)

    print("#####################")

    _s = b''
    for i in range(32):
        _s += b'\xff'
    _s = _s[:28] + b'\x00\x00\x00\x00\x00\x00\x00\x00'  # _s = ~uint256(0) >> 32
    proofOfWorkLimit = PyBigNum(_s)  # init
    ret = proofOfWorkLimit.get_compact()
    print(ret)
    print(repr(struct.pack(">I", ret)))

    print(repr(proofOfWorkLimit.get_uint256()))
    # print (repr(proofOfWorkLimit.getvch()))
    print("#####################")
    n = PyBigNum.set_compact(0x1d00ffff)
    print (repr(serialize.ser_uint256(n)))

    n *= 20 * 60
    print type(n)
    print n

    _s = b''
    for i in range(32):
        _s += b'\xff'
    _s = _s[:30] + b'\x00\x00\x00\x00'  # _s = ~uint256(0) >> 32
    proofOfWorkLimit = PyBigNum(_s)  # init
    if n > proofOfWorkLimit:
        print 'over'
    else:
        print 'current'
    print type(n)
    n = PyBigNum(n)
    print n.get_compact()

    n2 = PyBigNum(n)
    print n2
    print n.get_compact()

    pass


if __name__ == "__main__":
    main()

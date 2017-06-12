#
# serialize.py
#
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
#
# from https://github.com/jgarzik/python-bitcoinlib/blob/master/bitcoin/script.py
# from __future__ import absolute_import, division, print_function, unicode_literals

import binascii
import struct
import inspect
from StringIO import StringIO
from enum import IntEnum
import types
from copy import deepcopy

from app import config as cfg

# Py3 compatibility
import sys

bchr = chr
if sys.version > '3':
    bchr = lambda x: bytes([x])


def wrap_to_StringIO(f):
    if isinstance(f, bytearray):
        f = bytes(f)
    if isinstance(f, str):
        f = StringIO(f)
    return f


class SerType(IntEnum):
    # primary actions
    SER_NETWORK = (1 << 0)
    SER_DISK = (1 << 1)
    SER_GETHASH = (1 << 2)

    # modifiers
    SER_SKIPSIG = (1 << 16)
    SER_BLOCKHEADERONLY = (1 << 17)


def deser_str(f):
    nit = struct.unpack(b"<B", f.read(1))[0]
    if nit == 253:
        nit = struct.unpack(b"<H", f.read(2))[0]
    elif nit == 254:
        nit = struct.unpack(b"<I", f.read(4))[0]
    elif nit == 255:
        nit = struct.unpack(b"<Q", f.read(8))[0]
    return f.read(nit)


def ser_str(s):
    if len(s) < 253:
        return bchr(len(s)) + s
    elif len(s) < 254:
        return bchr(253) + struct.pack(b"<H", len(s)) + s
    elif len(s) < 255:
        return bchr(254) + struct.pack(b"<I", len(s)) + s
    return bchr(255) + struct.pack(b"<Q", len(s)) + s


def ser_flatdata(s, n=-1):
    s_size = len(s)
    if s_size < n:
        s += (b'\x00' * (n - s_size))
    elif s_size > n:
        s = s[:n]
    return s


def deser_flatdata(f, n):
    return f.read(n)


def deser_uint256(f):
    r = 0
    if type(f) is str:
        f = StringIO(f)
    for i in range(8):
        t = struct.unpack(b"<I", f.read(4))[0]
        r += t << (i * 32)
    return r


def ser_uint256(u):
    rs = b""
    for i in range(8):
        rs += struct.pack(b"<I", u & 0xFFFFFFFF)
        u >>= 32
    return rs


def hexser_uint256(u, in_type=None):
    if in_type != 'str':
        u = ser_uint256(u)
    return binascii.hexlify(u)  # ''.join(["%02X" % ord(x) for x in u])


def deser_uint160(f):
    r = 0
    if type(f) is str or isinstance(f, bytearray):
        f = StringIO(f)
    for i in range(5):
        t = struct.unpack(b"<I", f.read(4))[0]
        r += t << (i * 32)
    return r


def ser_uint160(u):
    rs = b""
    for i in range(5):
        rs += struct.pack(b"<I", u & 0xFFFFFFFF)
        u >>= 32
    return rs


def deser_int64(f):
    return struct.unpack(b"<q", f.read(8))[0]


def ser_int64(u):
    return struct.pack(b"<q", u)


def deser_uint64(f):
    return struct.unpack(b"<Q", f.read(8))[0]


def ser_uint64(u):
    return struct.pack(b"<Q", u)


def deser_uint(f, endian='small'):
    if endian == 'big':
        return struct.unpack(b">I", f.read(4))[0]
    return struct.unpack(b"<I", f.read(4))[0]


def ser_uint(i, endian='small'):
    if endian == 'big':
        return struct.pack(b">I", i)
    return struct.pack(b"<I", i)


def deser_int(f, endian='small'):
    if endian == 'big':
        return struct.unpack(b">i", f.read(4))[0]
    return struct.unpack(b"<i", f.read(4))[0]


def ser_int(i, endian='small'):
    if endian == 'big':
        return struct.pack(b">i", i)
    return struct.pack(b"<i", i)


def deser_short(f, endian='small'):
    if endian == 'big':
        return struct.unpack(b">h", f.read(2))[0]
    return struct.unpack(b"<h", f.read(2))[0]


def ser_short(i, endian='small'):
    if endian == 'big':
        return struct.pack(b">h", i)
    return struct.pack(b"<h", i)


def deser_ushort(f, endian='small'):
    if endian == 'big':
        return struct.unpack(b">H", f.read(2))[0]
    return struct.unpack(b"<H", f.read(2))[0]


def ser_ushort(i, endian='small'):
    if endian == 'big':
        return struct.pack(b">H", i)
    return struct.pack(b"<H", i)


def deser_char(f):
    return struct.unpack(b"b", f.read(1))[0]


def ser_char(i):
    return struct.pack(b"b", i)


def deser_uchar(f):
    return struct.unpack(b"B", f.read(1))[0]


def ser_uchar(i):
    return struct.pack(b"B", i)


# list
def deser_list(f, cls, arg1=None, nType=0, nVersion=cfg.VERSION):
    nit = struct.unpack(b"<B", f.read(1))[0]
    if nit == 253:
        nit = struct.unpack(b"<H", f.read(2))[0]
    elif nit == 254:
        nit = struct.unpack(b"<I", f.read(4))[0]
    elif nit == 255:
        nit = struct.unpack(b"<Q", f.read(8))[0]
    r = []
    for i in range(nit):
        if isinstance(cls, types.FunctionType):
            t = cls(f)
        else:
            if arg1 is not None:
                t = cls(arg1)
            else:
                t = cls()
            t.deserialize(f)
        r.append(t)
    return r


def ser_list(l, ser_func=None, cls=None, nType=0, nVersion=cfg.VERSION):
    s = StringIO()
    if len(l) < 253:
        s.write(bchr(len(l)))
    elif len(l) < 254:
        s.write(bchr(253) + struct.pack(b"<H", len(l)))
    elif len(l) < 255:
        s.write(bchr(254) + struct.pack(b"<I", len(l)))
    else:
        s.write(bchr(255) + struct.pack(b"<Q", len(l)))
    for i in l:
        if cls is not None:
            s.write(cls.serialize(i, nType=nType, nVersion=nVersion))
        else:
            s.write(i.serialize(nType=nType, nVersion=nVersion) if ser_func is None else ser_func(i))
    return s.getvalue()


def deser_uint256_list(f):
    return deser_list(f, deser_uint256)


def ser_uint256_list(l):
    return ser_list(l, ser_func=ser_uint256)


def deser_str_list(f):
    return deser_list(f, deser_str)


def ser_str_list(l):
    return ser_list(l, ser_func=ser_str)


def deser_strpair_list(f):
    nit = struct.unpack(b"<B", f.read(1))[0]
    if nit == 253:
        nit = struct.unpack(b"<H", f.read(2))[0]
    elif nit == 254:
        nit = struct.unpack(b"<I", f.read(4))[0]
    elif nit == 255:
        nit = struct.unpack(b"<Q", f.read(8))[0]
    r = []
    for i in range(nit):
        fir = deser_str(f)
        sec = deser_str(f)
        r.append((fir, sec))
    return r


def ser_strpair_list(l):
    r = b""
    if len(l) < 253:
        r = bchr(len(l))
    elif len(l) < 254:
        r = bchr(253) + struct.pack(b"<H", len(l))
    elif len(l) < 255:
        r = bchr(254) + struct.pack(b"<I", len(l))
    else:
        r = bchr(255) + struct.pack(b"<Q", len(l))
    for sv in l:
        r += ser_str(sv[0])
        r += ser_str(sv[1])
    return r


def deser_int_list(f):
    return deser_list(f, deser_int)


def ser_int_list(l):
    return ser_list(l, ser_func=ser_int)


def deser_str_dict(f):
    return deser_dict(f, deser_str, deser_str)


def ser_str_dict(d):
    return ser_dict(d, ser_str, ser_str)


def deser_dict(f, key_cls, value_cls, arg1=None, arg2=None):
    nit = struct.unpack(b"<B", f.read(1))[0]
    if nit == 253:
        nit = struct.unpack(b"<H", f.read(2))[0]
    elif nit == 254:
        nit = struct.unpack(b"<I", f.read(4))[0]
    elif nit == 255:
        nit = struct.unpack(b"<Q", f.read(8))[0]
    r = dict()
    for i in range(nit):
        if isinstance(key_cls, types.FunctionType):
            k = key_cls(f)
        else:
            if arg1 is not None:
                k = key_cls(arg1)
            else:
                k = key_cls()
            k.deserialize(f)

        if isinstance(value_cls, types.FunctionType):
            v = value_cls(f)
        else:
            if arg2 is not None:
                v = value_cls(arg2)
            else:
                v = value_cls()
            v.deserialize(f)

        r[k] = v
    return r


def ser_dict(d, key_ser_fuc=None, value_ser_fuc=None):
    r = b""
    dict_size = len(d)
    if dict_size < 253:
        r = bchr(len(d))
    elif dict_size < 254:
        r = bchr(253) + struct.pack(b"<H", dict_size)
    elif len(d) < 255:
        r = bchr(254) + struct.pack(b"<I", dict_size)
    else:
        r = bchr(255) + struct.pack(b"<Q", dict_size)
    for k, v in d.items():
        r += key_ser_fuc(k) if key_ser_fuc is not None else k.serialize()
        r += value_ser_fuc(v) if value_ser_fuc is not None else v.serialize()
    return r


class DataType(IntEnum):
    SER_NETWORK = (1 << 0)
    SER_DISK = (1 << 1)
    SER_GETHASH = (1 << 2)

    # modifiers
    SER_SKIPSIG = (1 << 16)
    SER_BLOCKHEADERONLY = (1 << 17)


class Stream(object):
    def write(self, s):
        pass

    def read(self, n=-1):
        pass


class Serializable(object):
    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        raise NotImplementedError("must implement deserialize function")

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        raise NotImplementedError("must implement serialize function")

    def serialize_size(self, nType=0, nVersion=cfg.VERSION):
        return len(self.serialize(nType, nVersion))


def serialize_hash(s, nType=SerType.SER_GETHASH, nVersion=cfg.VERSION):
    """

    :param s:
    :type s: Serializable
    :return:
    """
    return s.serialize(nType, nVersion=nVersion)


UCHAR_MAX = 0xff


def _get_size_of_compact_size(size):
    if size < (UCHAR_MAX - 2):
        return 1
    elif size <= 0xffff:
        return 1 + 2
    elif size <= 0xffffffff:
        return 1 + 4
    else:
        return 1 + 8


# same as serialize.ser_string()
def _write_compact_size(stream, size):
    if size < (UCHAR_MAX - 2):  # uchar_max-2
        stream.write(struct.pack("<B", size))  # unsigned char
    elif size <= 0xffff:  # ushort_max
        ch_str = struct.pack("<B", UCHAR_MAX - 2)  # unsigned char
        size_str = struct.pack("<H", size)  # unsigned shor
        stream.write(ch_str)
        stream.write(size_str)
    elif size <= 0xffffffff:  # uint_max
        ch_str = struct.pack("<B", UCHAR_MAX - 1)  # unsigned char
        size_str = struct.pack("<I", size)  # unsigned int
        stream.write(ch_str)
        stream.write(size_str)
    else:
        ch_str = struct.pack("<B", UCHAR_MAX)  # unsigned char
        size_str = struct.pack("<Q", size)  # unsigned long long
        stream.write(ch_str)
        stream.write(size_str)


# same as serialize.deser_string()
def _read_compact_size(stream):
    s = stream.read(1)  # read 1 byte
    n = struct.unpack("<B", s)[0]
    if n < (UCHAR_MAX - 2):
        return n
    elif n == UCHAR_MAX - 2:
        s = stream.read(2)  # read 2B
        return struct.unpack("<H", s)[0]
    elif n == UCHAR_MAX - 1:
        s = stream.read(4)  # read 4B
        return struct.unpack("<I", s)[0]
    else:
        s = stream.read(8)  # read 8B
        return struct.unpack("<Q", s)[0]


def Serialize(stream, obj, in_type=None, nType=0, nVersion=cfg.VERSION):
    """

    :param stream:
    :type stream: Stream
    :param obj:
    :type obj: any
    :param in_type:
    :type in_type: str | unicode | tuple
    :param nType:
    :param nVersion:
    :return:
    """
    if in_type is None:
        in_type = type(obj).__name__
        if in_type not in ['str', 'unicode', 'int', 'long', 'tuple', 'list', 'dict', 'set']:
            in_type = Serializable

    if isinstance(obj, Serializable) or in_type == 'Serializable':
        s = obj.serialize(nType=nType, nVersion=nVersion)
        stream.write(s)
    elif (isinstance(obj, tuple) or in_type == 'tuple') and len(obj) == 2:
        Serialize(stream, obj[0], in_type=in_type[0], nType=nType, nVersion=nVersion)
        Serialize(stream, obj[1], in_type=in_type[1], nType=nType, nVersion=nVersion)
    elif isinstance(obj, (list, set)) or in_type == 'list' or in_type == 'set':
        _write_compact_size(stream, len(obj))
        for i in obj:
            stream.write(Serialize(stream, i, in_type=in_type, nType=nType, nVersion=nVersion))
    elif isinstance(obj, dict) or in_type == 'dict':
        _write_compact_size(stream, len(obj))
        for k, v in obj.items():
            stream.write(Serialize(stream, k, in_type=in_type[0], nType=nType, nVersion=nVersion))
            stream.write(Serialize(stream, v, in_type=in_type[1], nType=nType, nVersion=nVersion))
    elif in_type == 'str':
        _write_compact_size(stream, len(obj))
        stream.write(obj)
    elif in_type == 'char':
        stream.write(ser_char(obj))
    elif in_type == 'uchar':
        stream.write(ser_uchar(obj))
    elif in_type == 'short':
        stream.write(ser_short(obj))
    elif in_type == 'ushort':
        stream.write(ser_ushort(obj))
    elif in_type == 'int':
        stream.write(ser_int(obj))
    elif in_type == 'uint':
        stream.write(ser_uint(obj))
    elif in_type == 'int64':
        stream.write(ser_int64(obj))
    elif in_type == 'uint64':
        stream.write(ser_uint64(obj))
    elif in_type == 'uint160':
        stream.write(ser_uint160(obj))
    elif in_type == 'uint256':
        stream.write(ser_uint256(obj))
    else:
        raise TypeError("Unsupported type")


def Unserialize(f, out_type='str', cls=None, nType=0, nVersion=cfg.VERSION):
    """

    :param f:
    :type f: Stream
    :param out_type:
    :type out_type: str | unicode | None
    :param cls:
    :type cls: type | tuple | None
    :param nType:
    :param nVersion:
    :return:
    """
    if out_type == "str" and cls is not None:
        out_type = None
    if (out_type == 'Serializable' or out_type is None) and \
            (cls is not None and inspect.isclass(cls) and issubclass(cls, Serializable)):
        ins = cls()  # new the instance
        ins.deserialize(f, nType, nVersion)
        return ins
    elif out_type == 'tuple':
        if not isinstance(cls, tuple) or len(cls) != 2:
            raise TypeError("when out_type is tuple, the cls must be the tuple like ((info1,cls1), (info2,cls2))")
        if type(cls[0]) is tuple:
            fir = Unserialize(f, cls[0][0], cls[0][1], nType=nType, nVersion=nVersion)
        else:
            if isinstance(cls[0], (str, unicode)):
                fir = Unserialize(f, cls[0], None, nType=nType, nVersion=nVersion)
            elif inspect.isclass(cls) and issubclass(cls, Serializable):
                fir = Unserialize(f, None, cls[0], nType=nType, nVersion=nVersion)
            else:
                raise TypeError(
                    "when out_type is 'tuple', the cls must be (ele_type, ele_class) or ele_type or Serializable class")

        if type(cls[1]) is tuple:
            sec = Unserialize(f, cls[1][0], cls[1][1], nType=nType, nVersion=nVersion)
        else:
            if isinstance(cls[1], (str, unicode)):
                sec = Unserialize(f, cls[1], None, nType=nType, nVersion=nVersion)
            elif inspect.isclass(cls) and issubclass(cls, Serializable):
                sec = Unserialize(f, None, cls[1], nType=nType, nVersion=nVersion)
            else:
                raise TypeError(
                    "when out_type is 'tuple', the cls must be ('type', Serializable) or 'type' or Serializable")

        return fir, sec
    elif out_type == 'list' or out_type == 'set':
        size = _read_compact_size(f)
        if isinstance(cls, tuple) and len(cls) == 2:
            ret = [Unserialize(f, out_type=cls[0], cls=cls[1], nType=nType, nVersion=nVersion) for _ in range(size)]
        elif isinstance(cls, (str, unicode)):
            ret = [Unserialize(f, out_type=cls, cls=None, nType=nType, nVersion=nVersion) for _ in range(size)]
        elif inspect.isclass(cls) and issubclass(cls, Serializable):
            ret = [Unserialize(f, out_type=None, cls=cls, nType=nType, nVersion=nVersion) for _ in range(size)]
        else:
            raise TypeError(
                "when out_type is 'list' or 'set', the cls must be ('type', Serializable) 'type' or Serializable")
        return ret if out_type == 'list' else set(ret)
    elif out_type == 'dict':
        if not isinstance(cls, tuple) or len(cls) != 2:
            raise TypeError(
                "when out_type is tuple, the cls must be the tuple like ((key_info,key_cls), (value_info,value_cls))")
        size = _read_compact_size(f)
        r = dict()
        for _ in range(size):
            if type(cls[0]) is type:
                k = Unserialize(f, cls[0][0], cls[0][1], nType=nType, nVersion=nVersion)
            else:
                if isinstance(cls[0], (str, unicode)):
                    k = Unserialize(f, cls[0], None, nType=nType, nVersion=nVersion)
                elif inspect.isclass(cls) and issubclass(cls, Serializable):
                    k = Unserialize(f, None, cls[0], nType=nType, nVersion=nVersion)
                else:
                    raise TypeError(
                        "when out_type is 'dict', the cls must be ('key_type', Serializable) 'key_type' or Serializable")
            if type(cls[1]) is type:
                v = Unserialize(f, cls[1][0], cls[1][1], nType=nType, nVersion=nVersion)
            else:
                if isinstance(cls[1], (str, unicode)):
                    v = Unserialize(f, cls[1], None, nType=nType, nVersion=nVersion)
                elif inspect.isclass(cls) and issubclass(cls, Serializable):
                    v = Unserialize(f, None, cls[1], nType=nType, nVersion=nVersion)
                else:
                    raise TypeError(
                        "when out_type is 'dict', the cls must be ('key_type', Serializable) 'key_type' or Serializable")
            r[k] = v
        return r
    elif out_type == 'str':
        size = _read_compact_size(f)
        return f.read(size)
    elif out_type == 'char':
        return deser_char(f)
    elif out_type == 'uchar':
        return deser_uchar(f)
    elif out_type == 'short':
        return deser_short(f)
    elif out_type == 'ushort':
        return deser_ushort(f)
    elif out_type == 'int':
        return deser_int(f)
    elif out_type == 'uint':
        return deser_uint(f)
    elif out_type == 'int64':
        return deser_int64(f)
    elif out_type == 'uint64':
        return deser_uint64(f)
    elif out_type == 'uint160':
        return deser_uint160(f)
    elif out_type == 'uint256':
        return deser_uint256(f)
    else:
        raise TypeError("Unsupported type")


def GetSerializeSize(s):
    return _get_size_of_compact_size(len(s)) + len(s)


def GetSizeOfCompactSize(size):
    return _get_size_of_compact_size(size)


class PyFlatData(Serializable):
    def __init__(self, data, size=-1):
        self.__data = data
        if size == -1:
            self.__size = len(self.__data)
        else:
            self.__size = size

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        return self.__data
        pass

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        if self.__size == -1:
            raise RuntimeError("FlatData must init with size")
        self.__data = f.read(self.__size)
        return self.__data

    def serialize_size(self, nType=0, nVersion=cfg.VERSION):
        return self.__size

    pass


class PyDataStream(StringIO, Stream, Serializable):
    def __init__(self, s=b'', nType=0, nVersion=cfg.VERSION):
        super(PyDataStream, self).__init__(s)
        self.nType = nType
        self.nVersion = nVersion
        pass

    def __add__(self, other):
        s = self.getvalue()
        pos = self.tell()
        s += other.unread_str()
        self.buf = s
        self.len = len(self.buf)
        self.seek(pos)
        return self

    def __str__(self):
        return self.getvalue()[self.pos:]

    def __len__(self):
        return len(self.getvalue()) - self.pos

    def __getitem__(self, n):
        pos = self.tell()
        s = self.getvalue()
        if isinstance(n, slice):
            fir = pos + (n.start if n.start else 0)
            sec = pos + (n.stop if n.stop else len(self))
            if n.step is not None:
                raise NotImplementedError("not impl for step")
            return s[fir:sec]
        elif isinstance(n, (int, long)):
            if pos + n > len(s):
                return ""
            return s[pos + n]
        else:
            raise NotImplementedError("just impl for slice and int/long")

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        print "Warning! Can't use this function"
        pass

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        # Special case: stream << stream concatenates like stream += stream
        return str(self)

    def copy(self):
        return deepcopy(self)

    def begin_index(self):
        return self.tell()  # pos

    def end_index(self):
        return len(self.getvalue())

    def write(self, s):
        pos = self.tell()
        self.seek(len(self.getvalue()))
        super(PyDataStream, self).write(s)
        self.seek(pos)

    def raw_write(self, s, pos):
        old_pos = self.tell()
        self.seek(old_pos + pos)
        super(PyDataStream, self).write(s)
        self.seek(old_pos)

    def raw_read(self, fir, size):
        old_pos = self.tell()
        fir += old_pos
        return self.getvalue()[fir:fir + size]

    def raw_read_buf(self, fir, size):
        return self.getvalue()[fir:fir + size]

    def unread_str(self):
        return self.getvalue()[self.tell():]

    def insert(self, index, b):
        self.flush()
        s = self.getvalue()
        pos = self.tell()
        if index >= pos:
            s = s[:index] + b + s[index:]
            self.buf = s
            self.len = len(self.buf)
            self.seek(pos)

    def erase(self, first, last=-1):
        if last == -1:
            last = self.end_index()
            if last < first:
                last = first
        s = self.getvalue()
        if first == self.tell():
            # special case for erasing from the front
            if last == len(s):
                self.seek(0)
                self.buf = ''
                self.len = 0
            else:
                self.seek(last)
        else:
            self.buf = s[:first] + s[last:]
            self.len = len(self.buf)
            # if last == -1:
            #     last = first + 1
            # assert first <= last, "last index must larger than first index"
            # if first == last:
            #     return
            # s = self.getvalue()
            # pos = self.tell()
            # if last < pos:
            #     return
            # elif first < pos <= last:
            #     first = pos
            # elif pos <= first:
            #     pos = first
            #     pass
            # s = s[:first] + s[last:]
            # self.buf = s
            # self.len = len(self.buf)
            # self.seek(pos)

    def ignore(self, size):
        if size < 0:
            return
        read_pos_next = self.tell() + size
        buff_str = self.getvalue()
        buff_str_size = len(buff_str)
        if read_pos_next >= buff_str_size:
            self.clear()
            return self
        self.seek(read_pos_next)
        return self

    def compact(self):
        pos = self.tell()
        self.buf = self.getvalue()[pos:]
        self.len = len(self.buf)
        self.seek(0)

    def clear(self):
        self.getvalue()
        self.seek(0)
        self.buf = ''
        self.len = 0

    def stream_in(self, obj, in_type=None):
        Serialize(self, obj, in_type, nType=self.nType, nVersion=self.nVersion)
        return self

    def stream_out(self, out_type="str", cls=None):
        return Unserialize(self, out_type, cls, nType=self.nType, nVersion=self.nVersion)

    pass


def main():
    print(hexser_uint256(0xfffffffffffff))

    # class SerType(IntEnum):
    #     # primary actions
    #     SER_NETWORK = (1 << 0)
    #     SER_DISK = (1 << 1)
    #     SER_GETHASH = (1 << 2)
    #
    #     # modifiers
    #     SER_SKIPSIG = (1 << 16)
    #     SER_BLOCKHEADERONLY = (1 << 17)
    #
    #     def __or__(self, other):
    #         ret = self.value | other.value
    #         return self._reflect(ret)
    #
    #     def _reflect(self, value):
    #         d = dict(zip(SerType.__dict__.values(), SerType.__dict__.keys()))
    #         return getattr(SerType, d[value])
    r = SerType.SER_DISK | SerType.SER_GETHASH
    print(type(r))

    s = PyDataStream()
    s2 = s.copy()
    s.stream_in(1, in_type='int').stream_in(100, in_type='uint256')
    print(s.stream_out(out_type='int'))
    # print(s.stream_out(out_type='uint256'))
    s2.stream_in([1, 2, 3], in_type="int")
    s3 = s2.copy()
    print(repr(str(s)))
    print(s.tell())
    print(repr(str(s2)))
    s2.stream_out(out_type="list", cls=b"int")
    print(s2.tell())
    print(repr(str(s3)))
    print(s3.tell())
    # print(repr(s.stream_out(out_type="list", cls=b"int")))

    print(repr(ser_uint64(0)))

    s = PyDataStream('12345678123456')
    s.read(3)
    s.read(1)
    s.write("123")
    # s.erase(10)
    # s.erase(5)
    print s[:]
    pass


if __name__ == "__main__":
    main()

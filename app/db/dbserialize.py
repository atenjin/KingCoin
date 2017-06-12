#!/usr/bin/env python  
# -*- coding: utf-8 -*-
from json import dumps, loads

from app.config import VERSION
from app.base.serialize import *


#
# class DataStream2(object):
#     @class_params_check(serialize.SerType, str)
#     def __var_init(self, nTypeIn, nVersionIn=VERSION):
#         self.nType = nTypeIn
#         self.nVersion = nVersionIn
#
#     def __init__(self, stream='', nTypeIn=0, nVersionIn=VERSION):
#         if (not isinstance(stream, str)) or (not isinstance(stream, bytearray)):
#             raise Exception("params_chack: invalid parameters in DataStream __init__ for" + stream)
#         self.__vch = bytearray(stream)
#         self.__var_init(nTypeIn, nVersionIn)
#
#     def __add__(self, other):
#         assert isinstance(other, DataStream), "params_chack: invalid parameters in DataStream __add__ for" + other
#         assert self.nType != other.nType, "second item's nType not equal to first item"
#         return DataStream(self.__vch + other.__vch, self.nType, self.nVersion)
#
#     def __iadd__(self, other):
#         assert isinstance(other, DataStream), "params_chack: invalid parameters in DataStream __add__ for" + other
#         assert self.nType == other.nType, "second item's nType not equal to first item"
#         self.__vch += other.__vch
#         return self
#
#     @class_params_check(int)
#     def __getitem__(self, item):
#         return self.__vch[item]
#
#     def __iter__(self):
#         it = iter(self.__vch)
#         return it
#
#     def __len__(self):
#         return len(self.__vch)
#
#     def empty(self):
#         return len(self.__vch) == 0
#
#     def clear(self):
#         self.__vch = bytearray()
#
#     def serialize(self):
#         pass
#
#     @class_params_check(int, object)
#     def insert(self, index, other):
#         assert isinstance(other, DataStream), "params_chack: invalid parameters in DataStream __add__ for" + other
#         self.__vch[index:index] = other.__vch
#
#     def erase(self, index):
#         del self.__vch[index]
#
#     def __str__(self):
#         return str(self.__vch)
#
#     pass


class DataStream(Serializable):
    def __init__(self, data=None):
        self.__data = data

    def serialize(self, nType=0, nVersion=VERSION):
        if isinstance(self.__data, str):
            return dumps(self.__data.decode('latin1'))
        if isinstance(self.__data, tuple):
            if isinstance(self.__data[1], (str, unicode)):
                self.__data = (self.__data[0], self.__data[1].decode('latin1'))

        return dumps(self.__data)

    def deserialize(self, f, nType=0, nVersion=VERSION):
        self.__data = loads(f)
        if isinstance(self.__data, (unicode, str)):
            self.__data = self.__data.encode('latin1')
            return self.__data
        if isinstance(self.__data, (list, tuple)):
            if isinstance(self.__data[1], (unicode, str)):
                self.__data = [self.__data[0], self.__data[1].encode('latin1')]

        return self.__data

    def get_data(self):
        return self.__data if self.__data else None

    def get_data_size(self):
        return len(self.serialize())


class PyAutoFile(object):
    def __init__(self, filenew=None, szmode=None, typein=SerType.SER_DISK, versionin=VERSION):
        if type(filenew) is str:
            self._file = open(filenew, szmode)
        else:
            self._file = filenew
        self.nType = typein
        self.nVersion = versionin
        pass

    def __del__(self):
        self.close()

    def close(self):
        if not hasattr(self, "_file"):
            return
        if self._file is not None and not self._file.closed:
            self._file.close()
        self._file = None

    def write(self, s):
        if self._file is None:
            raise RuntimeError("file is None!")
        self._file.write(s)

    def read(self, nbytes=-1):
        if self._file is None:
            raise RuntimeError("file is None!")
        return self._file.read(nbytes)

    def seek(self, offset, whence=0):
        self._file.seek(offset, whence)

    def tell(self):
        return self._file.tell()

    def read_version(self):
        self.nVersion = int(self.stream_out())
        return self.nVersion

    def write_version(self):
        self.stream_in(str(self.nVersion))

    def release_file(self):
        f = self._file
        self._file = None
        return f

    def stream_out(self, out_type="str", cls=None):
        """

        :return:
        :rtype str
        """
        if self._file is None:
            raise RuntimeError("file is None!")
        return Unserialize(self._file, out_type, cls, nType=self.nType, nVersion=self.nVersion)

    def stream_in(self, obj, in_type=None):
        """

        :param s:
        :type s: str
        :return:
        """
        Serialize(self._file, obj, in_type, nType=self.nType, nVersion=self.nVersion)
        return self

    def get_serialize_size(self, s):
        return GetSerializeSize(s)

    pass


def main():
    pass


if __name__ == '__main__':
    main()

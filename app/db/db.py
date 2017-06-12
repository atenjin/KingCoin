#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bsddb
import os
import inspect

from app import context as ctx
from app.config import strAppDir, strLogDir, DBVERSION
from app.utils.baseutil import Singleton, class_params_check
from dbserialize import DataStream
from app.base import serialize


class PyDBInit(Singleton):
    f_db_env = False
    dict_file_use_count = dict()
    db_map = dict()

    def __init__(self):
        if hasattr(self, "_created") and self._created:
            return
        self._created = True
        self.dbenv = bsddb.db.DBEnv()

        if not os.path.isdir(strLogDir):
            os.mkdir(strLogDir)
        print "dbenv.open strAppDir=%s" % strAppDir

        self.dbenv.set_lg_dir(strLogDir)
        self.dbenv.set_lg_max(10000000)
        self.dbenv.set_lk_max_locks(10000)
        self.dbenv.set_lk_max_objects(10000)
        # self.dbenv.set_errfile(open("db.log", "a"))

        self.dbenv.open(strAppDir,
                        bsddb.db.DB_CREATE |
                        bsddb.db.DB_INIT_LOCK |
                        bsddb.db.DB_INIT_LOG |
                        bsddb.db.DB_INIT_MPOOL |
                        bsddb.db.DB_INIT_TXN |
                        bsddb.db.DB_THREAD |
                        bsddb.db.DB_PRIVATE |
                        bsddb.db.DB_RECOVER,
                        0660)
        PyDBInit.f_db_env = True

    def __getenv(self):
        if hasattr(self, "dbenv"):
            return self.dbenv
        return None

    @staticmethod
    def getenv():
        return PyDBInit().__getenv()

    def __destroy_env(self):
        keys = PyDBInit.db_map.keys()
        for i in keys:
            PyDBInit.db_map[i].close()
        PyDBInit.db_map = dict()

        if hasattr(self, "dbenv") and self.dbenv is not None:
            self.dbenv.close()
            PyDBInit.f_db_env = False
            print "dbenv is destroyed"

    @staticmethod
    def destroy_env():
        return PyDBInit().__destroy_env()

    pass


class PyDB(object):
    DB_SET_RANGE = bsddb.db.DB_SET_RANGE
    Version = DBVERSION

    @class_params_check(str, str, bool)
    def __init__(self, szfile, szmode, f_txn):
        self._db = None
        self.strFile = ''
        self.__txn_list = []
        self.open = False
        self.first_init = False

        if not szfile:
            return

        n_flags = bsddb.db.DB_THREAD

        f_create = szmode.find("c") != -1
        f_readonly = (szmode.find('+') == -1) and (szmode.find('w') == -1)
        if f_create:
            n_flags |= bsddb.db.DB_CREATE
            filename = strAppDir + '/' + szfile
            if not os.path.exists(filename):
                self.first_init = True
        elif f_readonly:
            n_flags |= bsddb.db.DB_RDONLY

        if not f_readonly or f_txn:
            n_flags |= bsddb.db.DB_AUTO_COMMIT

        with ctx.db_mutex:
            dbenv = PyDBInit.getenv()
            self._db = bsddb.db.DB(dbenv, 0)
            self._db.open(filename=szfile,  # Filename
                          dbname="main",  # Logical db name
                          dbtype=bsddb.db.DB_BTREE,  # Database type
                          flags=n_flags,  # Flags
                          mode=0660)  # mode=0660
            self.strFile = szfile

            if self.strFile in PyDBInit.dict_file_use_count:
                PyDBInit.dict_file_use_count[self.strFile] += 1
            else:
                PyDBInit.dict_file_use_count[self.strFile] = 0
            PyDBInit.db_map[hash(self)] = self

            self.open = True
            if f_create and not self._exists("version"):
                self.write_version(DBVERSION)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            return False
        self._db.sync()
        self.close()
        return True

    def _read(self, key, value=None, raw=False):
        """

        :param key: a Serializable class or basic build-in type
        :type key: serialize.Serializable  | Any
        :param value: a Serializable class or class type, None return raw str
        :type value: serialize.Serializable  | type
        :return: str or class instance (Serializable or DataStream)
        :rtype: str | serialize.Serializable | DataStream | any
        """
        if not isinstance(key, serialize.Serializable):
            if not raw:
                key = DataStream(key)
        sk = key.serialize(serialize.SerType.SER_DISK, nVersion=PyDB.Version)
        ssvalue_data = self._db.get(sk, default=None, txn=self.get_txn())

        if ssvalue_data is None:
            return None

        # 在没有传入value 的时候会直接返回原始的 raw 字符串，可以在函数外面再处理
        if value is not None:
            if inspect.isclass(value):  # auto new the class instance
                value = value()
            value.deserialize(ssvalue_data, nType=serialize.SerType.SER_DISK, nVersion=PyDB.Version)
        else:
            value = DataStream().deserialize(ssvalue_data, nType=serialize.SerType.SER_DISK, nVersion=PyDB.Version)
        return value

    def _write(self, key, value, f_overwrite=True, raw=False):
        """

        :param key: a Serializable class or basic type
        :type key: Any | Serializable
        :param value: a Serializable class or basic type
        :type value: Serializable  | Any
        :param f_overwrite: mark if orverwrite
        :type f_overwrite: bool
        :return: None
        """
        if not isinstance(key, serialize.Serializable):
            if not raw:
                key = DataStream(key)
        if not isinstance(value, serialize.Serializable):
            if not raw:
                value = DataStream(value)

        if self._db is None:
            return
        sk = key.serialize(serialize.SerType.SER_DISK, nVersion=PyDB.Version)
        sv = value.serialize(serialize.SerType.SER_DISK, nVersion=PyDB.Version)

        self._db.put(sk, sv, txn=self.get_txn(), flags=(0 if f_overwrite else bsddb.db.DB_NOOVERWRITE))
        self._db.sync()

    def _erase(self, key, raw=False):
        """

        :param key: a Serializable class or basic type
        :type key: Any | Serializable
        :return: True->success False->fail
        :rtype: bool
        """
        if not isinstance(key, serialize.Serializable):
            if not raw:
                key = DataStream(key)
        if self._db is None:
            return False
        s = key.serialize(serialize.SerType.SER_DISK, nVersion=PyDB.Version)
        ret = 0
        try:
            self._db.delete(s, txn=self.get_txn())
        except bsddb.db.DBNotFoundError, e:
            ret = bsddb.db.DB_NOTFOUND
        return ret == 0

    def _exists(self, key):
        """

        :param key: a Serializable class or basic type
        :type key: Any | Serializable
        :return: True->success False->fail
        :rtype: bool
        """
        if not isinstance(key, serialize.Serializable):
            key = DataStream(key)
        if self._db is None:
            return False
        s = key.serialize(serialize.SerType.SER_DISK, nVersion=PyDB.Version)
        return self._db.exists(s, txn=self.get_txn())

    def _get_cursor(self):
        if self._db is None:
            return None
        return self._db.cursor()

    # @class_params_check(object, serialize.Serializable, serialize.Serializable, int)
    def read_at_cursor(self, cursor, sskey=None, ssvalue=None, flags=bsddb.db.DB_NEXT):
        if flags == bsddb.db.DB_SET or flags == bsddb.db.DB_SET_RANGE \
                or flags == bsddb.db.DB_GET_BOTH or flags == bsddb.db.DB_GET_BOTH_RANGE:
            sk = None
        elif sskey is not None:
            if not isinstance(sskey, serialize.Serializable):
                sskey = DataStream(sskey)
            sk = sskey.serialize(serialize.SerType.SER_DISK, nVersion=PyDB.Version)

        if flags == bsddb.db.DB_GET_BOTH or flags == bsddb.db.DB_GET_BOTH_RANGE:
            sv = None
        elif ssvalue is not None:
            if not isinstance(ssvalue, serialize.Serializable):
                ssvalue = DataStream(ssvalue)
            sv = ssvalue.serialize(serialize.SerType.SER_DISK, nVersion=PyDB.Version)
        ret = cursor.get(flags=flags)
        if ret is None:
            return None

        if sskey is not None:
            sskey.deserialize(ret[0], serialize.SerType.SER_DISK)
        else:
            sskey = ret[0]
        if ssvalue is not None:
            ssvalue.deserialize(ret[1], serialize.SerType.SER_DISK)
        else:
            ssvalue = ret[1]

        return sskey, ssvalue

    def read_datas(self, key=None, value=None, keycls=None, valcls=None, types=None, flags=bsddb.db.DB_NEXT):
        if types is None:
            types = list()
        cursor = self._get_cursor()
        if cursor is None:
            return None

        if key:
            if not isinstance(key, serialize.Serializable):
                key = DataStream(key)
            sskey = key.serialize(serialize.SerType.SER_DISK)
        else:
            sskey = ''
        if value:
            if not isinstance(value, serialize.Serializable):
                value = DataStream(value)
            ssvalue = value.serialize(serialize.SerType.SER_DISK)
        else:
            ssvalue = ''

        if flags == bsddb.db.DB_SET:
            cursor.set(key=sskey, flags=bsddb.db.DB_SET)
        elif flags == bsddb.db.DB_SET_RANGE:
            cursor.set_range(key=sskey, flags=bsddb.db.DB_SET_RANGE, dlen=-1, doff=-1)
        elif flags == bsddb.db.DB_GET_BOTH:
            cursor.set_both(key=sskey, data=ssvalue, flags=bsddb.db.DB_GET_BOTH)
        elif flags == bsddb.db.DB_GET_BOTH_RANGE:
            cursor.set_both(key=sskey, data=ssvalue, flags=bsddb.db.DB_GET_BOTH_RANGE)

        key_types = dict()
        for t in types:
            if isinstance(t, tuple):
                key_types[t[0]] = t[1]
            else:
                key_types[t] = None
        keys = key_types.keys()

        ret_list = list()
        while True:
            ret = cursor.next()
            if ret is None:
                break

            sskey = ret[0]
            ssvalue = ret[1]
            if keycls is None and valcls is None:
                key = DataStream().deserialize(sskey)
                if types:
                    if isinstance(key, list):
                        k_type = key[0]
                    else:
                        k_type = key

                    if k_type not in keys:
                        continue
                    cls_type = key_types[k_type]
                    if cls_type is None:
                        value = DataStream().deserialize(ssvalue, nType=serialize.SerType.SER_DISK)
                    else:
                        value = cls_type()
                        value.deserialize(ssvalue, nType=serialize.SerType.SER_DISK)
                else:
                    value = ssvalue
            elif issubclass(keycls, serialize.Serializable) and issubclass(valcls, serialize.Serializable):
                key = keycls()
                key.deserialize(sskey, nType=serialize.SerType.SER_DISK)

                value = valcls()
                value.deserialize(sskey, nType=serialize.SerType.SER_DISK)
            else:
                return None

            ret_list.append((key, value))
        return ret_list

    def get_txn(self):
        if self.__txn_list:
            return self.__txn_list[-1]
        else:
            return None

    def txn_begin(self):
        if self._db is None:
            return False
        tx = PyDBInit.getenv().txn_begin(self.get_txn(), 0)
        self.__txn_list.append(tx)
        return True

    def txn_commit(self):
        if self._db is None:
            return False
        if not self.__txn_list:
            return False
        txn = self.__txn_list.pop()
        ret = txn.commit()
        # TODO for txn_commit result
        print "txn_commit ret", ret
        return ret == 0

    def txn_abort(self):
        if self._db is None:
            return False
        if not self.__txn_list:
            return False
        txn = self.__txn_list.pop()
        return txn.abort() == 0

    def read_version(self, fromdb=True):
        if fromdb is False:
            return PyDB.Version
        s = DataStream()
        self._read("version", s)
        return s.get_data()

    def write_version(self, version):
        self._write("version", DataStream(version))
        PyDB.Version = version

    def close(self):
        if self.open:
            self._db.close()
            self.open = False
            PyDBInit.dict_file_use_count[self.strFile] -= 1
            PyDBInit.db_map.pop(hash(self), None)  # del key

    pass


def main():
    # wallet_db = PyWalletDB()
    # wallet_db.txn_begin()
    # wallet_db.txn_commit()
    # wallet_db.close()
    # # print wallet_db.read_version()
    # # wallet_db.close()
    # PyDBInit.destroy_env()
    pass


if __name__ == '__main__':
    main()

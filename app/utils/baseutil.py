#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import functools
import os
import struct

__all__ = [
    "params_check", "class_params_check", "singleton", "Singleton", "mutex"
]


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance


def class_params_check(*types, **kwtypes):
    """
       check the parameters of a class function, usage: @class_params_check(int, str, (int, str), key1=list, key2=(list, tuple))
    """

    def _decoration(func):
        @functools.wraps(func)
        def _inner(*args, **kwargs):
            result = [isinstance(_param, _type) for _param, _type in zip(args[1:], types)]
            assert all(result), "params_chack: invalid parameters in " + func.__name__
            result = [isinstance(kwargs[_param], kwtypes[_param]) for _param in kwargs if _param in kwtypes]
            # print result
            assert all(result), "params_chack: invalid parameters in " + func.__name__
            return func(*args, **kwargs)

        return _inner

    return _decoration


def params_check(*types, **kwtypes):
    """
    check the parameters of a function, usage: @params_chack(int, str, (int, str), key1=list, key2=(list, tuple))
    """

    def _decoration(func):
        @functools.wraps(func)
        def _inner(*args, **kwargs):
            result = [isinstance(_param, _type) for _param, _type in zip(args, types)]
            assert all(result), "params_chack: invalid parameters in " + func.__name__
            result = [isinstance(kwargs[_param], kwtypes[_param]) for _param in kwargs if _param in kwtypes]
            # print result
            assert all(result), "params_chack: invalid parameters in " + func.__name__
            return func(*args, **kwargs)

        return _inner

    return _decoration


def get_app_dir(dir_name):
    if os.getenv("APPDATA"):
        str_dir = os.getenv("APPDATA") + os.sep + dir_name
    elif os.getenv("USERPROFILE"):
        str_app_dir = os.getenv("USERPROFILE") + os.sep + "Application Data"
        if not os.path.isdir(str_app_dir):
            os.mkdir(str_app_dir)
        str_dir = str_app_dir + os.sep + dir_name
    elif os.path.expanduser('~'):
        str_dir = os.path.expanduser('~') + os.sep + dir_name
    else:
        raise Exception("can't find default path for user home or appdata path. You'd better input a specified path")

    if not os.path.isdir(str_dir):
        os.mkdir(str_dir)
    return str_dir


def get_rand(nmax):
    if nmax == 0:
        return 0
    # return deser_uint64(StringIO(os.urandom(8))) % nmax
    return struct.unpack(b"<Q", os.urandom(8))[0] % nmax


def rand_bytes(n):
    return os.urandom(n)


def main():
    class TestA(Singleton):
        def __init__(self, a):
            if hasattr(self, "_created") and self._created:
                return
            self._created = True

            print 'init a=', a
            self.a = a

    f = TestA(1)
    l = TestA(2)
    f.a = 3
    print l.a
    pass


if __name__ == '__main__':
    main()

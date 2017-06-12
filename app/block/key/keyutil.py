#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import hashlib
# from http://www.nightmare.com/rushing/python/ecdsa.py
import ctypes
import platform
import os

__all__ = ["ssl", "pubkey_to_addr"]

ssl = None
_sysstr = platform.system()


def check_result(val, func, args):
    if val == 0:
        raise ValueError
    else:
        return ctypes.c_void_p(val)


try:
    if _sysstr == "Windows":
        # ssl = ctypes.cdll.LoadLibrary("B:\\Programming\\Libs\\c_cpp\\OpenSSL\\Win32OpenSSL-1_0_2k\\bin\\libeay32")
        ssl = ctypes.cdll.LoadLibrary(os.getcwd() + '\\libs\\libeay32')
        print "Windows Platform load ssl successful"
    elif _sysstr == "Linux":
        ssl = ctypes.cdll.LoadLibrary(ctypes.cdll.find_library('ssl'))
        print "Linux Platform"
    else:
        print "Other System"
        raise NotImplementedError("unsupport platform")

    ssl.EC_KEY_new_by_curve_name.restype = ctypes.c_void_p
    ssl.EC_KEY_new_by_curve_name.errcheck = check_result
except OSError, e:
    print e
    # TODO fix error message and add log
    raise NotImplementedError("you must install latest openssl and config path to PATH env vars")


def base58CheckEncode(payload):  # payload is pri key
    # add 4-byte hash check to the end
    s = payload
    # checksum （所谓附加校验码，就是对私钥经过2次SHA-256运算，取两次哈希结果的前四字节），
    checksum = hashlib.sha256(hashlib.sha256(s).digest()).digest()[0:4]
    # 后面添加压缩标志和附加校验码
    result = str(s + checksum)  # result = version + pri_key + checksum
    # 关于countLeadingChars wiki上有说明 保留作leading zero用的
    leadingZeros = countLeadingChars(result, '\0')
    # leadingZeros + hash(hash(version + pri_key + checksum))
    return '1' * leadingZeros + base58encode(base256decode(result))


def base58CheckDecode(s):
    leadingOnes = countLeadingChars(s, '1')
    try:
        s = base256encode(base58decode(s))
    except Exception, e:
        print "base58CheckDecode ERROR for %s!" % s
        return None
    result = '\0' * leadingOnes + s[:-4]
    chk = s[-4:]
    checksum = hashlib.sha256(hashlib.sha256(result).digest()).digest()[0:4]
    if chk != checksum:
        return None
    return result
    # version = result[0]
    # return result[1:], version


_b58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def base58encode(n):
    result = ''
    while n > 0:
        result = _b58[n % 58] + result
        n /= 58
    return result


def base256encode(n):
    result = ''
    while n > 0:
        result = chr(n % 256) + result
        n /= 256
    return result


def base58decode(s):
    result = 0
    for i in range(0, len(s)):
        result = result * 58 + _b58.index(s[i])
    return result


def base256decode(s):
    result = 0
    for c in s:
        result = result * 256 + ord(c)
    return result


def countLeadingChars(s, ch):
    count = 0
    for c in s:
        if c == ch:
            count += 1
        else:
            break
    return count


def main():
    pass


if __name__ == '__main__':
    main()

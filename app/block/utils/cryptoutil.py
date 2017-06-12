#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import hashlib

from app.base.serialize import deser_uint160, deser_uint256


# return uint256
def Hash(s, s2=None, s3=None, out_type=None):
    if s2 is not None:
        s += s2
    if s3 is not None:
        s += s3
    h = hashlib.sha256(hashlib.sha256(s).digest())
    if out_type == 'hex':
        return h.hexdigest()
    digest = h.digest()
    if out_type == 'str':
        return digest
    return deser_uint256(digest)


Hash256 = Hash


# return uint160
def Ripemd160(v, output_type=None):
    h = hashlib.new('ripemd160')
    h.update(v)
    if output_type == 'hex':
        return h.hexdigest()

    digest = h.digest()
    if output_type == 'str':
        return digest
    return deser_uint160(digest)


# return uint160
def Sha1(v, output_type=None):
    h = hashlib.sha1(v)
    if output_type == 'hex':
        h.hexdigest()
    digest = h.digest()
    if output_type == 'str':
        return digest
    return deser_uint160(digest)


# return uint256
def Sha256(v, output_type=None):
    h = hashlib.sha256(v)
    if output_type == 'hex':
        h.hexdigest()
    digest = h.digest()
    if output_type == 'str':
        return digest
    return deser_uint256(digest)


# return uint160
def Hash160(s, out_type=None):
    h = hashlib.new('ripemd160')
    h.update(hashlib.sha256(s).digest())
    if out_type == 'hex':
        return h.hexdigest()
    digest = h.digest()
    if out_type == 'str':
        return digest
    return deser_uint160(digest)


def main():
    s1 = b'\x01\x02\03'
    s2 = b'\x01\x02\03'
    r = Hash(s1, s2, out_type='str')
    print (repr(r))
    pass


if __name__ == '__main__':
    main()

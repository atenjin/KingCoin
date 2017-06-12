#!/usr/bin/env python  
# -*- coding: utf-8 -*-
from app import config as cfg, context as ctx
from app.base import serialize
from app.block.key import PyKey, keyutil
from app.block.utils import cryptoutil
from app.block.tx.tx import PyWalletDB
from app.utils.baseutil import params_check


##########
# map keys
##

@params_check(PyKey)
def add_key(py_key, szmode="r+"):
    with ctx.dictKeysLock:
        pub_key = py_key.get_pubkey()
        pri_key = py_key.get_prikey()
        ctx.dictKeys[pub_key] = pri_key
        ctx.dictPubKeys[cryptoutil.Hash160(pub_key, "str")] = pub_key

    with PyWalletDB(szmode) as walletdb:
        walletdb.write_key(pub_key, pri_key)


def generate_new_key():
    py_key = PyKey()
    py_key.make_new_key()
    if not add_key(py_key):
        raise RuntimeError('generate_new_key() : AddKey failed')
    return py_key.get_pubkey()


@params_check(str)
def pubkey_to_addr(s, version=cfg.ADDRESSVERSION):
    assert len(s) == cfg.PUBLIC_KEY_SIZE or len(s) == cfg.PUBLIC_KEY_COMPRESSED_SIZE, \
        'the len of pub key must be %d or %d' % (cfg.PUBLIC_KEY_SIZE, cfg.PUBLIC_KEY_COMPRESSED_SIZE)
    return hash160_to_addr(cryptoutil.Hash160(s, out_type="str"), version)


def hash160_to_addr(var_hash160, version=cfg.ADDRESSVERSION):
    # 在公钥的hash前面加上版本号
    # add 1-byte version number to the front
    var_str = version + var_hash160
    return keyutil.base58CheckEncode(var_str)


def addr_to_hash160(addr, onlyhash=False, out_type="str"):
    """

    :param addr:
    :return: (hash160, version) or None
    :rtype tuple | None
    """
    ret = keyutil.base58CheckDecode(addr)
    if ret is None:
        return None
    if onlyhash:
        version = ret[0]
        if out_type == "str":
            return ret[1:] if version <= cfg.ADDRESSVERSION else None
        else:
            return serialize.deser_uint160(ret[1:]) if version <= cfg.ADDRESSVERSION else None
    return ret[1:], ret[0]


def is_valid_address(addr):
    ret = addr_to_hash160(addr)
    if ret is None:
        return False
    version = ret[1]
    return True if version <= cfg.ADDRESSVERSION else False


def set_address_book_name(str_addr, str_name, szmode='r+'):
    with PyWalletDB(szmode) as walletdb:
        walletdb.write_name(str_addr, str_name=str_name)
    pass


def main():
    pass


if __name__ == '__main__':
    main()

#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import binascii

from app.base import serialize
from app.block.tx.script import SignType


def main():
    hash_type = SignType.SIGHASH_ALL
    print binascii.hexlify(serialize.ser_uchar(hash_type))

    pass


if __name__ == '__main__':
    main()

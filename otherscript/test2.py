#!/usr/bin/env python  
# -*- coding: utf-8 -*-

from app.block.utils import cryptoutil
from app.base.serialize import PyDataStream


def test_datastream():
    s = PyDataStream()
    s.stream_in(1, "int")
    s.stream_in(2, "int")

    s2 = PyDataStream()
    s2.stream_in(s)

    pass


def main():
    # s = cryptoutil.Hash("123", out_type='str')
    # print len(s)
    test_datastream()
    pass


if __name__ == '__main__':
    main()

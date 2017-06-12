#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import os
import requests
import re

from app.config import CENT


def format_money(n, fPlus=False):
    n /= CENT
    s = "%d.%02d" % (abs(n) / 100, abs(n) % 100)
    # print "format_money: balance:", s
    s_size = len(s)
    for i in range(6, s_size, 4):
        if s[s_size - i - 1].isdigit():
            s = s[:s_size - i] + ',' + s[s_size - i:]
            s_size += 1
    if n < 0:
        s = '-' + s
    elif fPlus and n > 0:
        s = '+' + s
    return s


def parse_money(s):
    s.isdigit()
    cents = 0
    whole = ''
    s = s.strip()
    try:
        i = 0
        size = len(s)
        while i < size:
            if s[i] == ',' and i > 0 and s[i - 1].isdigit() and s[i + 1:i + 4].isdigit():
                i+=1
                continue
            if s[i] == '.':
                i += 1
                if not s[i:i + 2].isdigit():
                    return None
                cents = int(s[i:i + 2])
                if cents < 0 or cents > 99:
                    return None
                i += 2
                break
            if s[i] == ' ':
                break

            if not s[i].isdigit():
                return None
            whole += s[i]
            i += 1
            pass  # end while
        if len(whole) > 17:
            return None
        whole = int(whole)
        value = whole * 100 + cents
        if value / 100 != whole:
            return False
        value *= CENT
        return value
    except Exception, e:
        return None
        pass
    pass


def external_IP():
    r = requests.get("http://1212.ip138.com/ic.asp")
    if 2 <= r.status_code % 100 <= 3:
        ret = re.search("\[(.*)\]", r.text)
        if ret is None:
            return None
        return ret.group(1)
    return None


def cur_pwd():
    return os.path.abspath(os.curdir)


def main():
    s = format_money(1234512 * CENT)
    print (s)
    s= "0.01"
    print parse_money(s)
    pass


if __name__ == '__main__':
    main()

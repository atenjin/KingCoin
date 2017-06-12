#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import time
import datetime
from app import context as ctx


def get_time():
    return int(time.time())


def get_adjusted_time():
    return get_time() + ctx.timeOffset


def sleep_msec(msec):
    time.sleep(msec / 1000.0)


setKnown = set()  # ip set
listTimeOffsets = list()  # list<int64>  for time


def add_time_data(ip, time):
    offset_sample = time - get_time()

    # Ignore duplicates
    global setKnown
    if ip in setKnown:
        return
    else:
        setKnown.add(ip)

    # Add data
    global listTimeOffsets
    if not listTimeOffsets:  # is empty
        listTimeOffsets.append(0)

    listTimeOffsets.append(offset_sample)  # add data

    offsets_size = len(listTimeOffsets)
    print ("Added time data, samples %d, ip %s, offset %d (%d minutes)\n" %
           (offsets_size, ip, listTimeOffsets[-1], listTimeOffsets[-1] / 60))

    if offsets_size > 5 and offsets_size % 2 == 1:
        listTimeOffsets.sort()
        median = listTimeOffsets[offsets_size / 2]
        time_offset = median
        if abs(median) > 5 * 60:
            # Only let other nodes change our clock so far before we
            # go to the NTP servers
            ## todo: Get time from NTP servers, then set a flag
            ##    to make sure it doesn't get changed again
            pass
        for n in listTimeOffsets:
            print ("%d" % n)
        print ("|  nTimeOffset = %d  (%d minutes)\n" % (time_offset, time_offset / 60))
    pass  # end func


def get_strftime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def is_24_hour_time():
    return True


def date_time_str(time_in):
    try:
        if is_24_hour_time():
            return datetime.datetime.fromtimestamp(time_in).strftime('%x %H:%M')
        else:
            return datetime.datetime.fromtimestamp(time_in).strftime('%x %l:%M %p')
    except Exception, e:
        return str(time_in)


def main():
    print (get_time())
    pass


if __name__ == '__main__':
    main()

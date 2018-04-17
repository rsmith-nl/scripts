#!/usr/bin/env python3
# file: ntpclient.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2017-11-16 19:33:50 +0100
# Last modified: 2017-11-16 22:11:49 +0100
#

from contextlib import closing
from socket import socket, AF_INET, SOCK_DGRAM
import os
import struct
import time

_query = b'\x1b' + 47 * b'\0'


def get_ntp_time(host="pool.ntp.org", port=123):
    fmt = "!12I"
    with closing(socket(AF_INET, SOCK_DGRAM)) as s:
        s.sendto(_query, (host, port))
        msg, address = s.recvfrom(1024)
    unpacked = struct.unpack(fmt, msg[0:struct.calcsize(fmt)])
    return unpacked[10] + float(unpacked[11]) / 2**32 - 2208988800


if __name__ == "__main__":
    beforetime = time.clock_gettime(time.CLOCK_REALTIME)
    ntptime = get_ntp_time('nl.pool.ntp.org')
    aftertime = time.clock_gettime(time.CLOCK_REALTIME)
    localtime = (beforetime + aftertime) / 2
    if os.geteuid() == 0:
        time.clock_settime(time.CLOCK_REALTIME, ntptime)
        res = 'Time set to NTP time.'
    else:
        res = 'Can not set time: not superuser.'
    print('Local time value:', time.ctime(localtime))
    print('NTP time value:', time.ctime(ntptime))
    print('Local time - ntp time:', localtime - ntptime)
    print(res)

#!/usr/bin/env python3
# file: ntpclient.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2017-11-16 19:33:50 +0100
# Last modified: 2018-05-13T12:15:28+0200
"""Simple NTP query program."""

from contextlib import closing
from datetime import datetime
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
    # It is not guaranteed that the NTP time is *exactly* in the middle of both
    # local times. But it is a reasonable simplification.
    localtime = (beforetime + aftertime) / 2
    if os.geteuid() == 0:
        time.clock_settime(time.CLOCK_REALTIME, ntptime)
        res = 'Time set to NTP time.'
    else:
        res = 'Can not set time: not superuser.'
    diff = localtime - ntptime
    localtime = datetime.fromtimestamp(localtime)
    ntptime = datetime.fromtimestamp(ntptime)
    print('Local time value:', localtime.strftime('%a %b %d %H:%M:%S.%f %Y'))
    print('NTP time value:', ntptime.strftime('%a %b %d %H:%M:%S.%f %Y'))
    print('Local time - ntp time: {:.6f} s'.format(diff))
    print(res)

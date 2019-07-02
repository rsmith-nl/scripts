#!/usr/bin/env python3
# file: statusline-i3.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2019-06-30T22:23:11+0200
# Last modified: 2019-07-03T00:13:37+0200
"""Generate status line for i3 on my machine."""

import ctypes
import ctypes.util
import os
import mmap
import statistics as stat
import struct
import time

__version__ = 1.999

# Low level functions.


def to_int(value):
    """Convert binary sysctl value to integer."""
    return int.from_bytes(value, byteorder='little')


def to_degC(value):
    """Convert binary sysctl value to degree Centigrade."""
    return round(int.from_bytes(value, byteorder='little')/10 - 273.15, 1)


def sysctlbyname(name, buflen=4, convert=None):
    """
    Python wrapper for sysctlbyname(3) on FreeBSD.

    Arguments:
        name (str): Name of the sysctl to query
        buflen (int): Length of the data buffer to use.
        convert: Optional function to convert the data.
    """
    name_in = ctypes.c_char_p(bytes(name, encoding='ascii'))
    oldlen = ctypes.c_size_t(buflen)
    oldlenp = ctypes.byref(oldlen)
    oldp = ctypes.create_string_buffer(buflen)
    rv = libc.sysctlbyname(name_in, oldp, oldlenp, None, ctypes.c_size_t(0))
    if rv != 0:
        raise ValueError(f'sysctlbyname error')
    if convert:
        return convert(oldp.raw[:buflen])
    return oldp.raw[:buflen]


def sysctl(name, buflen=4, convert=None):
    """
    Python wrapper for sysctl(3) on FreeBSD.

    Arguments:
        name: list or tuple of integers.
        buflen (int): Length of the data buffer to use.
        convert: Optional function to convert the data.
    """
    cnt = len(name)
    mib = ctypes.c_int * cnt
    name_in = mib(*name)
    oldlen = ctypes.c_size_t(buflen)
    oldlenp = ctypes.byref(oldlen)
    oldp = ctypes.create_string_buffer(buflen)
    rv = libc.sysctl(
        ctypes.byref(name_in), ctypes.c_uint(cnt), oldp, oldlenp, None, ctypes.c_size_t(0)
    )
    if rv != 0:
        errno = ctypes.get_errno()
        raise ValueError(f'sysctl error: {errno}')
    if convert:
        return convert(oldp.raw[:buflen])
    return oldp.raw[:buflen]


# High level functions

def network():
    global netdata
    cnt = sysctlbyname('net.link.generic.system.ifcount', convert=to_int)
    items = []
    for n in range(1, cnt):
        tm = time.time()
        data = sysctl([4, 18, 0, 2, n, 1], buflen=208)
        name = data[:16].strip(b'\x00').decode('ascii')
        ibytes = to_int(data[120:128])
        obytes = to_int(data[128:138])
        dt = tm - netdata[name][2]
        d_in = int((ibytes - netdata[name][0])/dt)
        d_out = int((obytes - netdata[name][1])/dt)
        netdata[name] = (ibytes, obytes, tm)
        items.append(f'{name}: {d_in}B/{d_out}B')
    return ' '.join(items)


def mail():
    mboxname = '/home/rsmith/Mail/received'
    global lastmail
    newtime = os.stat(mboxname).st_mtime
    if newtime > lastmail['time']:
        with open(mboxname) as mbox:
            mm = mmap.mmap(mbox.fileno(), 0, prot=mmap.PROT_READ)
            start, total = 0, 0
            while True:
                rv = mm.find(b'\n\nFrom ', start)
                if rv == -1:
                    break
                else:
                    total += 1
                    start = rv+7
            start, read = 0, 0
            while True:
                rv = mm.find(b'\nStatus: R', start)
                if rv == -1:
                    break
                else:
                    read += 1
                    start = rv+10
        mailcount = total - read
        lastmail = {'count': mailcount, 'time': newtime}
    else:
        mailcount = lastmail['count']
    return f'Mail: {mailcount}'


def memory():
    suffixes = ('page_count', 'free_count', 'inactive_count', 'cache_count')
    stats = {
        suffix: sysctlbyname(f'vm.stats.vm.v_{suffix}', convert=to_int)
        for suffix in suffixes
    }
    memmax = stats['page_count']
    mem = (memmax - stats['free_count'] - stats['inactive_count'] - stats['cache_count'])
    free = int(100 * mem / memmax)
    return f'RAM: {free}%'


def cpu():
    global cpusage
    temps = [
        sysctlbyname(f'dev.cpu.{n}.temperature', convert=to_degC)
        for n in range(4)
    ]
    T = round(stat.mean(temps))
    resbuf = sysctlbyname('kern.cp_time', buflen=40)
    states = struct.unpack('5L', resbuf)
    # According to /usr/include/sys/resource.h, these are:
    # USER, NICE, SYS, INT, IDLE
    total = sum(states)
    used = total - states[-1]
    frac = int((used - cpusage['used']) / (total - cpusage['total']) * 100)
    cpusage = {'used': used, 'total': total}
    return f'CPU: {frac}%, {T}°C'


def date():
    return time.strftime('%a %Y-%m-%d %H:%M:%S')


def main():
    """
    Entry point for statusline-i3.py
    """
    while True:
        start = time.time()
        items = [network(), mail(), memory(), cpu(), date()]
        print(' | '.join(items))
        end = time.time()
        delta = end - start
        print(f"DEBUG: looptijd = {delta:.2f} s")
        if delta < 1:
            time.sleep(1 - delta)


# Global data
netdata = {'age0': (0, 0, 0), 'rl0': (0, 0, 0)}
lastmail = {'count': -1, 'time': 0}
cpusage = {'used': 0, 'total': 0}
libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)

if __name__ == '__main__':
    main()

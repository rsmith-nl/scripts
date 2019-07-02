#!/usr/bin/env python3
# file: statusline-i3.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2019-06-30T22:23:11+0200
# Last modified: 2019-07-02T02:28:36+0200
"""Generate status line for i3 on my machine."""

import ctypes
import os
import statistics as stat
import struct
import subprocess as sp
import time

__version__ = 1.99

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
        name_in, ctypes.c_int(cnt), oldp, oldlenp, None, ctypes.c_size_t(0)
    )
    if rv != 0:
        raise ValueError(f'sysctl error')
    if convert:
        return convert(oldp.raw[:buflen])
    return oldp.raw[:buflen]


def netstat(interface):
    """Return network statistics for named interface."""
    lines = sp.check_output(['netstat', '-b', '-n', '-I', interface],
                            encoding='ascii').splitlines()
    tm = time.time()
    if len(lines) == 1:
        return None
    items = lines[1].split()
    ibytes = int(items[7])
    obytes = int(items[10])
    return ibytes, obytes, tm


# High level functions

def network():
    global netdata
    ifaces = {'Ext': 'age0', 'Int': 'rl0'}
    items = []
    for desc, i in ifaces.items():
        data = netstat(i)
        if data:
            dt = data[2] - netdata[i][2]
            delta_in = int((data[0] - netdata[i][0])/dt)
            delta_out = int((data[1] - netdata[i][1])/dt)
            netdata[i] = data
            items.append(f'{desc}: {delta_in}B/{delta_out}B')
        else:
            items.append(f'{desc}: 0B/0B')
    return ' '.join(items)


def mail():
    mboxname = '/home/rsmith/Mail/received'
    global lastmail
    newtime = os.stat(mboxname).st_mtime
    if newtime > lastmail['time']:
        with open(mboxname) as mbox:
            lines = mbox.readlines()
        # This is faster than regex.
        read = len([ln for ln in lines if ln.startswith('Status: R')])
        total = len([ln for ln in lines if ln.startswith('From ')])
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
libc = ctypes.CDLL('libc.so.7')

if __name__ == '__main__':
    main()

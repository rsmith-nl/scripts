#!/usr/bin/env python3
# file: statusline-i3.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2019-06-30T22:23:11+0200
# Last modified: 2019-07-03T23:03:42+0200
"""Generate status line for i3 on my machine."""

import ctypes
import ctypes.util
import os
import mmap
import statistics as stat
import struct
import time

# Global data
__version__ = 2.0
libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)

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

    Returns:
        The requested binary data, converted if desired.
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

    Returns:
        The requested binary data, converted if desired.
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

def network(previous):
    """
    Report on bytes in/out for the network interfaces.

    Arguments:
        previous: A dict of {interface: (inbytes, outbytes, time)} or None.

    Returns:
        A new dict of {interface: (inbytes, outbytes, time)}, and a formatted
        string to display.
    """
    cnt = sysctlbyname('net.link.generic.system.ifcount', convert=to_int)
    newdata = {}
    items = []
    for n in range(1, cnt):
        tm = time.time()
        data = sysctl([4, 18, 0, 2, n, 1], buflen=208)
        name = data[:16].strip(b'\x00').decode('ascii')
        ibytes = to_int(data[120:128])
        obytes = to_int(data[128:136])
        # print("DEBUG: ibytes, obytes = ", ibytes, obytes)
        if previous:
            dt = tm - previous[name][2]
            d_in = int((ibytes - previous[name][0])/dt)
            d_out = int((obytes - previous[name][1])/dt)
            items.append(f'{name}: {d_in}B/{d_out}B')
        else:
            items.append(f'{name}: 0B/0B')
        newdata[name] = (ibytes, obytes, tm)
    return newdata, '  '.join(items)


def mail(previous):
    """
    Report unread mail.

    Arguments:
        previous: a 2-tuple (unread, time) from the previous call, or None

    Returns: A new 2-tuple (unread, time) and a string to display.
    """
    mboxname = '/home/rsmith/Mail/received'
    newtime = os.stat(mboxname).st_mtime
    if previous is None or newtime > previous[1]:
        with open(mboxname) as mbox:
            with mmap.mmap(mbox.fileno(), 0, prot=mmap.PROT_READ) as mm:
                start, total = 0, 1  # First mail is not found; it starts on first line...
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
        unread = total - read
        newdata = (unread, newtime)
    else:
        unread = previous[0]
        newdata = previous
    return newdata, f'Mail: {unread}'


def memory():
    """
    Report on the RAM usage on FreeBSD.

    Returns: a formatted string to display.
    """
    suffixes = ('page_count', 'free_count', 'inactive_count', 'cache_count')
    stats = {
        suffix: sysctlbyname(f'vm.stats.vm.v_{suffix}', convert=to_int)
        for suffix in suffixes
    }
    memmax = stats['page_count']
    mem = (memmax - stats['free_count'] - stats['inactive_count'] - stats['cache_count'])
    free = int(100 * mem / memmax)
    return f'RAM: {free}%'


def cpu(previous):
    """
    Report the CPU usage and temperature.

    Argument:
        previous: A 2-tuple (used, total) from the previous run.

    Returns:
        A 2-tuple (used, total) and a string to display.
    """
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
    if previous:
        prevused, prevtotal = previous
        frac = int((used - prevused) / (total - prevtotal) * 100)
    else:
        frac = 0
    return (used, total), f'CPU: {frac}%, {T}°C'


def date():
    """Return the date formatted for display."""
    return time.strftime('%a %Y-%m-%d %H:%M:%S')


def main():
    """
    Entry point for statusline-i3.py
    """
    netdata, _ = network(None)
    maildata, _ = mail(None)
    cpusage, _ = cpu(None)
    time.sleep(0.1)  # Lest we get divide by zero in cpu()
    while True:
        start = time.time()
        netdata, netstr = network(netdata)
        maildata, mailstr = mail(maildata)
        cpusage, cpustr = cpu(cpusage)
        print(' | '.join([netstr, mailstr, memory(), cpustr, date()]))
        end = time.time()
        delta = end - start
        # print(f"DEBUG: cycle time = {delta:.3f} s")
        if delta < 1:
            time.sleep(1 - delta)


if __name__ == '__main__':
    main()

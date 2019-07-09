#!/usr/bin/env python3
# file: statusline-i3.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2019-06-30T22:23:11+0200
# Last modified: 2019-07-10T00:19:29+0200
"""
Generate a status line for i3 on FreeBSD.
"""

from functools import partial
import argparse
import ctypes
import ctypes.util
import mmap
import os
import statistics as stat
import struct
import sys
import time

# Global data
__version__ = '2.2'
libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)

# Low level functions.


def to_int(value):
    """Convert binary sysctl value to integer."""
    return int.from_bytes(value, byteorder='little')


def to_degC(value):
    """Convert binary sysctl value to degree Centigrade."""
    return round(int.from_bytes(value, byteorder='little') / 10 - 273.15, 1)


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
        errno = ctypes.get_errno()
        raise ValueError(f'sysctlbyname error: {errno}')
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
        ctypes.byref(name_in), ctypes.c_uint(cnt), oldp, oldlenp, None,
        ctypes.c_size_t(0)
    )
    if rv != 0:
        errno = ctypes.get_errno()
        raise ValueError(f'sysctl error: {errno}')
    if convert:
        return convert(oldp.raw[:buflen])
    return oldp.raw[:buflen]


def fmt(nbytes):
    """Format network byte amounts."""
    nbytes = int(nbytes)
    if nbytes >= 1000000:
        nbytes /= 1000000
        return f'{nbytes:.1f}MiB'
    if nbytes > 1000:
        nbytes /= 1000
        return f'{nbytes:.1f}kiB'
    return f'{nbytes}B'


def setproctitle(name):
    """
    Change the name of the process

    Arguments:
        name (bytes): the new name for the process.
    """
    fmt = ctypes.c_char_p(b'-%s')
    value = ctypes.c_char_p(name)
    libc.setproctitle(fmt, value)


# High level functions


def network(storage):
    """
    Report on bytes in/out for the network interfaces.

    Arguments:
        storage: A dict of {interface: (inbytes, outbytes, time)} or an empty dict.
            This dict will be *modified* by this function.

    Returns:
        A string to display.
    """
    cnt = sysctlbyname('net.link.generic.system.ifcount', convert=to_int)
    items = []
    for n in range(1, cnt):
        tm = time.time()
        data = sysctl([4, 18, 0, 2, n, 1], buflen=208)
        name = data[:16].strip(b'\x00').decode('ascii')
        if name.startswith('lo'):
            continue
        ibytes = to_int(data[120:128])
        obytes = to_int(data[128:136])
        if storage and name in storage:
            dt = tm - storage[name][2]
            d_in = fmt((ibytes - storage[name][0]) / dt)
            d_out = fmt((obytes - storage[name][1]) / dt)
            items.append(f'{name}: {d_in}/{d_out}')
        else:
            items.append(f'{name}: 0B/0B')
        # Save values for the next run.
        storage[name] = (ibytes, obytes, tm)
    return '  '.join(items)


def mail(storage, mboxname):
    """
    Report unread mail.

    Arguments:
        storage: a dict with keys (unread, time, size) from the previous call or an empty dict.
            This dict will be *modified* by this function.
        mboxname (str): name of the mailbox to read.

    Returns: A string to display.
    """
    stats = os.stat(mboxname)
    if stats.st_size == 0:
        return 'Mail: 0'
    # When mutt modifies the mailbox, it seems to only change the
    # ctime, not the mtime! This is probably releated to how mutt saves the
    # file. See also stat(2).
    newtime = stats.st_ctime
    newsize = stats.st_size
    if not storage or newtime > storage['time'] or newsize != storage['size']:
        with open(mboxname) as mbox:
            with mmap.mmap(mbox.fileno(), 0, prot=mmap.PROT_READ) as mm:
                start, total = 0, 1  # First mail is not found; it starts on first line...
                while True:
                    rv = mm.find(b'\n\nFrom ', start)
                    if rv == -1:
                        break
                    else:
                        total += 1
                        start = rv + 7
                start, read = 0, 0
                while True:
                    rv = mm.find(b'\nStatus: R', start)
                    if rv == -1:
                        break
                    else:
                        read += 1
                        start = rv + 10
        unread = total - read
        # Save values for the next run.
        storage['unread'], storage['time'], storage['size'] = unread, newtime, newsize
    else:
        unread = storage['unread']
    return f'Mail: {unread}'


def memory():
    """
    Report on the RAM usage on FreeBSD.

    Returns: a string to display.
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


def cpu(storage):
    """
    Report the CPU usage and temperature.

    Argument:
        storage: A dict with keys (used, total) from the previous run or an empty dict.
            This dict will be *modified* by this function.

    Returns:
        A string to display.
    """
    temps = [sysctlbyname(f'dev.cpu.{n}.temperature', convert=to_degC) for n in range(4)]
    T = round(stat.mean(temps))
    resbuf = sysctlbyname('kern.cp_time', buflen=40)
    states = struct.unpack('5L', resbuf)
    # According to /usr/include/sys/resource.h, these are:
    # USER, NICE, SYS, INT, IDLE
    total = sum(states)
    used = total - states[-1]
    if storage:
        prevused, prevtotal = storage['used'], storage['total']
        frac = int((used - prevused) / (total - prevtotal) * 100)
    else:
        frac = 0
    # Save values for the next run.
    storage['used'], storage['total'] = used, total
    return f'CPU: {frac}%, {T}°C'


def battery():
    """Return battery condition as a string."""
    # Battery states acc. to /usr/src/sys/dev/acpica/acpiio.h
    lookup = {0: 'on AC', 1: 'discharging', 2: 'charging', 3: 'invalid', 4: 'CRITICAL!'}
    idx = sysctlbyname('hw.acpi.battery.state', convert=to_int)
    state = lookup[idx]
    percent = sysctlbyname('hw.acpi.battery.life', convert=to_int)
    return f'Bat: {percent}% ({state})'


def date():
    """Return the date as a string."""
    return time.strftime('%a %Y-%m-%d %H:%M:%S')


def parse_args(argv):
    """Handle the command line arguments"""
    opts = argparse.ArgumentParser(prog='open', description=__doc__)
    opts.add_argument('-v', '--version', action='version', version=__version__)
    opts.add_argument(
        '-m',
        '--mailbox',
        type=str,
        default=os.environ['MAIL'],
        help="Location of the mailbox (defaults to MAIL environment variable)"
    )
    args = opts.parse_args(argv)
    return args


def hasbattery():
    bat = False
    try:
        if sysctlbyname('hw.acpi.battery.units', convert=to_int) > 0:
            bat = True
    except ValueError:
        pass
    return bat


def main():
    """
    Entry point for statusline-i3.py
    """
    setproctitle(b'statusline-i3')
    maildata = {}
    cpudata = {}
    netdata = {}
    args = parse_args(sys.argv[1:])
    items = [
        partial(network, storage=netdata),
        partial(mail, storage=maildata, mboxname=args.mailbox), memory,
        partial(cpu, storage=cpudata), date
    ]
    if hasbattery():
        items.insert(-1, battery)
    while True:
        start = time.time()
        print(' | '.join(item() for item in items))
        sys.stdout.flush()
        end = time.time()
        delta = end - start
        if delta < 1:
            time.sleep(1 - delta)


if __name__ == '__main__':
    main()

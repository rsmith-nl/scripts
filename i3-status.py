#!/usr/bin/env python3
# file: i3-status.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2019-06-30T22:23:11+0200
# Last modified: 2019-07-01T02:17:52+0200
"""Generate status line for i3 on my machine."""

import os
import statistics as stat
import subprocess as sp
import time

# Low level functions.


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


def vmstats():
    """Return the vm stats."""
    rv = {}
    for ln in sp.check_output(['sysctl', 'vm.stats.vm'], encoding='ascii').splitlines():
        name, count = ln.split()
        rv[name[14:-1]] = int(count)
    return rv


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

# In [12]: %timeit read = len(re.findall('^Status: R', data, flags=re.MULTILINE))
# 381 ms ± 1.13 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
#
# In [13]: %timeit total = len(re.findall('^From ', data, flags=re.MULTILINE))
# 381 ms ± 1.74 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
#
# In [17]: %timeit len([ln for ln in lines if ln.startswith('Status: R')])
# 83.6 ms ± 72.6 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

# In [18]: %timeit len([ln for ln in lines if ln.startswith('From ')])
# 83.9 ms ± 88.9 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)


def mail():
    mboxname = '/home/rsmith/Mail/received'
    global mailcount
    if time.time() - os.stat(mboxname).st_mtime < 1 or mailcount < 0:
        with open(mboxname) as mbox:
            lines = mbox.readlines()
        # This is faster than regex; see above.
        read = len([ln for ln in lines if ln.startswith('Status: R')])
        total = len([ln for ln in lines if ln.startswith('From ')])
        mailcount = total - read
        print("DEBUG: mailcount = ", mailcount)
    return f'Mail: {mailcount}'


def memory():
    stats = vmstats()
    memmax = stats['page_count']
    mem = (memmax - stats['free_count'] - stats['inactive_count'] - stats['cache_count'])
    free = int(100 * mem / memmax)
    return f'RAM: {free}%'


def cpu():
    items = [f'dev.cpu.{n}.temperature' for n in range(4)]
    lines = sp.check_output(['sysctl'] + items, encoding='ascii').splitlines()
    temps = [float(ln.split()[1][:-1]) for ln in lines]
    T = round(stat.mean(temps))

    return f'CPU: %, {T}°C'


def date():
    return time.strftime('%a %Y-%m-%d %H:%M:%S')


# Statistics:
#In [5]: %timeit network()
#156 ms ± 1.34 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
#
#In [6]: %timeit memory()
#77.4 ms ± 118 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
#
#In [7]: %timeit cpu()
#76.3 ms ± 138 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
#
#In [8]: %timeit date()
#4.83 µs ± 12.8 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)


def main():
    """
    Entry point for i3-status.py.
    """
    while True:
        start = time.time()
        items = [network(), mail(), memory(), cpu(), date()]
        print(' | '.join(items))
        end = time.time()
        delta = end - start
        print("DEBUG: delta = ", delta)
        if delta < 1:
            time.sleep(1 - delta)


# Global data
netdata = {'age0': (0, 0, 0), 'rl0': (0, 0, 0)}
mailcount = -1

if __name__ == '__main__':
    main()

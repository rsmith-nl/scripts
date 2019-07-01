#!/usr/bin/env python3
# file: statusline-i3.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2019-06-30T22:23:11+0200
# Last modified: 2019-07-02T01:10:49+0200
"""Generate status line for i3 on my machine."""

import os
import statistics as stat
import subprocess as sp
import time

__version__ = 1.0

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


def mail():
    mboxname = '/home/rsmith/Mail/received'
    global lastmail
    newtime = os.stat(mboxname).st_mtime
    if newtime > lastmail['time']:
        with open(mboxname) as mbox:
            lines = mbox.readlines()
        # This is faster than regex; see above.
        read = len([ln for ln in lines if ln.startswith('Status: R')])
        total = len([ln for ln in lines if ln.startswith('From ')])
        mailcount = total - read
        lastmail = {'count': mailcount, 'time': newtime}
    else:
        mailcount = lastmail['count']
    return f'Mail: {mailcount}'


def memory():
    stats = vmstats()
    memmax = stats['page_count']
    mem = (memmax - stats['free_count'] - stats['inactive_count'] - stats['cache_count'])
    free = int(100 * mem / memmax)
    return f'RAM: {free}%'


def cpu():
    global cpusage
    items = [f'dev.cpu.{n}.temperature' for n in range(4)] + ['kern.cp_time']
    lines = sp.check_output(['sysctl'] + items, encoding='ascii').splitlines()
    temps = [float(ln.split()[1][:-1]) for ln in lines[:-1]]
    T = round(stat.mean(temps))
    states = [int(j) for j in lines[-1].split()[1:]]
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
    Entry point for i3-status.py.
    """
    while True:
        start = time.time()
        items = [network(), mail(), memory(), cpu(), date()]
        print(' | '.join(items))
        end = time.time()
        delta = end - start
        # print(f"DEBUG: looptijd = {delta:.2f} s")
        if delta < 1:
            time.sleep(1 - delta)


# Global data
netdata = {'age0': (0, 0, 0), 'rl0': (0, 0, 0)}
lastmail = {'count': -1, 'time': 0}
cpusage = {'used': 0, 'total': 0}

if __name__ == '__main__':
    main()

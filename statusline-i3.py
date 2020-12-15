#!/usr/bin/env python
# file: statusline-i3.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2019-06-30T22:23:11+0200
# Last modified: 2020-11-19T12:33:40+0100
"""
Generate a status line for i3 on FreeBSD.
"""

import argparse
import ctypes
import ctypes.util
import functools as ft
import logging
from logging.handlers import SysLogHandler
import mmap
import os
import statistics as stat
import struct
import sys
import time
import traceback

# Global data
__version__ = "2020.04.01"
libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)


def main():
    """
    Entry point for statusline-i3.py
    """
    args = setup()
    mailboxes = {name: {} for name in args.mailbox.split(":")}
    cpudata = {}
    netdata = {}
    items = [
        ft.partial(network, storage=netdata),
        ft.partial(mail, mailboxes=mailboxes),
        memory,
        ft.partial(cpu, storage=cpudata),
        date,
    ]
    if hasbattery():
        items.insert(-1, battery)
    logging.info("starting")
    sys.stdout.reconfigure(line_buffering=True)  # Flush every line.
    rv = 0
    # Run
    try:
        while True:
            start = time.monotonic()
            print(" | ".join(item() for item in items))
            end = time.monotonic()
            delta = end - start
            if delta < 1:
                time.sleep(1 - delta)
    except Exception:
        # Occasionally, statusline-i3 dies, and I don't know why.
        # This should catch what happens next time. :-)
        logging.error("caught exception: " + traceback.format_exc())
        rv = 2
    except KeyboardInterrupt:
        # This is mainly for when testing from the command-line.
        logging.info("caught KeyboardInterrupt; exiting")
    return rv


def setup():
    """Configure logging, process command-line arguments."""
    syslog = SysLogHandler(address="/var/run/log", facility=SysLogHandler.LOG_LOCAL3)
    pid = os.getpid()
    syslog.ident = f"statusline-i3[{pid}]: "
    logging.basicConfig(
        level="INFO", format="%(levelname)s: %(message)s", handlers=(syslog,)
    )
    setproctitle(b"statusline-i3")
    opts = argparse.ArgumentParser(prog="open", description=__doc__)
    opts.add_argument("-v", "--version", action="version", version=__version__)
    opts.add_argument(
        "-m",
        "--mailbox",
        type=str,
        default=os.environ["MAIL"],
        help="Location of the mailboxes. One or more mailbox names separated by ‘:’",
    )
    return opts.parse_args(sys.argv[1:])


# Low level functions.


def to_int(value):
    """Convert binary sysctl value to integer."""
    return int.from_bytes(value, byteorder="little")


def to_degC(value):
    """Convert binary sysctl value to degree Centigrade."""
    return round(int.from_bytes(value, byteorder="little") / 10 - 273.15, 1)


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
    name_in = ctypes.c_char_p(bytes(name, encoding="ascii"))
    oldlen = ctypes.c_size_t(buflen)
    oldlenp = ctypes.byref(oldlen)
    oldp = ctypes.create_string_buffer(buflen)
    rv = libc.sysctlbyname(name_in, oldp, oldlenp, None, ctypes.c_size_t(0))
    if rv != 0:
        errno = ctypes.get_errno()
        raise ValueError(f"sysctlbyname error: {errno}")
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
        ctypes.byref(name_in),
        ctypes.c_uint(cnt),
        oldp,
        oldlenp,
        None,
        ctypes.c_size_t(0),
    )
    if rv != 0:
        errno = ctypes.get_errno()
        raise ValueError(f"sysctl error: {errno}")
    if convert:
        return convert(oldp.raw[:buflen])
    return oldp.raw[:buflen]


def setproctitle(name):
    """
    Change the name of the process

    Arguments:
        name (bytes): the new name for the process.
    """
    fmt = ctypes.c_char_p(b"-%s")
    value = ctypes.c_char_p(name)
    libc.setproctitle(fmt, value)


# Helper functions.


def fmt(nbytes):
    """Format network byte amounts."""
    nbytes = int(nbytes)
    if nbytes >= 1000000:
        nbytes /= 1000000
        return f"{nbytes:.1f}MB"
    if nbytes > 1000:
        nbytes /= 1000
        return f"{nbytes:.1f}kB"
    return f"{nbytes}B"


def readmbox(mboxname, storage):
    """
    Report unread mail.

    Arguments:
        mboxname (str): name of the mailbox to read.
        storage: a dict with keys (unread, time, size) from the previous call
            or an empty dict. This dict will be *modified* by this function.

    Returns: The number of unread messages in this mailbox.
    """
    stats = os.stat(mboxname)
    # When mutt modifies the mailbox, it seems to only change the
    # ctime, not the mtime! This is probably releated to how mutt saves the
    # file. See also stat(2).
    newtime = stats.st_ctime
    newsize = stats.st_size
    if stats.st_size == 0:
        storage["unread"] = 0
        storage["time"] = newtime
        storage["size"] = 0
        return 0
    if not storage or newtime > storage["time"] or newsize != storage["size"]:
        with open(mboxname) as mbox:
            with mmap.mmap(mbox.fileno(), 0, prot=mmap.PROT_READ) as mm:
                start, total = (
                    0,
                    1,
                )  # First mail is not found; it starts on first line...
                while True:
                    rv = mm.find(b"\n\nFrom ", start)
                    if rv == -1:
                        break
                    else:
                        total += 1
                        start = rv + 7
                start, read = 0, 0
                while True:
                    rv = mm.find(b"\nStatus: R", start)
                    if rv == -1:
                        break
                    else:
                        read += 1
                        start = rv + 10
        unread = total - read
        if unread < 0:
            unread = 0
        # Save values for the next run.
        storage["unread"], storage["time"], storage["size"] = unread, newtime, newsize
    else:
        unread = storage["unread"]
    return unread


def hasbattery():
    """Checks if a battery is present according to ACPI."""
    bat = False
    try:
        if sysctlbyname("hw.acpi.battery.units", convert=to_int) > 0:
            bat = True
    except ValueError:
        pass
    return bat


# Functions for generating the items.


def network(storage):
    """
    Report on bytes in/out for the network interfaces.

    Arguments:
        storage: A dict of {interface: (inbytes, outbytes, time)} or an empty dict.
            This dict will be *modified* by this function.

    Returns:
        A string to display.
    """
    cnt = sysctlbyname("net.link.generic.system.ifcount", convert=to_int)
    items = []
    for n in range(1, cnt):
        tm = time.monotonic()
        data = sysctl([4, 18, 0, 2, n, 1], buflen=208)
        name = data[:16].strip(b"\x00").decode("ascii")
        if name.startswith("lo"):
            continue
        ibytes = to_int(data[120:128])
        obytes = to_int(data[128:136])
        if storage and name in storage:
            dt = tm - storage[name][2]
            d_in = fmt((ibytes - storage[name][0]) / dt)
            d_out = fmt((obytes - storage[name][1]) / dt)
            items.append(f"{name}: {d_in}/{d_out}")
        else:
            items.append(f"{name}: 0B/0B")
        # Save values for the next run.
        storage[name] = (ibytes, obytes, tm)
    return "  ".join(items)


def mail(mailboxes):
    """
    Report unread mail.

    Arguments:
        mailboxes: a dict of mailbox info with the paths as the keys.

    Returns: A string to display.
    """
    unread = 0
    for k, v in mailboxes.items():
        unread += readmbox(k, v)
    return f"Mail: {unread}"


def memory():
    """
    Report on the RAM usage on FreeBSD.

    Returns: a string to display.
    """
    suffixes = ("page_count", "free_count", "inactive_count", "cache_count")
    stats = {
        suffix: sysctlbyname(f"vm.stats.vm.v_{suffix}", convert=to_int)
        for suffix in suffixes
    }
    memmax = stats["page_count"]
    mem = memmax - stats["free_count"] - stats["inactive_count"] - stats["cache_count"]
    free = int(100 * mem / memmax)
    return f"RAM: {free}%"


def cpu(storage):
    """
    Report the CPU usage and temperature.

    Argument:
        storage: A dict with keys (used, total) from the previous run or an empty dict.
            This dict will be *modified* by this function.

    Returns:
        A string to display.
    """
    temps = [
        sysctlbyname(f"dev.cpu.{n}.temperature", convert=to_degC) for n in range(4)
    ]
    T = round(stat.mean(temps))
    resbuf = sysctlbyname("kern.cp_time", buflen=40)
    states = struct.unpack("5L", resbuf)
    # According to /usr/include/sys/resource.h, these are:
    # USER, NICE, SYS, INT, IDLE
    total = sum(states)
    used = total - states[-1]
    if storage:
        prevused, prevtotal = storage["used"], storage["total"]
        if total != prevtotal:
            frac = int((used - prevused) / (total - prevtotal) * 100)
        else:  # divide by 0!
            frac = "?"
    else:
        frac = 0
    # Save values for the next run.
    storage["used"], storage["total"] = used, total
    return f"CPU: {frac}%, {T}°C"


def battery():
    """Return battery condition as a string."""
    # Battery states acc. to /usr/src/sys/dev/acpica/acpiio.h
    lookup = {
        0: "on AC",
        1: "discharging",
        2: "charging",
        3: "invalid",
        4: "CRITICAL!",
        7: "unknown",
    }
    idx = sysctlbyname("hw.acpi.battery.state", convert=to_int)
    state = lookup[idx]
    percent = sysctlbyname("hw.acpi.battery.life", convert=to_int)
    return f"Bat: {percent}% ({state})"


def date():
    """Return the date as a string."""
    return time.strftime("%a %Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    main()

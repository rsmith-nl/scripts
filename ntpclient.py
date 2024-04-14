#!/usr/bin/env python
# file: ntpclient.py
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2017-11-16 19:33:50 +0100
# Last modified: 2020-04-01T20:30:30+0200
"""
Simple NTP query program. This program does not strive for high accuracy.
Use this only as a client, never for a time server!
"""

from datetime import datetime
from socket import socket, AF_INET, SOCK_DGRAM
import argparse
import os
import struct
import sys
import time

__version__ = "2020.04.01"


def main():
    """
    Entry point for ntpclient.py.
    """
    args = setup()
    t1 = time.clock_gettime(time.CLOCK_REALTIME)
    ntptime = get_ntp_time(args.server)
    t4 = time.clock_gettime(time.CLOCK_REALTIME)
    # It is not guaranteed that the NTP time is *exactly* in the middle of both
    # local times. But it is a reasonable simplification.
    roundtrip = round(t4 - t1, 4)
    localtime = (t1 + t4) / 2
    diff = localtime - ntptime
    res = None
    if os.geteuid() == 0:
        time.clock_settime(time.CLOCK_REALTIME, ntptime)
        res = "Time set to NTP time."
    localtime = datetime.fromtimestamp(localtime)
    ntptime = datetime.fromtimestamp(ntptime)
    if not args.quiet:
        print(f"Using server {args.server}.")
        print(f"NTP call took approximately {roundtrip} s.")
        print("Local time value:", localtime.strftime("%a %b %d %H:%M:%S.%f %Y."))
        print(
            "NTP time value:",
            ntptime.strftime("%a %b %d %H:%M:%S.%f %Y."),
            "±",
            roundtrip / 2,
            "s.",
        )
        print(f"Local time - ntp time: {diff:.6f} s.")
        if res:
            print(res)


def setup():
    """Process command-line arguments."""
    if "NTPSERVER" in os.environ:
        defaultserver = os.environ["NTPSERVER"]
    else:
        defaultserver = "pool.ntp.org"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress output (default: no)",
    )
    parser.add_argument(
        "-s",
        "--server",
        type=str,
        default=defaultserver,
        help=f"NTP server to use (default: “{defaultserver}”)",
    )
    args = parser.parse_args(sys.argv[1:])
    return args


# See e.g. # https://www.cisco.com/c/en/us/about/press/internet-protocol-journal/back-issues/table-contents-58/154-ntp.html
# From left to right:
# * No leap second adjustment = 0 (2 bits)
# * protocol version 3 (3 bits)
# * client packet = 3 (3 bits)
# In [1]: hex((0 & 0b11) << 6 | (3 & 0b111) << 3 | (3 & 0b111))
# Out[1]: '0x1b'
_query = b"\x1b" + 47 * b"\0"


def get_ntp_time(host="pool.ntp.org", port=123):
    fmt = "!12I"
    with socket(AF_INET, SOCK_DGRAM) as s:
        s.sendto(_query, (host, port))
        msg, address = s.recvfrom(1024)
    unpacked = struct.unpack(fmt, msg[0 : struct.calcsize(fmt)])
    # Return the average of receive and transmit timestamps.
    # Note that 2208988800 is the difference in seconds between the
    # UNIX epoch 1970-1-1 and the NTP epoch 1900-1-1.
    # See: (datetime.datetime(1970,1,1) - datetime.datetime(1900,1,1)).total_seconds()
    t2 = unpacked[8] + float(unpacked[9]) / 2 ** 32 - 2208988800
    t3 = unpacked[10] + float(unpacked[11]) / 2 ** 32 - 2208988800
    return (t2 + t3) / 2


if __name__ == "__main__":
    main()

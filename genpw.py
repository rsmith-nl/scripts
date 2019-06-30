#!/usr/bin/env python3
# file: genpw.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2013-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2013-12-11T23:33:07+01:00
# Last modified: 2019-06-30T10:55:17+0200
"""
Generate random passwords.

The passwords are random data from ``os.urandom`` which is encoded in base64
format.
"""

import argparse
import base64
import os
import sys

__version__ = '2.1'


def main(argv):
    """Entry point for genpw."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-l',
        '--length',
        default=16,
        type=int,
        help='# of random character for password (default 16)'
    )
    parser.add_argument(
        '-r',
        '--repeat',
        default=1,
        type=int,
        help='number of passwords to generate (default: 1)'
    )
    parser.add_argument(
        '-g',
        '--groupby',
        default=0,
        metavar='N',
        type=int,
        help='group by N characters (default: 0; no grouping)'
    )
    parser.add_argument('-v', '--version', action='version', version=__version__)
    args = parser.parse_args(argv)
    for _ in range(args.repeat):
        pw = genpw(args.length)
        if args.groupby > 0:
            n = args.groupby
            count = len(pw) // n
            pw = ' '.join([pw[k:k + n] for k in range(0, n * count, n)])
        print(pw)


def genpw(length):
    """
    Generate a random password.

    Arguments:
        length: Length of the requested password.

    Returns:
        A password string.
    """
    n = roundup(length)
    d = os.urandom(n)
    return base64.b64encode(d, b'__').decode()[:length]


def roundup(characters):
    """
    Prevent '=' at the end of base64 encoded strings.

    This is done by rounding up the number of characters.

    Arguments:
        characters: The number of requested (8-bit) characters.

    Returns:
        The revised number.
    """
    bits = characters * 6
    upto = 24
    rem = bits % upto
    if rem:
        bits += (upto - rem)
    return int(bits / 8)


if __name__ == '__main__':
    main(sys.argv[1:])

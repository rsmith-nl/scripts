#!/usr/bin/env python3
# vim:fileencoding=utf-8
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2013-12-11 22:58:53 +0100
# Last modified: 2015-05-15 13:06:15 +0200
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to genpw.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Generate random passwords by using random data from ``os.urandom`` which is
encoded in base64 format."""

from base64 import b64encode
from os import urandom
import argparse
import sys

__version__ = '2.0.0'


def main(argv):
    """
    Entry point for genpw.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-l', '--length',
                        default=16,
                        type=int,
                        help='# of random character for password (default 16)')
    parser.add_argument('-r', '--repeat',
                        default=1,
                        type=int,
                        help='number of passwords to generate (default: 1)')
    parser.add_argument('-g', '--groupby',
                        default=0,
                        metavar='N',
                        type=int,
                        help='group by N characters (default: 0; no grouping)')
    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__)
    args = parser.parse_args(argv)
    for _ in range(args.repeat):
        pw = genpw(args.length).decode('ascii')
        if args.groupby > 0:
            n = args.groupby
            count = len(pw) // n
            pw = ' '.join([pw[k:k+n] for k in range(0, n*count, n)])
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
    d = urandom(n)
    s = b64encode(d, b'__')
    return s


def roundup(characters):
    """
    Rounds up the number of characters so that you don't end up with '='
    af the end of the base64 encoded string.

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

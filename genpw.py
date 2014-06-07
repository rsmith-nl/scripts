#!/usr/bin/env python2
# vim:fileencoding=utf-8
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2013-12-11 22:58:53 +0100
# Modified: $Date$
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to genpw.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Generate random passwords."""

from __future__ import print_function, division
import argparse
from base64 import b64encode
import sys

__version__ = '$Revision$'[11:-2]


def roundup(characters):
    """Rounds up the number of characters so that you don't end up with '='
    af the end of the base64 encoded string.

    :param characters: number of requested (8-bit) characters
    :returns: revised number
    """
    bits = characters * 6
    upto = 24
    rem = bits % upto
    if rem:
        bits += (upto - rem)
    return int(bits/8)


def genpw(length, dev='/dev/random'):
    """Generate a random password

    :param length: length of the requested password
    :param dev: device to use
    :returns: password string
    """
    n = roundup(length)
    with open(dev, 'rb') as rf:
        d = rf.read(n)
    s = b64encode(d)
    for c in r'/+':
        s = s.replace(c, '_')
    return s


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-l', '--length', default=16, type=int,
                        help='# of random character for password (default 8)')
    parser.add_argument('-r', '--repeat', default=1, type=int,
                        help='number of passwords to generate (default: 1)')
    parser.add_argument('-d', '--device', default='/dev/random', type=str,
                        help='random number device (default: /dev/random)')
    parser.add_argument('-v', '--version', action='version',
                        version=__version__)
    args = parser.parse_args(argv)
    for _ in range(args.repeat):
        print(genpw(args.length, args.device))


if __name__ == '__main__':
    main(sys.argv[1:])

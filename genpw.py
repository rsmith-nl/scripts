# /usr/bin/env python3
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


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-l', '--length', default=18, type=int,
                        help='# of random bytes for password (default 18)')
    parser.add_argument('-r', '--repeat', default=1, type=int,
                        help='number of passwords to generate (default: 1)')
    parser.add_argument('-d', '--device', default='/dev/random', type=str,
                        help='random number device (default: /dev/random)')
    parser.add_argument('-v', '--version', action='version',
                        version=__version__)
    args = parser.parse_args(argv)
    for _ in range(args.repeat):
        with open(args.device, 'rb') as rf:
            d = rf.read(args.length)
            s = str(b64encode(d), encoding='utf-8')
            for c in r'/+':
                s = s.replace(c, '_')
            print(s)


if __name__ == '__main__':
    main(sys.argv[1:])

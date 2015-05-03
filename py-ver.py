#!/usr/bin/env python3
# file: py-ver.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-28 23:25:35 +0200
# Last modified: 2015-05-03 19:50:07 +0200
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to py-ver.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""List the __version__ string in all Python files under the current working
directory or set it to the given value."""

import argparse
import os
import re
import sys

_vre = re.compile('^__version__\s+=.+', flags=re.M)


def printver(fn, newver):
    """
    List the version string in a file.

    Arguments:
        fn: Name of the file to read.
        newver: For compatibility with replacever, ignored.
    """
    with open(fn, 'r', encoding='utf-8') as f:
        data = f.read()
    res = _vre.search(data)
    if res:
        print("{}: {}".format(fn, res.group()))


def replacever(fn, newver):
    """
    Replace the version string in a file.

    Arguments:
        fn: Name of the file to read.
        newver: New version string.
    """
    with open(fn, 'r+', encoding='utf-8') as f:
        data = f.read()
        if _vre.search(data):
            data = _vre.sub(newver, data, count=1)
            f.seek(0)
            f.write(data)


def main(argv):
    """Entry point for this script.

    Arguments:
        argv: List command line argument strings.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-s', '--set',
                        dest='verstr',
                        default='',
                        type=str,
                        help='version to set')
    parser.add_argument('-d', '--dir',
                        dest='dirname',
                        default='',
                        type=str,
                        help='directory to use (defaults: current)')
    parser.add_argument('file',
                        nargs='*',
                        help='files to process')
    args = parser.parse_args(argv[1:])
    if not args.file and len(args.dirname) == 0:
        parser.print_help()
        sys.exit(0)
    if args.verstr:
        func = replacever
        args.verstr = "__version__ = '{}'".format(args.verstr)
    else:
        func = printver
    filelist = []
    if args.dirname:
        for root, dirs, files in os.walk(args.dirname):
            for d in ['.git', '__pycache__']:
                try:
                    dirs.remove(d)
                except ValueError:
                    pass
            filelist += [os.path.join(root, f) for f in files
                         if f.endswith('.py')]
    if args.file:
        filelist += [f for f in args.file if f.endswith('.py')]
    for p in filelist:
        func(p, args.verstr)


if __name__ == '__main__':
    main(sys.argv)

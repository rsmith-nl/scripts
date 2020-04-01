#!/usr/bin/env python3
# file: py-ver.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2015-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-04-28T23:25:35+0200
# Last modified: 2020-04-01T20:41:12+0200
"""Recursively list or set the __version__ string in Python files."""

import argparse
import os
import re
import sys

__version__ = '1.0'
_vre = re.compile(r'^__version__\s+=\s+' + '[\'\"].+', flags=re.M)
_vse = re.compile('[ ]+version=.+', flags=re.M)  # in setup.py


def main():
    """
    Entry point for py-ver.
    """
    args = setup()
    if args.verstr:
        func = replacever
    else:
        func = printver
    filelist = [nm for nm in args.file if os.path.isfile(nm) and nm.endswith('.py')]
    dirs = [nm for nm in args.file if os.path.isdir(nm)]
    for nm in dirs:
        for root, dirs, files in os.walk(nm):
            for d in ['.git', '__pycache__']:
                try:
                    dirs.remove(d)
                except ValueError:
                    pass
            filelist += [os.path.join(root, f) for f in files if f.endswith('.py')]
    for p in filelist:
        func(p, args.verstr)


def setup():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-s', '--set', dest='verstr', default='', type=str, help='version to set'
    )
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('file', nargs='*', help='files to process')
    args = parser.parse_args(sys.argv[1:])
    if not args.file:
        parser.print_help()
        sys.exit(0)
    return args


def replacever(fn, newver):
    """
    Replace the version string in a file.

    Arguments:
        fn: Name of the file to read.
        newver: New version string.
    """
    with open(fn, 'r+', encoding='utf-8') as f:
        data = f.read()
        changed = False
        if _vre.search(data):
            newver = f"__version__ = '{newver}'"
            data = _vre.sub(newver, data, count=1)
            changed = True
        elif fn.endswith('setup.py') and _vse.search(data):
            newver = f"      version='{newver}',"
            data = _vse.sub(newver, data, count=1)
            changed = True
        if changed:
            f.seek(0)
            f.truncate()
            f.write(data)


def printver(fn, newver):
    """
    List the version string in a file.

    Arguments:
        fn: Name of the file to read.
        newver: For compatibility with replacever, ignored.
    """
    with open(fn, 'r', encoding='utf-8') as f:
        data = f.read()
    rlist = [_vre.search(data)]
    if fn.endswith('setup.py'):
        rlist.append(_vse.search(data))
    rlist = [r for r in rlist if r is not None]
    for res in rlist:
        rs = res.group().strip()
        print(f"{fn}: {rs}")


if __name__ == '__main__':
    main()

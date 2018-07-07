#!/usr/bin/env python3
# file: sha256.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2014-2016 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2014-12-28T13:36:38+0100
# Last modified: 2018-07-07T15:10:52+0200
"""
Calculate the SHA256 checksum of files.

Meant for systems that don't come with such a utility.
"""

from hashlib import sha256
from os.path import isfile
from sys import argv, exit
import argparse

__version__ = '1.0.2'


def main(argv):
    """
    Entry point for sha256.

    Arguments:
        argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    hs = '''compare file to this sha256 string;
            will add "[ OK ]" or "[ Failed ]" after the checksum'''
    parser.add_argument('-c', '--checksum', default=None, help=hs)
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('file', nargs='*')
    args = parser.parse_args(argv)
    if not args.file:
        parser.print_help()
        exit(0)
    if args.checksum and len(args.checksum) != 64:
        print('Invalid checksum length. Skipping comparison.')
        args.checksum = None
    for nm in args.file:
        if not isfile(nm):
            continue
        with open(nm, 'rb') as f:
            data = f.read()
        hexdat = sha256(data).hexdigest()
        print(f'SHA256 ({nm}) = {hexdat}', end='')
        if args.checksum:
            if args.checksum != hexdat:
                print(' [ Failed ]', end='')
            else:
                print(' [ OK ]', end='')
        print()


if __name__ == '__main__':
    main(argv[1:])

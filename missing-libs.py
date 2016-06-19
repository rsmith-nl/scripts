# file: missing-libs.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-01-17 15:00:08 +0100
# Last modified: 2016-06-19 10:25:45 +0200

"""Check if any of the files in the given directory are executables linked to
missing shared libraries."""

import argparse
import logging
import sys
import os
import subprocess as sp
from enum import Enum

__version__ = '1.0.0'


class Ftype(Enum):
    script = 1
    executable = 2
    other = 3
    unaccessible = 4


def main(argv):
    """
    Entry point for missing-libs.py.

    Arguments:
        argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__)
    parser.add_argument('--log', default='warning',
                        choices=['debug', 'info', 'warning', 'error'],
                        help="logging level (defaults to 'warning')")
    parser.add_argument("dirs", nargs='*',
                        help="one or more directory to process")
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                        format='%(levelname)s: %(message)s')
    logging.debug('Command line arguments = {}'.format(argv))
    logging.debug('Parsed arguments = {}'.format(args))
    for d in args.dirs:
        logging.info('examining files in {}'.format(d))
        data = [get_type(e.path) for e in os.scandir(d)]
        exe = [a for a, b in data if b == Ftype.executable]
        for e in exe:
            check_missing_libs(e)


def get_type(path):
    """Returns a tuple (path, Ftype)"""
    try:
        with open(path, 'rb') as p:
            data = p.read(2)
    except OSError:
        logging.warning("cannot access {}".format(path))
        return (path, Ftype.unaccessible)
    if data == b'#!':
        return (path, Ftype.script)
    elif data == b'\x7f\x45':
        return (path, Ftype.executable)
    else:
        return (path, Ftype.other)


def check_missing_libs(path):
    logging.info("checking {}".format(path))
    try:
        rv = sp.run(['ldd', path], stdout=sp.PIPE, stderr=sp.DEVNULL,
                    universal_newlines=True, check=True)
        for ln in rv.stdout.splitlines():
            if 'missing' in ln or 'not found' in ln:
                print(path, ln)
    except sp.CalledProcessError:
        logging.warning('ldd failed on {}'.format(path))


if __name__ == '__main__':
    main(sys.argv[1:])

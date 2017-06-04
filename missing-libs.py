#!/usr/bin/env python3
# file: missing-libs.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-01-17 15:00:08 +0100
# Last modified: 2017-06-04 13:45:43 +0200

"""Check executables in the given directory for missing shared libraries."""

import argparse
import concurrent.futures as cf
import logging
import sys
import os
import subprocess as sp
from enum import Enum

__version__ = '2.1.0'


class Ftype(Enum):
    """Enum for limited file type information."""

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
    programs = (e.path for d in args.dirs for e in os.scandir(d)
                if get_type(e.path) == Ftype.executable)
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        for path, missing in tp.map(check_missing_libs, programs):
            for lib in missing:
                print(path, lib)


def get_type(path):
    """
    Determine the Ftype of a file.

    Returns:
        The Ftype for the given path.
    """
    try:
        with open(path, 'rb') as p:
            data = p.read(2)
    except OSError:
        logging.warning("cannot access {}".format(path))
        return Ftype.unaccessible
    if data == b'#!':
        return Ftype.script
    elif data == b'\x7f\x45':
        return Ftype.executable
    else:
        return Ftype.other


def check_missing_libs(path):
    """
    Check if a program has missing libraries, using ldd.

    Arguments:
        path: String containing the path of a file to query.

    Returns:
        A tuple of the path and a list of missing libraries.
    """
    logging.info("checking {}".format(path))
    try:
        p = sp.run(['ldd', path], stdout=sp.PIPE, stderr=sp.DEVNULL,
                   universal_newlines=True, check=True)
        rv = [ln for ln in p.stdout.splitlines()
              if 'missing' in ln or 'not found' in ln]
    except sp.CalledProcessError:
        logging.warning('ldd failed on {}'.format(path))
        rv = []
    return (path, rv)


if __name__ == '__main__':
    main(sys.argv[1:])

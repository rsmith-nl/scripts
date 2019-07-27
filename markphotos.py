#! /usr/bin/env python3
# file: markphotos.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2011-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2011-11-06T20:28:07+01:00
# Last modified: 2019-07-27T21:14:01+0200
"""Script to add my copyright notice to photos."""

from os import utime
from time import mktime
import argparse
import concurrent.futures as cf
import logging
import os.path
import subprocess as sp
import sys

__version__ = '1.2.1'


def main(argv):
    """
    Entry point for markphotos.

    Arguments:
        argv: Command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--log',
        default='warning',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'warning')"
    )
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument("files", metavar='file', nargs='+', help="one or more files to process")
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None), format='%(levelname)s: %(message)s'
    )
    logging.debug(f'command line arguments = {argv}')
    logging.debug(f'parsed arguments = {args}')
    # Check for requisites
    try:
        sp.run(['exiftool'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        logging.info('found “exiftool”')
    except FileNotFoundError:
        logging.error('the “exiftool” program cannot be found')
        sys.exit(1)
    # Work starts here.
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        for fn, rv in tp.map(processfile, args.files):
            logging.info(f'file "{fn}" processed.')
            if rv != 0:
                logging.error(f'error processing "{fn}": {rv}')


def processfile(name):
    """
    Add copyright notice to a file using exiftool.

    Arguments:
        name: path of the file to change

    Returns:
        A 2-tuple of the file path and the return value of exiftool.
    """
    args = ['exiftool', '-CreateDate', name]
    cp = sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL, text=True)
    fields = cp.stdout.split(":")
    year = int(fields[1])
    cr = "R.F. Smith <rsmith@xs4all.nl> http://rsmith.home.xs4all.nl/"
    cmt = f"Copyright © {year} {cr}"
    args = [
        'exiftool', f'-Copyright="Copyright (C) {year} {cr}"',
        f'-Comment="{cmt}"', '-overwrite_original', '-q', name
    ]
    cp = sp.run(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    modtime = int(
        mktime(
            (
                year, int(fields[2]), int(fields[3][:2]), int(fields[3][3:]), int(fields[4]),
                int(fields[5]), 0, 0, -1
            )
        )
    )
    utime(name, (modtime, modtime))
    return name, cp.returncode


if __name__ == '__main__':
    main(sys.argv[1:])

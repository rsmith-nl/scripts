#! /usr/bin/env python3
# file: markphotos.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2011-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2011-11-06T20:28:07+01:00
# Last modified: 2018-04-16T22:16:12+0200
"""Script to add my copyright notice to photos."""

from os import utime
from time import mktime
import argparse
import concurrent.futures as cf
import logging
import os.path
import subprocess
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
        help="logging level (defaults to 'warning')")
    parser.add_argument(
        '-v', '--version', action='version', version=__version__)
    parser.add_argument(
        "files",
        metavar='file',
        nargs='+',
        help="one or more files to process")
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format='%(levelname)s: %(message)s')
    logging.debug('command line arguments = {}'.format(argv))
    logging.debug('parsed arguments = {}'.format(args))
    checkfor(['exiftool', '-ver'])
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        for fn, rv in tp.map(processfile, args.files):
            logging.info('file "{}" processed.'.format(fn))
            if rv != 0:
                logging.error('error processing "{}": {}'.format(fn, rv))


def checkfor(args, rv=0):
    """
    Make sure that a program necessary for using this script is available.

    If the required utility is not found, this function will exit the program.

    Arguments:
        args: String or list of strings of commands. A single string may not
            contain spaces.
        rv: Expected return value from evoking the command.
    """
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('no spaces in single command allowed')
        args = [args]
    try:
        rc = subprocess.call(
            args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if rc != rv:
            raise OSError
        logging.info('found required program "{}"'.format(args[0]))
    except OSError as oops:
        outs = 'required program "{}" not found: {}.'
        logging.error(outs.format(args[0], oops.strerror))
        sys.exit(1)


def processfile(name):
    """
    Add copyright notice to a file using exiftool.

    Arguments:
        name: path of the file to change

    Returns:
        A 2-tuple of the file path and the return value of exiftool.
    """
    args = ['exiftool', '-CreateDate', name]
    createdate = subprocess.check_output(args).decode()
    fields = createdate.split(":")
    year = int(fields[1])
    cr = "R.F. Smith <rsmith@xs4all.nl> http://rsmith.home.xs4all.nl/"
    cmt = "Copyright © {} {}".format(year, cr)
    args = [
        'exiftool', '-Copyright="Copyright (C) {} {}"'.format(year, cr),
        '-Comment="{}"'.format(cmt), '-overwrite_original', '-q', name
    ]
    rv = subprocess.call(
        args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    modtime = int(
        mktime((year, int(fields[2]), int(fields[3][:2]), int(fields[3][3:]),
                int(fields[4]), int(fields[5]), 0, 0, -1)))
    utime(name, (modtime, modtime))
    return name, rv


if __name__ == '__main__':
    main(sys.argv[1:])

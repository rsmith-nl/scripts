#!/usr/bin/env python3
# file: rename.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-09-06 11:45:52 +0200
# Last modified: 2017-06-04 13:52:14 +0200
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to rename.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/
"""
Utility to rename files.

It renames the files given on the command line in the sequence that they are
given to <prefix><number>, keeping the extension of the original file.
"""

import argparse
import logging
import sys
import os

__version__ = '1.0.0'


def main(argv):
    """
    Entry point for rename.py.

    Arguments:
        argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-p',
        '--prefix',
        default='picture-',
        help='prefix for the image name (default "picture-")')
    parser.add_argument(
        '-s',
        '--start',
        type=int,
        default=1,
        help='first number to use (default 1)')
    parser.add_argument(
        '-w',
        '--width',
        type=int,
        default=2,
        help='field width for number (default 2)')
    parser.add_argument(
        '-v', '--version', action='version', version=__version__)
    parser.add_argument(
        '--log',
        default='warning',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'warning')")
    parser.add_argument(
        "files",
        metavar='file',
        nargs='*',
        help="one or more files to process")
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format='%(levelname)s: %(message)s')
    # The real work starts here...
    pairs = newnames(args.files, args.prefix, args.start, args.width)
    es = 'Could not rename "{}" to "{}": {}'
    for old, new in pairs:
        try:
            os.rename(old, new)
        except OSError as e:
            print(es.format(old, new, e))


def newnames(paths, prefix, start, precision):
    """
    Generate new filenames, keeping the path and extension.

    Arguments:
        path: Iterable of path names
        prefix: New filename prefix to use
        start: Initial number to use after the prefix.
        precision: How to format the number.

    Returns:
        List of (path, newpath) tuples
    """
    if not prefix:
        raise ValueError('empty prefix')
    number = int(start)
    if number < 0:
        raise ValueError('negative numbers not allowed')
    precision = int(precision)
    if precision < 0:
        raise ValueError('precision must be positive')
    if isinstance(paths, str):
        paths = [paths]
    req_prec = len(str(len(paths)))
    if req_prec > precision:
        s = 'precision changed from {} to {}'
        logging.warning(s.format(precision, req_prec))
        precision = req_prec
    rv = []
    for path in paths:
        head, tail = os.path.split(path)
        logging.debug('head = {}'.format(head))
        logging.debug('tail = {}'.format(tail))
        if not tail:
            number += 1
            continue
        if head and not head.endswith(os.path.sep):
            head = head + os.path.sep
        _, ext = os.path.splitext(tail)
        t = ''.join([prefix, r'{:0', str(precision), r'd}', ext])
        newpath = ''.join([head, t.format(number)])
        logging.debug('newpath = {}'.format(newpath))
        number += 1
        rv.append((path, newpath))
    return rv


if __name__ == '__main__':
    main(sys.argv[1:])

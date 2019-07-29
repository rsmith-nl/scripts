#!/usr/bin/env python3
# file: tifftopdf.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2012-2017 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2012-06-29T21:02:55+02:00
# Last modified: 2019-07-29T15:37:23+0200
"""
Convert TIFF files to PDF format.

Using the utilities tiffinfo and tiff2pdf from the libtiff package.
"""

from functools import partial
import argparse
import concurrent.futures as cf
import logging
import os
import re
import subprocess as sp
import sys

__version__ = '1.4'


def main(argv):
    """
    Entry point for tifftopdf.

    Arguments:
        argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--log',
        default='warning',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'warning')"
    )
    parser.add_argument('-j', '--jpeg', help='use JPEG compresion', action="store_true")
    parser.add_argument(
        '-q', '--quality', help='JPEG compresion quality (default 85)', type=int, default=85
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
        sp.run(['tiffinfo'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        logging.info('found “tiffinfo”')
        sp.run(['tiff2pdf'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        logging.info('found “tiff2pdf”')
    except FileNotFoundError:
        logging.error('a required program cannot be found')
        sys.exit(1)
    # Work starts here.
    func = tiffconv
    if args.jpeg:
        logging.info('using JPEG compression.')
        func = partial(tiffconv, jpeg=True, quality=args.quality)
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        for fn, rv in tp.map(func, args.files):
            if rv == 0:
                logging.info(f'finished "{fn}"')
            else:
                logging.error(f'conversion of {fn} failed, return code {rv}')


def tiffconv(fname, jpeg=False, quality=85):
    """
    Start a tiff2pdf process for given file.

    Arguments:
        name: Name of the tiff file to convert.
        jpeg: Use JPEG compression.
        quality: JPEG compression quality.

    Returns:
        A 2-tuple (input filename, tiff2pdf return value).
    """
    try:
        args = ['tiffinfo', fname]
        p = sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL)
        txt = p.stdout.decode().split()
        if 'Width:' not in txt:
            raise ValueError('no width in TIF')
        index = txt.index('Width:')
        width = float(txt[index + 1])
        length = float(txt[index + 4])
        try:
            index = txt.index('Resolution:')
            xres = float(txt[index + 1][:-1])
            yres = float(txt[index + 2])
        except ValueError:
            xres, yres = None, None
        outname = re.sub(r'\.tif{1,2}?$', '.pdf', fname, flags=re.IGNORECASE)
        program = ['tiff2pdf']
        if xres:
            args = [
                '-w',
                str(width / xres), '-l',
                str(length / xres), '-x',
                str(xres), '-y',
                str(yres), '-o', outname, fname
            ]
        else:
            args = ['-o', outname, '-z', '-p', 'A4', '-F', fname]
            logging.warning(f"no resolution in {fname}. Fitting to A4")
        if jpeg:
            args = program + ['-n', '-j', '-q', str(quality)] + args
        else:
            args = program + args
        logging.info(f'calling "{args}"')
        rv = sp.run(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        logging.info(f'created "{outname}"')
        return (fname, rv.returncode)
    except Exception as e:
        logging.error(f'starting conversion of "{fname}" failed: {e}')
        return (fname, 0)


if __name__ == '__main__':
    main(sys.argv[1:])

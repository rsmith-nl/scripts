#!/usr/bin/env python3
# file: dicom2png.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2012-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2012-04-11T19:21:19+02:00
# Last modified: 2019-07-27T21:07:49+0200
"""
Convert DICOM files from an X-ray machine to PNG format.

During the conversion process, blank areas are removed. The blank area removal
is based on the image size of a Philips flat detector. The image goes from
2048x2048 pixels to 1574x2048 pixels.
"""

from datetime import datetime
from functools import partial
import argparse
import concurrent.futures as cf
import logging
import os
import subprocess as sp
import sys

__version__ = '1.4'


def convert(filename, quality, level):
    """
    Convert a DICOM file to a PNG file.

    Removing the blank areas from the Philips detector.

    Arguments:
        filename: name of the file to convert.
        quality: JPEG quality to apply
        level: Boolean to indicate whether level adustment should be done.
    Returns:
        Tuple of (input filename, output filename, convert return value)
    """
    outname = filename.strip() + '.png'
    size = '1574x2048'
    args = [
        'convert', filename, '-units', 'PixelsPerInch', '-density', '300', '-crop',
        size + '+232+0', '-page', size + '+0+0', '-auto-gamma', '-quality',
        str(quality)
    ]
    if level:
        args += ['-level', '-35%,70%,0.5']
    args.append(outname)
    cp = sp.run(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    return (filename, outname, cp.returncode)


def main(argv):
    """
    Entry point for dicom2png.

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
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument(
        '-l',
        '--level',
        action='store_true',
        default=False,
        help='Correct color levels (default: no)'
    )
    parser.add_argument(
        '-q', '--quality', type=int, default=80, help='JPEG quailty level (default: 80)'
    )
    parser.add_argument('fn', nargs='*', metavar='filename', help='DICOM files to process')
    args = parser.parse_args(argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None), format='%(levelname)s: %(message)s'
    )
    logging.debug(f'command line arguments = {argv}')
    logging.debug(f'parsed arguments = {args}')
    # Check for requisites
    try:
        sp.run(['convert'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        logging.info('found “convert”')
    except FileNotFoundError:
        logging.error('the program “convert” cannot be found')
        sys.exit(1)
    if not args.fn:
        logging.error('no files to process')
        sys.exit(1)
    if args.quality != 80:
        logging.info(f'quality set to {args.quality}')
    if args.level:
        logging.info('applying level correction.')
    convert_partial = partial(convert, quality=args.quality, level=args.level)
    starttime = str(datetime.now())[:-7]
    logging.info(f'started at {starttime}.')
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        for infn, outfn, rv in tp.map(convert_partial, args.fn):
            logging.info(f'finished conversion of {infn} to {outfn} (returned {rv})')
    endtime = str(datetime.now())[:-7]
    logging.info(f'completed at {endtime}.')


if __name__ == '__main__':
    main(sys.argv)

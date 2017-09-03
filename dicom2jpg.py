#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2017-07-20 22:48:21 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to dicom2png.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/
"""
Convert DICOM files from an X-ray machine to JPEG format.

During the conversion process, blank areas are removed. The blank area removal
is based on the image size of a Philips flat detector. The image goes from
2048x2048 pixels to 1574x2048 pixels.
"""

import concurrent.futures as cf
from datetime import datetime
import argparse
import logging
import os
import sys
import subprocess as sp

__version__ = '1.3.0'


def convert(filename):
    """
    Convert a DICOM file to a JPEG file.

    Removing the blank areas from the Philips detector.

    Arguments:
        filename: name of the file to convert.

    Returns:
        Tuple of (input filename, output filename, convert return value)
    """
    outname = filename.strip() + '.jpg'
    size = '1574x2048'
    args = [
        'convert', filename, '-units', 'PixelsPerInch', '-density', '300',
        '-crop', size + '+232+0', '-page', size + '+0+0', '-auto-gamma',
        outname
    ]
    rv = sp.call(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    return (filename, outname, rv)


def checkfor(args, rv=0):
    """
    Ensure that a necessary program is available.

    Arguments:
        args: String or list of strings of commands. A single string may
            not contain spaces.
        rv: Expected return value from evoking the command.
    """
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('no spaces in single command allowed')
        args = [args]
    try:
        with open(os.devnull, 'w') as bb:
            rc = sp.call(args, stdout=bb, stderr=bb)
        if rc != rv:
            raise OSError
    except OSError as oops:
        outs = "Required program '{}' not found: {}."
        print(outs.format(args[0], oops.strerror))
        sys.exit(1)


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
        help="logging level (defaults to 'warning')")
    parser.add_argument(
        '-v', '--version', action='version', version=__version__)
    parser.add_argument(
        'fn', nargs='*', metavar='filename', help='DICOM files to process')
    args = parser.parse_args(argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format='%(levelname)s: %(message)s')
    logging.debug('command line arguments = {}'.format(argv))
    logging.debug('parsed arguments = {}'.format(args))
    checkfor('convert', rv=1)
    if not args.fn:
        logging.error('no files to process')
        sys.exit(1)
    logging.info('started at {}.'.format(str(datetime.now())[:-7]))
    es = 'finished conversion of {} to {} (returned {})'
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        for infn, outfn, rv in tp.map(convert, args.fn):
            logging.info(es.format(infn, outfn, rv))
    logging.info('completed at {}.'.format(str(datetime.now())[:-7]))


if __name__ == '__main__':
    main(sys.argv)

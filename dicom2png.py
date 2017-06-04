#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2017-06-04 13:20:31 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to dicom2png.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/
"""
Convert DICOM files from an X-ray machine to PNG format.

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
from wand.image import Image

__version__ = '1.2.0'


def convert(filename):
    """
    Convert a DICOM file to a PNG file.

    Removing the blank areas from the Philips detector.

    Arguments:
        filename: name of the file to convert.

    Returns:
        Tuple of (input filename, output filename)
    """
    outname = filename.strip() + '.png'
    with Image(filename=filename) as img:
        with img.convert('png') as converted:
            converted.units = 'pixelsperinch'
            converted.resolution = (300, 300)
            converted.crop(left=232, top=0, width=1574, height=2048)
            converted.save(filename=outname)
    return filename, outname


def main(argv):
    """
    Entry point for dicom2png.

    Arguments:
        argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', default='warning',
                        choices=['debug', 'info', 'warning', 'error'],
                        help="logging level (defaults to 'warning')")
    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__)
    parser.add_argument('fn', nargs='*', metavar='filename',
                        help='DICOM files to process')
    args = parser.parse_args(argv[1:])
    logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                        format='%(levelname)s: %(message)s')
    logging.debug('command line arguments = {}'.format(argv))
    logging.debug('parsed arguments = {}'.format(args))
    if not args.fn:
        logging.error('no files to process')
        sys.exit(1)
    logging.info('started at {}.'.format(str(datetime.now())[:-7]))
    es = 'finished conversion of {} to {}'
    with cf.ProcessPoolExecutor(max_workers=os.cpu_count()) as tp:
        for infn, outfn in tp.map(convert, args.fn):
            logging.info(es.format(infn, outfn))
    logging.info('completed at {}.'.format(str(datetime.now())[:-7]))


if __name__ == '__main__':
    main(sys.argv)

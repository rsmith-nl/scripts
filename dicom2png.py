#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-08-03 12:20:37 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to dicom2png.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert DICOM files from an X-ray machine to PNG format, remove blank
areas. The blank area removal is based on the image size of a Philips flat
detector. The image goes from 2048x2048 pixels to 1574x2048 pixels."""

__version__ = '1.1.0'

from multiprocessing import Pool, Lock
import os
import sys
from wand.image import Image

globallock = Lock()


def report(s, prefix=None):
    """Print status report, using proper locking."""
    if prefix:
        s = ': '.join([prefix, s])
    globallock.acquire()
    print(s, flush=True)
    globallock.release()


def convert(filename):
    """Convert a DICOM file to a PNG file, removing the blank areas from the
    Philips detector.

    Arguments:
        filename: name of the file to convert.

    Returns:
        Name of the output file.
    """
    outname = filename.strip() + '.png'
    report('Starting processing of {}.'.format(filename))
    es = 'Finished conversion of {} to {}'
    with Image(filename=filename) as img:
        with img.convert('png') as converted:
            converted.units = 'pixelsperinch'
            converted.resolution = (300, 300)
            converted.crop(left=232, top=0, width=1574, height=2048)
            converted.save(filename=outname)
            report(es.format(filename, outname))
    return outname


def main(argv):
    """Main program.

    Arguments:
        argv: command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print("{} ver. {}".format(binary, __version__), file=sys.stderr)
        print("Usage: {} [file ...]\n".format(binary), file=sys.stderr)
        print(__doc__)
        sys.exit(0)
    del argv[0]  # Remove the name of the script from the arguments.
    p = Pool()
    p.map(convert, argv)

if __name__ == '__main__':
    main(sys.argv)

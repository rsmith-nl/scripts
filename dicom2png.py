#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2017-01-01 22:14:13 +0100
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to dicom2png.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert DICOM files from an X-ray machine to PNG format, remove blank
areas. The blank area removal is based on the image size of a Philips flat
detector. The image goes from 2048x2048 pixels to 1574x2048 pixels."""

import concurrent.futures as cf
import os
import sys
from wand.image import Image

__version__ = '1.1.3'


def convert(filename):
    """Convert a DICOM file to a PNG file, removing the blank areas from the
    Philips detector.

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
    """Entry point for dicom2png.py.

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
    es = 'Finished conversion of {} to {}'
    with cf.ProcessPoolExecutor(max_workers=os.cpu_count()) as tp:
        fl = [tp.submit(convert, fn) for fn in argv]
        for fut in cf.as_completed(fl):
            infn, outfn = fut.result()
            print(es.format(infn, outfn))

if __name__ == '__main__':
    main(sys.argv)

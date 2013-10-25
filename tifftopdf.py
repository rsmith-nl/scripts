#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to tiff2pdf.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert TIFF files to PDF format using the libtiff package."""

import os
import sys
import subprocess
from multiprocessing import cpu_count
from time import sleep
from checkfor import checkfor


def convert(fname):
    """Convert the file named fname."""
    try:
        args = ['tiffinfo', fname]
        # Gather information about the TIFF file. pylint: disable=E1103
        txt = subprocess.check_output(args).decode().split()
        if 'Width:' not in txt:
            raise ValueError
        index = txt.index('Width:')
        width = float(txt[index+1])
        length = float(txt[index+4])
        xres = float(txt[index+6][:-1])
        yres = float(txt[index+7])
        # Create the output file name.
        if fname.endswith(('.tif', '.TIF')):
            outname = fname[:-4]
        elif fname.endswith(('.tiff', '.TIFF')):
            outname = fname[:-5]
        outname = outname.replace(' ', '_') + '.pdf'
        args = ['tiff2pdf', '-w', str(width/xres), '-l', str(length/xres),
                '-x', str(xres), '-y', str(yres), '-o', outname, fname]
        subprocess.call(args)
        print("File '{}' converted to '{}'.".format(fname, outname))
    except:
        print("Converting {} failed.".format(fname))


def manageprocs(proclist):
    """Check a list of subprocesses for processes that have ended and
    remove them from the list.
    """
    print('# of conversions running: {}\r'.format(len(proclist)), end='')
    sys.stdout.flush()
    for p in proclist:
        pr, ifn, ofn = p
        if pr.poll() is not None:
            print('Conversion of {} to {} finished.'.format(ifn, ofn))
            proclist.remove(p)
    sleep(0.5)


def main(argv):
    """Main program.

    :param argv: command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print("Usage: {} [file ...]".format(binary))
        sys.exit(0)
    checkfor('tiffinfo', 255)
    checkfor(['tiff2pdf', '-v'])
    procs = []
    maxprocs = cpu_count()
    for fname in argv[1:]:
        while len(procs) == maxprocs:
            manageprocs(procs)
        procs.append(convert(fname))
    while len(procs) > 0:
        manageprocs(procs)


if __name__ == '__main__':
    main(sys.argv)

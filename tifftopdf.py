#!/usr/bin/env python
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
from multiprocessing import Pool, Lock

globallock = Lock()

def checkfor(args):
    """Make sure that a program necessary for using this script is
    available.

    Arguments:
    args -- string or list of strings of commands. A single string may
            not contain spaces.
    """
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('No spaces in single command allowed.')
        args = [args]
    try:
        with open('/dev/null', 'w') as bb:
            subprocess.check_call(args, stdout=bb, stderr=bb)
    except:
        print "Required program '{}' not found! exiting.".format(args[0])
        sys.exit(1)

def process(fname):
    """Process the file named fname."""
    try:
        args = ['tiffinfo', fname]
        # Gather information about the TIFF file.
        txt = subprocess.check_output(args).split() #pylint: disable=E1103
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
        globallock.acquire()
        print "File '{}' converted to '{}'.".format(fname, outname)
        globallock.release()  
    except:
        globallock.acquire()
        print "Converting {} failed.".format(fname)
        globallock.release()

def main(argv):
    """Main program.

    Keyword arguments:
    argv -- command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print "Usage: {} [file ...]".format(binary)
        sys.exit(0)
    checkfor('tiffinfo')
    checkfor('tiff2pdf')
    p = Pool()
    p.map(process, argv[1:])
    p.close()

if __name__ == '__main__':
    main(sys.argv)

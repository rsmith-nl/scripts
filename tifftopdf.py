#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Time-stamp: <2012-06-29 23:23:24 rsmith>
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
    available."""
    if isinstance(args, str):
        args = args.split()
    try:
        f = open('/dev/null')
        subprocess.call(args, stderr=subprocess.STDOUT, stdout=f)
        f.close()
    except:
        print "Required program '{}' not found! exiting.".format(args[0])
        sys.exit(1)

def process(fname):
    """Process the file named fname."""
    try:
        args = ['tiffinfo', fname]
            # Gather information about the TIFF file.
        txt = subprocess.check_output(args).split()
        if not txt[7] == 'Width:':
            raise ValueError
        width = float(txt[8])
        length = float(txt[11])
        xres = float(txt[13][:-1])
        yres = float(txt[14])
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

## This is the main program ##
if __name__ == '__main__':
    if len(sys.argv) == 1:
        path, binary = os.path.split(sys.argv[0])
        print "Usage: {} [file ...]".format(binary)
        sys.exit(0)
    checkfor('tiffinfo')
    checkfor('tiff2pdf')
    p = Pool()
    p.map(process, sys.argv[1:])
    p.close()

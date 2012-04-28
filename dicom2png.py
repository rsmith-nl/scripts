#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Time-stamp: <2012-04-28 11:14:03 rsmith>
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to dicom2png.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

'''Convert DICOM files to PNG format, remove blank areas. The blank erea
   removal is based on the image size of a Philips flat detector. The image
   goes from 2048x2048 pixels to 1574x2048 pixels.'''

import os
import sys
import subprocess
from multiprocessing import Pool, Lock

def checkfor(args):
    '''Make sure that a program necessary for using this script is available.'''
    try:
        subprocess.check_output(args, stderr=subprocess.STDOUT)
    except CalledProcessError:
        print "Required program '{}' not found! exiting.".format(progname)
        sys.exit(1)

def processfile(fname):
    '''Use the convert(1) program from the ImageMagick suite to convert the
       image and crop it.'''
    size = '1574x2048'
    args = ['convert', fname, '-units', 'PixelsPerInch', '-density', '300', 
            '-crop', size+'+232+0', '-page', size+'+0+0', fname+'.png']
    rv = subprocess.call(args)
    globallock.acquire()
    if rv != 0:
        print "Error '{}' when processing file '{}'.".format(rv, fname)
    else:
        print "File '{}' processed.".format(fname)
    globallock.release()

## This is the main program ##
if __name__ == '__main__':
    if len(sys.argv) == 1:
        path, binary = os.path.split(sys.argv[0])
        print "Usage: {} [file ...]".format(binary)
        sys.exit(0)
    checkfor('convert')
    globallock = Lock()
    p = Pool()
    p.map(processfile, sys.argv[1:])
    p.close()

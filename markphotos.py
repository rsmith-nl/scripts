#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Adds my copyright notice to photos.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Time-stamp: <2012-04-28 11:42:44 rsmith>
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to markphotos.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

import sys
import subprocess
from multiprocessing import Pool, Lock
from os import utime
import os.path
from time import mktime

def processfile(name):
    args = ['exiftool', '-CreateDate', name]
    createdate = subprocess.check_output(args)
    fields = createdate.split(":")
    year = int(fields[1])
    cr = "R.F. Smith <rsmith@xs4all.nl> http://rsmith.home.xs4all.nl/"
    cmt = "Copyright © {} {}".format(year, cr)
    args = ['exiftool', '-Copyright="Copyright (C) {} {}"'.format(year, cr),
            '-Comment="{}"'.format(cmt), '-overwrite_original', '-q', name]
    rv = subprocess.call(args)
    modtime = int(mktime((year, int(fields[2]), int(fields[3][:2]),
                          int(fields[3][3:]), int(fields[4]), int(fields[5]),
                          0,0,-1)))
    utime(name, (modtime, modtime))
    globallock.acquire()
    if rv == 0:
        print "File '{}' processed.".format(name)
    else:
        print "Error when processing file '{}'".format(name)
    globallock.release()

def checkfor(args):
    '''Make sure that a program necessary for using this script is available.'''
    try:
        subprocess.check_output(args, stderr=subprocess.STDOUT)
    except CalledProcessError:
        print "Required program '{}' not found! exiting.".format(progname)
        sys.exit(1)

if __name__ == '__main__':
    files = sys.argv[1:]
    if len(files) == 0:
        path, binary = os.path.split(sys.argv[0])
        print "Usage: {} [file ...]".format(binary)
        exit(0)
    checkfor(['exiftool', '-ver'])
    globallock = Lock()
    p = Pool()
    p.map(processfile, files)
    p.close()

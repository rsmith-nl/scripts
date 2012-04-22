#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Adds my copyright notice to photos.
#
# Author R.F. Smith <rsmith@xs4all.nl>
# Time-stamp: <2012-04-22 19:35:42 rsmith>
# 
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to backup-local. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

import sys
import shlex, subprocess
from multiprocessing import Pool, Lock
from os import utime
import os.path
from time import mktime

def processfile(name):
    args = shlex.split("exiftool -CreateDate {}".format(name))
    createdate = subprocess.check_output(args)
    fields = createdate.split(":")
    year = int(fields[1])
    cr = "R.F. Smith <rsmith@xs4all.nl> http://rsmith.home.xs4all.nl/"
    cmt = "Copyright © {} {}".format(year, cr)
    cmd = "exiftool -Copyright='{}' -Comment='{}' -overwrite_original -q {}"
    args = shlex.split(cmd.format(cr, cmt, name))
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

if __name__ == '__main__':
    files = sys.argv[1:]
    if len(files) == 0:
        path, binary = os.path.split(sys.argv[0])
        print "Usage: {} [file ...]".format(binary)
        exit(0)
    try:
        subprocess.check_output(['exiftool', '-ver'], stderr=subprocess.STDOUT)
    except CalledProcessError:
        print "Exiftool not found! exiting."
        exit(1)
    globallock = Lock()
    p = Pool()
    p.map(processfile, files)
    p.close()

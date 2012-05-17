#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Time-stamp: <2012-04-28 11:31:29 rsmith>
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to foto4lb.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

'Shrink fotos to a size suitable for use in my logbook and other documents.'

import sys
import subprocess
from multiprocessing import Pool, Lock
from os import utime
import os.path
from time import mktime
from datetime import datetime

def getexifdict(name):
    args = ['exiftool', '-CreateDate', '-Comment', '-Copyright', name]
    data = subprocess.check_output(args)
    lines = data.splitlines()
    ld = {}
    for l in lines:
        key, val = l.split(':',1)
        key = key.replace(' ', '')
        val = val.strip()
        if key == 'CreateDate':
            val = val.replace(' ',':')
        ld[key] = val
    return ld

def processfile(name):
    try:
        ed = getexifdict(name)
        fields = ed['CreateDate'].split(':')
        dt = datetime(int(fields[0]), int(fields[1]), int(fields[2]),
                      int(fields[3]), int(fields[4]), int(fields[5]))
    except:
        ed = {}
        cds = '{}:{}:{} {}:{}:{}'
        dt = datetime.today()
        ed['CreateDate'] = cds.format(dt.year, dt.month, dt.day,
                                      dt.hour, dt.minute, dt.second)
    args = ['mogrify', '-strip', '-resize', '886', '-units', 'PixelsPerInch',
            '-density', '300', '-quality', '90', name]
    rv = subprocess.call(args)
    errstr = "Error when processing file '{}'"
    if rv != 0:
        globallock.acquire()
        print errstr.format(name)
        globallock.release()
        return
    args = ['exiftool']
    args += ['-{}="{}"'.format(k, ed[k]) for k in ed.iterkeys()]
    args += ['-q', '-overwrite_original', name]
    rv = subprocess.call(args)
    if rv == 0:
        modtime = mktime((dt.year, dt.month, dt.day, dt.hour,
                         dt.minute, dt.second, 0,0,-1))
        utime(name, (modtime, modtime))
        globallock.acquire()
        print "File '{}' processed".format(name)
        globallock.release()
    else:
        globallock.acquire()
        print errstr.format(name)
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
    checkfor(['exiftool',  '-ver'])
    checkfor('mogrify')
    globallock = Lock()
    p = Pool()
    p.map(processfile, files)
    p.close()

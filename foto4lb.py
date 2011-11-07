#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Shrink fotos to a size suitable for use in my logbook and other documents.
#
# Copyright © 2011 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Time-stamp: <2011-11-07 21:39:03 rsmith>
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import sys
import shlex, subprocess
from multiprocessing import Pool, Lock
from os import utime
from time import mktime
from datetime import datetime

def getexifdict(name):
    ds = "exiftool -CreateDate -Comment -Copyright -ImageWidth -ImageHeight {}"
    args = shlex.split(ds.format(name))
    data = subprocess.check_output(args)
    lines = data.splitlines()
    ld = {}
    for l in lines:
        key, val = l.split(':',1)
        key = key.strip()
        val = val.strip()
        if key == 'Create Date':
            val = val.replace(' ',':')
        ld[key] = val
    return ld

def processfile(name):
    try:
        ed = getexifdict(name)
        fields = ed['Create Date'].split(':')
        dt = datetime(int(fields[0]), int(fields[1]), int(fields[2]), 
                      int(fields[3]), int(fields[4]), int(fields[5]))
    except:
        ed = {}
        cds = '{}:{}:{} {}:{}:{}'
        dt = datetime.today()
        ed['Create Date'] = cds.format(dt.year, dt.month, dt.day, 
                                      dt.hour, dt.minute, dt.second)
    cmd = 'mogrify -strip -resize 886 -units PixelsPerInch -density 300'
    cmd += ' -quality 90 {}'.format(name)
    args = shlex.split(cmd)
    rv = subprocess.call(args)
    if rv != 0:
        globallock.acquire()
        print "Error when processing file '{}'".format(name)
        globallock.release()
        return
    cmd = "exiftool"
    for k in iterkeys(ed):
        cmd += ' -{}="{}"'.format(k, ed[k]) 
    cmd += ' -q {}'.format(name)
    args = shlex.split(cmd)
    rv = subprocess.call(args)
    if rv == 0:
        modtime = mktime(dt.year, dt.month, dt.day, dt.hour, 
                         dt.minute, dt.second, 0,0,-1)
        utime(name, (modtime, modtime))
        globallock.acquire()
        print "File '{}' processed".format(name)
        globallock.release()        
    else:
        globallock.acquire()
        print "Error when processing file '{}'".format(name)
        globallock.release()

if __name__ == '__main__':
    files = sys.argv[1:]
    try:
        subprocess.check_output(['exiftool', '-ver'], stderr=subprocess.STDOUT)
        subprocess.check_output(['mogrify', '-ver'], stderr=subprocess.STDOUT)
    except CalledProcessError:
        print "Exiftool or mogrify not found! exiting."
        exit(1)
    globallock = Lock()
    p = Pool()
    p.map(processfile, files)

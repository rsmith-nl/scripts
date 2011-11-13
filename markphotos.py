#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Adds my copyright notice to photos.
#
# Copyright © 2011 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Time-stamp: <2011-11-13 22:18:13 rsmith>
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
    try:
        subprocess.check_output(['exiftool', '-ver'], stderr=subprocess.STDOUT)
    except CalledProcessError:
        print "Exiftool not found! exiting."
        exit(1)
    globallock = Lock()
    p = Pool()
    p.map(processfile, files)
    p.close()

#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2012 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Time-stamp: <2012-04-11 19:37:50 rsmith>
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

"Convert DICOM files to PNG format, remove blank areas."

import os
import sys # voor argv.
import subprocess
from multiprocessing import Pool, Lock

def checkfor(args):
    try:
        subprocess.check_output(args, stderr=subprocess.STDOUT)
    except CalledProcessError:
        print "Required program '{}' not found! exiting.".format(progname)
        sys.exit(1)

def processfile(fname):
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

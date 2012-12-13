#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all
# copyright and related or neighboring rights to gitdates.py. This
# work is published from the Netherlands. See
# http://creativecommons.org/publicdomain/zero/1.0/

"""For each file in a directory managed by git, get the short hash and
data of the most recent commit of that file."""

import os
import sys
import subprocess
import time
from multiprocessing import Pool
from checkfor import checkfor

# Suppres terminal windows on MS windows.
startupinfo = None
if os.name == 'nt':
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

def filecheck(fname):
    """Start a git process to get file info. Return a string
    containing the filename, the abbreviated commit hash and the
    author date in ISO 8601 format.

    Arguments:
    fname -- Name of the file to check.
    """
    args = ['git', '--no-pager', 'log', '-1', '--format=%h|%at', fname]
    try:
        data = subprocess.check_output(args, startupinfo=startupinfo)[:-1]
        h, t = data.split('|')
        out = (fname[2:], h, time.gmtime(float(t)))
    except subprocess.CalledProcessError:
        out = (fname)
    return out

def filedatasorter(a, b):
    """Sort the 3-tuples of the filedata list in reverse order, according
    to their dates which is the third item in the tuple.

    Arguments:
    a, b -- 3-tuple of a name, short hash tag and struct_time.
    """
    p = a[2]
    q = b[2]
    if p > q:
        return -1
    if p == q:
        return 0
    return 1

def main():
    """Main program."""
    checkfor(['git', '--version'])
    # Get a list of all files
    allfiles = []
    if not '.git' in os.listdir('.'):
        print 'This directory is not managed by git.'
        sys.exit(0)
    for root, dirs, files in os.walk('.'):
        if '.git' in dirs:
            dirs.remove('.git')
        tmp = [os.path.join(root, f) for f in files]
        allfiles += tmp
    # Gather the files' data using a Pool.
    p = Pool()
    filedata = []
    for res in p.imap(filecheck, allfiles):
        filedata.append(res)
    p.close()
    # Sort the data (latest modified first) and print it
    filedata.sort(filedatasorter)
    dfmt = '%Y-%m-%d %H:%M:%S %Z'
    for name, tag, date in filedata:
        print '{}|{}|{}'.format(name, tag, time.strftime(dfmt, date))


if __name__ == '__main__':
    main()

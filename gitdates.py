#!/usr/bin/env python3
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
        b = subprocess.check_output(args, startupinfo=startupinfo)
        data = b.decode()[:-1]
        h, t = data.split('|')
        out = (fname[2:], h, time.gmtime(float(t)))
    except (subprocess.CalledProcessError, ValueError):
        return (fname[2:], '', time.gmtime(0.0))
    return out

def main():
    """Main program."""
    checkfor(['git', '--version'])
    # Get a list of all files
    allfiles = []
    # Get a list of excluded files.
    exargs = ['git', 'ls-files', '-i', '-o', '--exclude-standard']
    exc = subprocess.check_output(exargs).split()
    if not '.git' in os.listdir('.'):
        print('This directory is not managed by git.')
        sys.exit(0)
    for root, dirs, files in os.walk('.'):
        if '.git' in dirs:
            dirs.remove('.git')
        tmp = [os.path.join(root, f) for f in files if f not in exc]
        allfiles += tmp
    # Gather the files' data using a Pool.
    p = Pool()
    filedata = []
    for res in p.imap_unordered(filecheck, allfiles):
        filedata.append(res)
    p.close()
    # Sort the data (latest modified first) and print it
    filedata.sort(key=lambda a: a[2], reverse=True)
    dfmt = '%Y-%m-%d %H:%M:%S %Z'
    for name, tag, date in filedata:
        print('{}|{}|{}'.format(name, tag, time.strftime(dfmt, date)))


if __name__ == '__main__':
    main()
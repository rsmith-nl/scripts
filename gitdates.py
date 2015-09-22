#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-09-23 01:09:21 +0200
#
# To the extent possible under law, Roland Smith has waived all
# copyright and related or neighboring rights to gitdates.py. This
# work is published from the Netherlands. See
# http://creativecommons.org/publicdomain/zero/1.0/

"""For each file in a directory managed by git, get the short hash and
data of the most recent commit of that file."""

from __future__ import print_function
from multiprocessing import Pool
import os
import subprocess
import sys
import time

# Suppres annoying command prompts on ms-windows.
startupinfo = None
if os.name == 'nt':
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


def main():
    """
    Entry point for gitdates.
    """
    checkfor(['git', '--version'])
    # Get a list of all files
    allfiles = []
    # Get a list of excluded files.
    if '.git' not in os.listdir('.'):
        print('This directory is not managed by git.')
        sys.exit(0)
    exargs = ['git', 'ls-files', '-i', '-o', '--exclude-standard']
    exc = subprocess.check_output(exargs, startupinfo=startupinfo).split()
    for root, dirs, files in os.walk('.'):
        for d in ['.git', '__pycache__']:
            try:
                dirs.remove(d)
            except ValueError:
                pass
        tmp = [os.path.join(root, f) for f in files if f not in exc]
        allfiles += tmp
    # Gather the files' data using a Pool.
    p = Pool()
    filedata = [res for res in p.imap_unordered(filecheck, allfiles)
                if res is not None]
    p.close()
    # Sort the data (latest modified first) and print it
    filedata.sort(key=lambda a: a[2], reverse=True)
    dfmt = '%Y-%m-%d %H:%M:%S %Z'
    for name, tag, date in filedata:
        print('{}|{}|{}'.format(name, tag, time.strftime(dfmt, date)))


def checkfor(args, rv=0):
    """
    Make sure that a program necessary for using this script is available.
    Calls sys.exit when this is not the case.

    Arguments:
        args: String or list of strings of commands. A single string may
            not contain spaces.
        rv: Expected return value from evoking the command.
    """
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('no spaces in single command allowed')
        args = [args]
    try:
        rc = subprocess.call(args, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        if rc != rv:
            raise OSError
    except OSError as oops:
        outs = "Required program '{}' not found: {}."
        print(outs.format(args[0], oops.strerror))
        sys.exit(1)


def filecheck(fname):
    """
    Start a git process to get file info. Return a string containing the
    filename, the abbreviated commit hash and the author date in ISO 8601
    format.

    Arguments:
        fname: Name of the file to check.

    Returns:
        A 3-tuple containing the file name, latest short hash and latest
        commit date.
    """
    args = ['git', '--no-pager', 'log', '-1', '--format=%h|%at', fname]
    try:
        b = subprocess.check_output(args, startupinfo=startupinfo)
        data = b.decode()[:-1]
        h, t = data.split('|')
        out = (fname[2:], h, time.gmtime(float(t)))
    except (subprocess.CalledProcessError, ValueError):
        return None
    return out


if __name__ == '__main__':
    main()

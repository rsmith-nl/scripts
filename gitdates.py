#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-05-03 22:05:17 +0200
#
# To the extent possible under law, Roland Smith has waived all
# copyright and related or neighboring rights to gitdates.py. This
# work is published from the Netherlands. See
# http://creativecommons.org/publicdomain/zero/1.0/

"""For each file in a directory managed by git, get the short hash and
data of the most recent commit of that file."""

from multiprocessing import Pool
import os
import subprocess
import sys
import time

# Suppres terminal windows on MS windows.
startupinfo = None
if os.name == 'nt':
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


def checkfor(args, rv=0):
    """Make sure that a program necessary for using this script is
    available.

    :param args: String or list of strings of commands. A single string may
    not contain spaces.
    :param rv: Expected return value from evoking the command.
    """
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('no spaces in single command allowed')
        args = [args]
    try:
        with open(os.devnull, 'w') as bb:
            rc = subprocess.call(args, stdout=bb, stderr=bb)
        if rc != rv:
            raise OSError
    except OSError as oops:
        outs = "Required program '{}' not found: {}."
        print(outs.format(args[0], oops.strerror))
        sys.exit(1)


def filecheck(fname):
    """Start a git process to get file info. Return a string
    containing the filename, the abbreviated commit hash and the
    author date in ISO 8601 format.

    :param fname: name of the file to check.
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


def main():
    """Main program."""
    checkfor(['git', '--version'])
    # Get a list of all files
    allfiles = []
    # Get a list of excluded files.
    if '.git' not in os.listdir('.'):
        print('This directory is not managed by git.')
        sys.exit(0)
    exargs = ['git', 'ls-files', '-i', '-o', '--exclude-standard']
    exc = subprocess.check_output(exargs).split()
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


if __name__ == '__main__':
    main()

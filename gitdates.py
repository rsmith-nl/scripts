#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-10-08 22:33:37 +0200
#
# To the extent possible under law, Roland Smith has waived all
# copyright and related or neighboring rights to gitdates.py. This
# work is published from the Netherlands. See
# http://creativecommons.org/publicdomain/zero/1.0/

"""For each file in a directory managed by git, get the short hash and
data of the most recent commit of that file."""

from concurrent.futures import ThreadPoolExecutor
import logging
import os
import subprocess
import sys
import time


def main():
    """
    Entry point for gitdates.
    """
    logging.basicConfig(level='WARNING', format='%(levelname)s: %(message)s')
    checkfor(['git', '--version'])
    # Get a list of all files
    allfiles = []
    # Get a list of excluded files.
    if '.git' not in os.listdir('.'):
        logging.error('This directory is not managed by git.')
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
    # Gather the files' data using a ThreadPoolExecutor.
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        res = tp.map(filecheck, allfiles)
    filedata = [r for r in res if r is not None]
    # Sort the data (latest modified first) and print it
    filedata.sort(key=lambda a: a[2], reverse=True)
    dfmt = '%Y-%m-%d %H:%M:%S %Z'
    for name, tag, date in filedata:
        print('{}|{}|{}'.format(name, tag, time.strftime(dfmt, date)))


def checkfor(args, rv=0):
    """
    Make sure that a program necessary for using this script is available.
    If the required utility is not found, this function will exit the program.

    Arguments:
        args: String or list of strings of commands. A single string may not
            contain spaces.
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
        logging.info('found required program "{}"'.format(args[0]))
    except OSError as oops:
        outs = 'required program "{}" not found: {}.'
        logging.error(outs.format(args[0], oops.strerror))
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
        b = subprocess.check_output(args)
        data = b.decode()[:-1]
        h, t = data.split('|')
        out = (fname[2:], h, time.gmtime(float(t)))
    except (subprocess.CalledProcessError, ValueError):
        logging.error('git log failed for "{}"'.format(fname))
        return None
    return out


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to <script>. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Description."""

import os
import sys
import subprocess
from multiprocessing import Pool

def checkfor(args):
    """Make sure that a program necessary for using this script is
    available.

    Arguments:
    args -- string or list of strings of commands. A single string may
            not contain spaces.
    """
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('No spaces in single command allowed.')
        args = [args]
    try:
        with open('/dev/null', 'w') as bb:
            subprocess.check_call(args, stdout=bb, stderr=bb)
    except subprocess.CalledProcessError:
        print "Required program '{}' not found! exiting.".format(args[0])
        sys.exit(1)

def filecheck(fname):
    """Start a git process to get file info."""
    args = ['git', '--no-pager', 'log', '-1', '--format=%h %ai', fname]
    try:
        data = subprocess.check_output(args)
    except subprocess.CalledProcessError:
        data = 'no data'
    outs = '{} {}'.format(fname[2:], data[:-1])
    return outs

#    gprint("Updating {} failed.".format(fname))

def main():
    """Main program."""
    checkfor(['git', '--version'])
    allfiles = []
    if not '.git' in os.listdir('.'):
        print 'This directory is not managed by git.'
        sys.exit(0)
    for root, dirs, files in os.walk('.'):
        if '.git' in dirs:
            dirs.remove('.git')
        tmp = [os.path.join(root, f) for f in files]
        allfiles += tmp
    p = Pool()
    for res in p.imap(filecheck, allfiles):
        print res
    p.close()

if __name__ == '__main__':
    main()

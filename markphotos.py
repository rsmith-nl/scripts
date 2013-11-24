#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Adds my copyright notice to photos.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to markphotos.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

from __future__ import division, print_function

__version__ = '$Revision$'[11:-2]

import sys
import subprocess
from multiprocessing import Pool, Lock
from os import utime
import os.path
from time import mktime

globallock = Lock()


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


def processfile(name):
    args = ['exiftool', '-CreateDate', name]
    createdate = subprocess.check_output(args).decode()
    fields = createdate.split(":")
    year = int(fields[1])
    cr = "R.F. Smith <rsmith@xs4all.nl> http://rsmith.home.xs4all.nl/"
    cmt = "Copyright © {} {}".format(year, cr)
    args = ['exiftool', '-Copyright="Copyright (C) {} {}"'.format(year, cr),
            '-Comment="{}"'.format(cmt), '-overwrite_original', '-q', name]
    rv = subprocess.call(args)
    modtime = int(mktime((year, int(fields[2]), int(fields[3][:2]),
                          int(fields[3][3:]), int(fields[4]), int(fields[5]),
                          0, 0, -1)))
    utime(name, (modtime, modtime))
    globallock.acquire()
    if rv == 0:
        print("File '{}' processed.".format(name))
    else:
        print("Error when processing file '{}'".format(name))
    globallock.release()


def main(argv):
    """Main program.

    Keyword arguments:
    argv -- command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print("{} version {}".format(binary, __version__), file=sys.stderr)
        print("Usage: {} [file ...]".format(binary), file=sys.stderr)
        sys.exit(0)
    checkfor(['exiftool',  '-ver'])
    p = Pool()
    p.map(processfile, argv[1:])
    p.close()

if __name__ == '__main__':
    main(sys.argv)

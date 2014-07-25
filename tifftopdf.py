#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to tiff2pdf.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert TIFF files to PDF format using the libtiff package."""

from __future__ import division, print_function  # Python 2 compatibility

__version__ = '$Revision$'[11:-2]

import os
import sys
import subprocess
from multiprocessing import cpu_count
from time import sleep


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


def convert(fname):
    """Convert the file named fname."""
    try:
        args = ['tiffinfo', fname]
        # Gather information about the TIFF file. pylint: disable=E1103
        txt = subprocess.check_output(args).decode().split()
        if 'Width:' not in txt:
            raise ValueError
        index = txt.index('Width:')
        width = float(txt[index+1])
        length = float(txt[index+4])
        try:
            index = txt.index('Resolution:')
            xres = float(txt[index+1][:-1])
            yres = float(txt[index+2])
        except ValueError:
            xres, yres = None, None
        # Create the output file name.
        if fname.endswith(('.tif', '.TIF')):
            outname = fname[:-4]
        elif fname.endswith(('.tiff', '.TIFF')):
            outname = fname[:-5]
        outname = outname.replace(' ', '_') + '.pdf'
        if xres:
            args = ['tiff2pdf', '-w', str(width/xres), '-l', str(length/xres),
                    '-x', str(xres), '-y', str(yres), '-o', outname, fname]
        else:
            args = ['tiff2pdf', '-o', outname, '-z', '-p', 'A4', '-F', fname]
            print("No resolution in {}. Fitting to A4.".format(fname))
        with open(os.devnull, 'w') as bitbucket:
            p = subprocess.Popen(args, stdout=bitbucket, stderr=bitbucket)
            print("Conversion of {} to {} started.".format(fname, outname))
        return (p, fname, outname)
    except Exception as e:
        print("Starting conversion of {} failed: {}".format(fname, str(e)))
        return (None, fname, None)


def manageprocs(proclist):
    """Check a list of subprocesses for processes that have ended and
    remove them from the list.
    """
    print('# of conversions running: {}\r'.format(len(proclist)), end='')
    sys.stdout.flush()
    for p in proclist:
        pr, ifn, ofn = p
        if pr is None:
            proclist.remove(p)
            break
        if pr.poll() is not None:
            print('Conversion of {} to {} finished.'.format(ifn, ofn))
            proclist.remove(p)
    sleep(0.5)


def main(argv):
    """Main program.

    :param argv: command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print("{} version {}".format(binary, __version__), file=sys.stderr)
        print("Usage: {} [file ...]".format(binary), file=sys.stderr)
        sys.exit(0)
    checkfor('tiffinfo', 255)
    checkfor(['tiff2pdf', '-v'])
    procs = []
    maxprocs = cpu_count()
    for fname in argv[1:]:
        while len(procs) == maxprocs:
            manageprocs(procs)
        procs.append(convert(fname))
    while len(procs) > 0:
        manageprocs(procs)


if __name__ == '__main__':
    main(sys.argv)

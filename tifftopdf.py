#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-09-23 01:17:28 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to tiff2pdf.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert TIFF files to PDF format using the utilities tiffinfo and tiff2pdf
from the libtiff package."""

__version__ = '1.0.1'

from multiprocessing import cpu_count
from time import sleep
import os
import subprocess
import sys


def main(argv):
    """
    Entry point for tifftopdf.

    Arguments:
        argv: command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print("{} version {}".format(binary, __version__), file=sys.stderr)
        print("Usage: {} [file ...]".format(binary), file=sys.stderr)
        sys.exit(0)
    checkfor('tiffinfo', 255)
    checkfor(['tiff2pdf', '-v'])
    mapprocs(argv[1:], convert)


def checkfor(args, rv=0):
    """
    Make sure that a program necessary for using this script is available.
    Exits the program is the requirement cannot be found.

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


def mapprocs(lst, fn):
    """
    Map a process starting function over a list of filenames.

    Arguments:
        lst: List of filenames.
        fn: function that starts a process.
    """
    procs = []
    maxprocs = cpu_count()
    for fname in lst:
        while len(procs) == maxprocs:
            manageprocs(procs)
        procs.append(fn(fname))
    while len(procs) > 0:
        manageprocs(procs)


def convert(fname):
    """
    Start a tiff2pdf process for the file fname.

    Arguments:
        name: Name of the tiff file to convert.

    Returns:
        A 3-tuple (Popen object, input filename, output filename).
    """
    try:
        args = ['tiffinfo', fname]
        txt = subprocess.check_output(args, stderr=subprocess.DEVNULL)
        txt = txt.decode('utf-8').split()
        if 'Width:' not in txt:
            raise ValueError('no width in TIF')
        index = txt.index('Width:')
        width = float(txt[index + 1])
        length = float(txt[index + 4])
        try:
            index = txt.index('Resolution:')
            xres = float(txt[index + 1][:-1])
            yres = float(txt[index + 2])
        except ValueError:
            xres, yres = None, None
        # Create the output file name.
        if fname.endswith(('.tif', '.TIF')):
            outname = fname[:-4]
        elif fname.endswith(('.tiff', '.TIFF')):
            outname = fname[:-5]
        outname = outname.replace(' ', '_') + '.pdf'
        if xres:
            args = ['tiff2pdf', '-w', str(width / xres), '-l',
                    str(length / xres), '-x', str(xres), '-y', str(yres), '-o',
                    outname, fname]
        else:
            args = ['tiff2pdf', '-o', outname, '-z', '-p', 'A4', '-F', fname]
            print("No resolution in {}. Fitting to A4.".format(fname))
        p = subprocess.Popen(args, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        print("Conversion of {} to {} started.".format(fname, outname))
        return (p, fname, outname)
    except Exception as e:
        print("Starting conversion of {} failed: {}".format(fname, str(e)))
        return (None, fname, None)


def manageprocs(proclist):
    """
    Manage a list of subprocesses.

    Arguments:
        proclist: a list of 3-tuples (Popen, input filename, output
        filename)
    """
    print('# of conversions running: {}\r'.format(len(proclist)), end='')
    sys.stdout.flush()
    for p in proclist:
        pr, ifn, ofn = p
        if pr is None:
            proclist.remove(p)
        elif pr.poll() is not None:
            print('Conversion of {} to {} finished.'.format(ifn, ofn))
            proclist.remove(p)
    sleep(0.5)


if __name__ == '__main__':
    main(sys.argv)

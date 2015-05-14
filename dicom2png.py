#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-05-14 21:09:45 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to dicom2png.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert DICOM files from an X-ray machine to PNG format, remove blank
areas. The blank area removal is based on the image size of a Philips flat
detector. The image goes from 2048x2048 pixels to 1574x2048 pixels."""

__version__ = '1.0.1'

from multiprocessing import cpu_count
from time import sleep
import os
import subprocess
import sys


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


def startconvert(fname):
    """Use the convert(1) program from the ImageMagick suite to convert the
       image and crop it."""
    size = '1574x2048'
    args = ['convert', fname, '-units', 'PixelsPerInch', '-density', '300',
            '-crop', size + '+232+0', '-page', size + '+0+0', '-auto-gamma',
            fname + '.png']
    with open(os.devnull, 'w') as bb:
        p = subprocess.Popen(args, stdout=bb, stderr=bb)
    print('Start processing', fname)
    return (fname, p)


def manageprocs(proclist):
    """Check a list of subprocesses for processes that have ended and
    remove them from the list.
    """
    for it in proclist:
        fn, pr = it
        result = pr.poll()
        if result is not None:
            proclist.remove(it)
            if result == 0:
                print('Finished processing', fn)
            else:
                s = 'The conversion of {} exited with error code {}.'
                print(s.format(fn, result))
    sleep(0.5)


def main(argv):
    """Main program.

    Keyword arguments:
    argv -- command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print("{} ver. {}".format(binary, __version__), file=sys.stderr)
        print("Usage: {} [file ...]\n".format(binary), file=sys.stderr)
        print(__doc__)
        sys.exit(0)
    del argv[0]
    checkfor('convert', 1)
    procs = []
    maxprocs = cpu_count()
    for ifile in argv:
        while len(procs) == maxprocs:
            manageprocs(procs)
        procs.append(startconvert(ifile))
    while len(procs) > 0:
        manageprocs(procs)


if __name__ == '__main__':
    main(sys.argv)

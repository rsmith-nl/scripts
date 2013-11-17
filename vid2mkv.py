#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to vid2mkv.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert all video files given on the command line to Theora/Vorbis streams
in a Matroska container."""

from __future__ import print_function, division

__version__ = '$Revision$'[11:-2]

import os
import sys
import subprocess
from multiprocessing import cpu_count
from time import sleep


def warn(s):
    """Print a warning message.

    :param s: Message string
    """
    s = ' '.join(['Warning:', s])
    print(s, file=sys.stderr)


def startencoder(fname):
    """Use ffmpeg to convert a video file to Theora/Vorbis
    streams in a Matroska container.

    :param fname: Name of the file to convert.
    :returns: a 3-tuple of a Process, input path and output path
    """
    basename, ext = os.path.splitext(fname)
    known = ['.mp4', '.avi', '.wmv', '.flv', '.mpg', '.mpeg', '.mov', '.ogv']
    if ext.lower() not in known:
        warn("File {} has unknown extension, ignoring it.".format(fname))
        return (None, fname, None)
    ofn = basename + '.mkv'
    args = ['ffmpeg', '-i', fname, '-c:v', 'libtheora', '-q:v', '6', '-c:a',
            'libvorbis', '-q:a', '3', '-sn', ofn]
    with open(os.devnull, 'w') as bitbucket:
        try:
            p = subprocess.Popen(args, stdout=bitbucket, stderr=bitbucket)
            print("Conversion of {} to {} started.".format(fname, ofn))
        except:
            warn("Starting conversion of {} failed.".format(fname))
    return (p, fname, ofn)


def manageprocs(proclist):
    """Check a list of subprocesses tuples for processes that have ended and
    remove them from the list.

    :param proclist: a list of (process, input filename, output filename)
    tuples.
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


def main(argv):
    """Main program.

    :param argv: command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print("{} version {}".format(binary, __version__), file=sys.stderr)
        print("Usage: {} [file ...]".format(binary), file=sys.stderr)
        sys.exit(0)
    avis = argv[1:]
    procs = []
    maxprocs = cpu_count()
    for ifile in avis:
        while len(procs) == maxprocs:
            manageprocs(procs)
        procs.append(startencoder(ifile))
    while len(procs) > 0:
        manageprocs(procs)


if __name__ == '__main__':
    main(sys.argv)

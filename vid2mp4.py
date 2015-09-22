#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-09-23 01:20:34 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to vid2mp4.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert all video files given on the command line to H.264/AAC streams in
an MP4 container."""

__version__ = '1.1.1'

from multiprocessing import cpu_count
from time import sleep
import logging
import os
import subprocess
import sys


def main(argv):
    """
    Entry point for vid2mp4.

    Arguments:
        argv: All command line arguments.
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print("{} version {}".format(binary, __version__), file=sys.stderr)
        print("Usage: {} [file ...]".format(binary), file=sys.stderr)
        sys.exit(0)
    logging.basicConfig(level="INFO", format='%(levelname)s: %(message)s')
    checkfor(['ffmpeg', '-version'])
    vids = argv[1:]
    procs = []
    maxprocs = cpu_count()
    for ifile in vids:
        while len(procs) == maxprocs:
            manageprocs(procs)
        procs.append(startencoder(ifile))
    while len(procs) > 0:
        manageprocs(procs)


def checkfor(args, rv=0):
    """
    Make sure that a program necessary for using this script is available.

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
        outs = "required program '{}' not found: {}."
        logging.error(outs.format(args[0], oops.strerror))
        sys.exit(1)


def startencoder(fname):
    """
    Use ffmpeg to convert a video file to H.264/AAC streams in an MP4
    container.

    Arguments:
        fname: Name of the file to convert.

    Returns:
        A 3-tuple of a Process, input path and output path.
    """
    basename, ext = os.path.splitext(fname)
    known = ['.mp4', '.avi', '.wmv', '.flv', '.mpg', '.mpeg', '.mov', '.ogv']
    if ext.lower() not in known:
        ls = "File {} has unknown extension, ignoring it.".format(fname)
        logging.warning(ls)
        return (None, fname, None)
    ofn = basename + '.mp4'
    args = ['ffmpeg', '-i', fname, '-c:v', 'libx264', '-crf', '29', '-flags',
            '+aic+mv4', '-c:a', 'libfaac', '-sn', ofn]
    try:
        p = subprocess.Popen(args, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        logging.info("Conversion of {} to {} started.".format(fname, ofn))
    except:
        logging.error("Starting conversion of {} failed.".format(fname))
    return (p, fname, ofn)


def manageprocs(proclist):
    """
    Check a list of subprocesses tuples for processes that have ended and
    remove them from the list.

    Arguments:
        proclist: a list of (process, input filename, output filename)
                  tuples.
    """
    nr = '# of conversions running: {}\r'.format(len(proclist))
    logging.info(nr, end='')
    sys.stdout.flush()
    for p in proclist:
        pr, ifn, ofn = p
        if pr is None:
            proclist.remove(p)
        elif pr.poll() is not None:
            logging.info('Conversion of {} to {} finished.'.format(ifn, ofn))
            proclist.remove(p)
    sleep(0.5)


if __name__ == '__main__':
    main(sys.argv)

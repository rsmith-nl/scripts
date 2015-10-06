#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-10-06 21:32:19 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to vid2mp4.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert all video files given on the command line to H.264/AAC streams in
an MP4 container."""

__version__ = '1.2.0'

from functools import partial
from multiprocessing import cpu_count
from time import sleep
import argparse
import logging
import os
import subprocess
import sys


def main(argv):
    """
    Entry point for vid2mp4.

    Arguments:
        argv: Command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    crfh = 'constant rate factor (lower is better, default 29)'
    parser.add_argument('-c', '--crf', type=int, default=29, help=crfh)
    parser.add_argument('-p', '--preset', default='medium',
                        choices=['ultrafast', 'superfast', 'veryfast',
                                 'faster', 'fast', 'medium', 'slow', 'slower',
                                 'veryslow'],
                        help='preset (default medium) slower is smaller file')
    parser.add_argument('--log', default='warning',
                        choices=['debug', 'info', 'warning', 'error'],
                        help="logging level (defaults to 'warning')")
    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__)
    parser.add_argument("files", metavar='file', nargs='*',
                        help="one or more files to process")
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                        format='%(levelname)s: %(message)s')
    logging.info('command line arguments = {}'.format(argv))
    logging.info('parsed arguments = {}'.format(args))
    checkfor(['ffmpeg', '-version'])
    starter = partial(startencoder, crf=args.crf, preset=args.preset)
    procs = []
    maxprocs = cpu_count()
    for ifile in args.files:
        while len(procs) == maxprocs:
            manageprocs(procs)
        procs.append(starter(ifile))
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


def startencoder(fname, crf, preset):
    """
    Use ffmpeg to convert a video file to H.264/AAC streams in an MP4
    container.

    Arguments:
        fname: Name of the file to convert.
        crf: Constant rate factor. See ffmpeg docs.
        preset: Encoding preset. See ffmpeg docs.

    Returns:
        A 3-tuple of a Process, input path and output path.
    """
    basename, ext = os.path.splitext(fname)
    known = ['.mp4', '.avi', '.wmv', '.flv', '.mpg', '.mpeg', '.mov', '.ogv',
             '.mkv', '.webm']
    if ext.lower() not in known:
        ls = "File {} has unknown extension, ignoring it.".format(fname)
        logging.warning(ls)
        return (None, fname, None)
    ofn = basename + '.mp4'
    args = ['ffmpeg', '-i', fname, '-c:v', 'libx264', '-crf', str(crf),
            '-preset', preset, '-flags',  '+aic+mv4', '-c:a', 'libfaac',
            '-sn', '-y', ofn]
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
    logging.info(nr)
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
    main(sys.argv[1:])

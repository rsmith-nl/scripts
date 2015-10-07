#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-10-07 23:36:24 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to vid2mp4.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert all video files given on the command line to H.264/AAC streams in
an MP4 container."""

__version__ = '1.3.0'

from concurrent.futures import ThreadPoolExecutor
from functools import partial
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
    starter = partial(runencoder, crf=args.crf, preset=args.preset)
    with ThreadPoolExecutor() as tp:
        convs = tp.map(starter, args.files)
    convs = [(fn, rv) for fn, rv in convs if rv != 0]
    for fn, rv in convs:
        print('Conversion of {} failed, return code {}'.format(fn, rv))


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


def runencoder(fname, crf, preset):
    """
    Use ffmpeg to convert a video file to H.264/AAC streams in an MP4
    container.

    Arguments:
        fname: Name of the file to convert.
        crf: Constant rate factor. See ffmpeg docs.
        preset: Encoding preset. See ffmpeg docs.

    Returns:
        (fname, return value)
    """
    basename, ext = os.path.splitext(fname)
    known = ['.mp4', '.avi', '.wmv', '.flv', '.mpg', '.mpeg', '.mov', '.ogv',
             '.mkv', '.webm']
    if ext.lower() not in known:
        ls = "File {} has unknown extension, ignoring it.".format(fname)
        logging.warning(ls)
        return (fname, 0)
    ofn = basename + '.mp4'
    args = ['ffmpeg', '-i', fname, '-c:v', 'libx264', '-crf', str(crf),
            '-preset', preset, '-flags',  '+aic+mv4', '-c:a', 'libfaac',
            '-sn', '-y', ofn]
    logging.info('Starting conversion of "{}" to "{}"'.format(fname, ofn))
    rv = subprocess.call(args, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    logging.info('Finished "{}"'.format(ofn))
    return fname, rv


if __name__ == '__main__':
    main(sys.argv[1:])

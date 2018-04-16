#!/usr/bin/env python3
# file: vid2mkv.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2013-2017 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2013-11-16T18:41:21+01:00
# Last modified: 2018-04-16T22:41:38+0200
"""Convert video files to Theora/Vorbis streams in a Matroska container."""

from functools import partial
import argparse
import concurrent.futures as cf
import logging
import os
import subprocess
import sys

__version__ = '1.4.1'


def main(argv):
    """
    Entry point for vid2mkv.

    Arguments:
        argv: Command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-q',
        '--videoquality',
        type=int,
        default=6,
        help='video quality (0-10, default 6)')
    parser.add_argument(
        '-a',
        '--audioquality',
        type=int,
        default=3,
        help='audio quality (0-10, default 3)')
    parser.add_argument(
        '--log',
        default='warning',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'warning')")
    parser.add_argument(
        '-v', '--version', action='version', version=__version__)
    parser.add_argument(
        "files",
        metavar='file',
        nargs='+',
        help="one or more files to process")
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format='%(levelname)s: %(message)s')
    logging.debug('command line arguments = {}'.format(argv))
    logging.debug('parsed arguments = {}'.format(args))
    checkfor(['ffmpeg', '-version'])
    starter = partial(runencoder, vq=args.videoquality, aq=args.audioquality)
    errmsg = 'conversion of {} failed, return code {}'
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        fl = [tp.submit(starter, t) for t in args.files]
        for fut in cf.as_completed(fl):
            fn, rv = fut.result()
            if rv == 0:
                logging.info('finished "{}"'.format(fn))
            elif rv < 0:
                ls = 'file "{}" has unknown extension, ignoring it.'
                logging.warning(ls.format(fn))
            else:
                logging.error(errmsg.format(fn, rv))


def checkfor(args, rv=0):
    """
    Ensure that a program necessary for using this script is available.

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
        rc = subprocess.call(
            args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if rc != rv:
            raise OSError
        logging.info('found required program "{}"'.format(args[0]))
    except OSError as oops:
        outs = 'required program "{}" not found: {}.'
        logging.error(outs.format(args[0], oops.strerror))
        sys.exit(1)


def runencoder(fname, vq, aq):
    """
    Convert a video file to Theora/Vorbis streams in a Matroska container.

    Arguments:
        fname: Name of the file to convert.
        vq : Video quality. See ffmpeg docs.
        aq: Audio quality. See ffmpeg docs.

    Returns:
        (fname, return value)
    """
    basename, ext = os.path.splitext(fname)
    known = [
        '.mp4', '.avi', '.wmv', '.flv', '.mpg', '.mpeg', '.mov', '.ogv',
        '.mkv', '.webm', '.gif'
    ]
    if ext.lower() not in known:
        return (fname, -1)
    ofn = basename + '.mkv'
    args = [
        'ffmpeg', '-i', fname, '-c:v', 'libtheora', '-q:v',
        str(vq), '-c:a', 'libvorbis', '-q:a',
        str(aq), '-sn', '-y', ofn
    ]
    logging.debug(' '.join(args))
    logging.info('starting conversion of "{}".'.format(fname))
    rv = subprocess.call(
        args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return fname, rv


if __name__ == '__main__':
    main(sys.argv[1:])

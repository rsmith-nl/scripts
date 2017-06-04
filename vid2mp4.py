#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2017-06-04 13:57:48 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to vid2mp4.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/
"""Convert video files to H.264/AAC streams in an MP4 container."""

from functools import partial
import argparse
import concurrent.futures as cf
import logging
import os
import subprocess
import sys

__version__ = '1.5.1'


def main(argv):
    """
    Entry point for vid2mp4.

    Arguments:
        argv: Command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    crfh = 'constant rate factor (lower is better, default 29)'
    parser.add_argument('-c', '--crf', type=int, default=29, help=crfh)
    parser.add_argument(
        '-p',
        '--preset',
        default='medium',
        choices=[
            'ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium',
            'slow', 'slower', 'veryslow'
        ],
        help='preset (default medium) slower is smaller file')
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
    starter = partial(runencoder, crf=args.crf, preset=args.preset)
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


def runencoder(fname, crf, preset):
    """
    Convert a video file to H.264/AAC streams in an MP4 container.

    Arguments:
        fname: Name of the file to convert.
        crf: Constant rate factor. See ffmpeg docs.
        preset: Encoding preset. See ffmpeg docs.

    Returns:
        (fname, return value)
    """
    basename, ext = os.path.splitext(fname)
    known = [
        '.mp4', '.avi', '.wmv', '.flv', '.mpg', '.mpeg', '.mov', '.ogv',
        '.mkv', '.webm', '.gif'
    ]
    if ext.lower() not in known:
        return fname, -1
    ofn = basename + '.mp4'
    args = [
        'ffmpeg', '-i', fname, '-c:v', 'libx264', '-crf',
        str(crf), '-preset', preset, '-flags', '+aic+mv4', '-c:a', 'aac',
        '-sn', '-y', ofn
    ]
    logging.debug(' '.join(args))
    logging.info('starting conversion of "{}".'.format(fname))
    rv = subprocess.call(
        args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return fname, rv


if __name__ == '__main__':
    main(sys.argv[1:])

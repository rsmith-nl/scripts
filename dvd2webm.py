#!/usr/bin/env python3
# file: dvd2webm.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-02-10 22:42:09 +0100
# Last modified: 2017-10-08 11:12:01 +0200
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to dvd2webm.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/
"""
Convert an mpeg stream from a DVD to a webm file, using constrained rate VP9
encoding for video and libvorbis for audio.

It uses the first video stream and the first audio stream, unless otherwise
indicated.
"""

from collections import Counter
from datetime import datetime
import argparse
import logging
import os
import re
import subprocess as sp
import sys

__version__ = '0.8.2'


def main(argv):
    """Entry point for dvd2webm.py."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--log',
        default='info',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'info')")
    parser.add_argument(
        '-v', '--version', action='version', version=__version__)
    parser.add_argument(
        '-s',
        '--start',
        type=str,
        help="time (hh:mm:ss) at which to start encoding")
    parser.add_argument('-c', '--crop', type=str, help="crop (w:h:x:y) to use")
    parser.add_argument(
        '-t', '--subtitle', type=str, help="name of srt file for subtitles")
    ahelp = "number of the audio track to use (default: 0; first audio track)"
    parser.add_argument('-a', '--audio', type=int, default=0, help=ahelp)
    parser.add_argument('fn', metavar='filename', help='MPEG file to process')
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format='%(levelname)s: %(message)s')
    logging.debug('command line arguments = {}'.format(argv))
    logging.debug('parsed arguments = {}'.format(args))
    logging.info("processing '{}'.".format(args.fn))
    logging.info('started at {}.'.format(str(datetime.now())[:-7]))
    logging.info('using audio stream {}.'.format(args.audio))
    if not args.crop:
        logging.info('looking for cropping.')
        args.crop = findcrop(args.fn)
        width, height, _, _ = args.crop.split(':')
        if width in ['720', '704'] and height == '576':
            logging.info('standard format, no cropping necessary.')
            args.crop = None
    a1, a2 = mkargs(args.fn, args.crop, args.start, args.subtitle, args.audio)
    encode(a1, a2)


def findcrop(path, start='00:10:00', duration='00:00:01'):
    """
    Find the cropping of the video file.

    Arguments:
        path: location of the file to query.
        start: A string that defines where in the movie to start scanning.
            Defaults to 10 minutes from the start. Format HH:MM:SS.
        duration: A string defining how much of the movie to scan. Defaults to
            one second. Format HH:MM:SS.

    Returns:
        A string containing the cropping to use with ffmpeg.
    """
    args = [
        'ffmpeg',
        '-hide_banner',
        '-ss',
        start,  # Start at 10 minutes in.
        '-t',
        duration,  # Parse for one second.
        '-i',
        path,  # Path to the input file.
        '-vf',
        'cropdetect',  # Use the crop detect filter.
        '-an',  # Disable audio output.
        '-y',  # Overwrite output without asking.
        '-f',
        'rawvideo',  # write raw video output.
        '/dev/null'  # Write output to /dev/null
    ]
    proc = sp.run(
        args, universal_newlines=True, stdout=sp.DEVNULL, stderr=sp.PIPE)
    rv = Counter(re.findall('crop=(\d+:\d+:\d+:\d+)', proc.stderr))
    return rv.most_common(1)[0][0]


def reporttime(p, start, end):
    """
    Report the amount of time passed between start and end.

    Arguments:
        start: datetime.datetime instance.
        end: datetime.datetime instance.
    """
    dt = str(end - start)
    logging.info('pass {} took {}.'.format(p, dt[:-7]))


def mkargs(fn, crop, start, subfname, atrack):
    """
    Create argument lists for constrained quality VP9/vorbis encoding.

    Arguments:
        fn: Path of the input file.
        crop: String telling ffmeg how to crop in the format w:h:x:y.
        start: String telling ffmeg the time when to start encoding.
        subfname: Path of the SRT subtitles file.
        atrack: number of the audio track (0-based indexing)

    Returns:
        A tuple (args1, args2) which are the argument lists for starting
        subprocesses for the first and second step respectively.
    """
    basename = fn.rsplit('.', 1)[0]
    numcolumns = '1'
    numthreads = str(os.cpu_count() - 1)
    logging.info('using {} threads.'.format(numthreads))
    # TODO: Add ‘--row-mt=1’ to args1 and args2 after libvpx-1.6.2 comes out.
    # In that case, also set ‘numthreads = str(2*os.cpu_count())’
    # See https://github.com/Kagami/webm.py/wiki/Notes-on-encoding-settings
    args1 = [
        'ffmpeg', '-loglevel', 'quiet', '-i', fn, '-passlogfile', basename,
        '-c:v', 'libvpx-vp9', '-threads', numthreads, '-pass', '1', '-sn',
        '-b:v', '1400k', '-crf', '33', '-g', '250', '-speed', '4',
        '-tile-columns', numcolumns, '-an', '-f', 'webm', '-map', '0:v',
        '-map', '0:a:{}'.format(atrack), '-y', '/dev/null'
    ]
    args2 = [
        'ffmpeg', '-loglevel', 'quiet', '-i', fn, '-passlogfile', basename,
        '-c:v', 'libvpx-vp9', '-threads', numthreads, '-pass', '2', '-sn',
        '-b:v', '1400k', '-crf', '33', '-g', '250', '-speed', '2',
        '-tile-columns', numcolumns, '-auto-alt-ref', '1', '-lag-in-frames',
        '25', '-c:a', 'libvorbis', '-q:a', '3', '-f', 'webm', '-map', '0:v',
        '-map', '0:a:{}'.format(atrack), '-y', '{}.webm'.format(basename)
    ]
    vf = []
    if subfname:
        logging.info("using subtitles from '{}'.".format(subfname))
        vf.append('subtitles={}'.format(subfname))
    if crop:
        logging.info('using cropping {}.'.format(crop))
        vf.append('crop={}'.format(crop))
    if vf:
        opts = ','.join(vf)
        logging.debug('vf options: {}.'.format(opts))
        args1.insert(-2, '-vf')
        args2.insert(-2, '-vf')
        args1.insert(-2, opts)
        args2.insert(-2, opts)
    if start:
        logging.info("starting encoding at {}.".format(start))
        args1.insert(3, '-ss')
        args2.insert(3, '-ss')
        args1.insert(4, start)
        args2.insert(4, start)
    logging.debug('first pass: ' + ' '.join(args1))
    logging.debug('second pass: ' + ' '.join(args2))
    return args1, args2


def encode(args1, args2):
    """
    Run the encoding subprocesses.

    Arguments:
        args1: Commands to run the first encoding step as a subprocess.
        args2: Commands to run the second encoding step as a subprocess.
    """
    logging.info('running pass 1...')
    logging.debug('pass 1: {}'.format(' '.join(args1)))
    start = datetime.utcnow()
    proc = sp.run(args1, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    end = datetime.utcnow()
    if proc.returncode:
        logging.error('pass 1 returned {}.'.format(proc.returncode))
        return
    else:
        reporttime(1, start, end)
    logging.info('running pass 2...')
    logging.debug('pass 2: {}'.format(' '.join(args2)))
    start = datetime.utcnow()
    proc = sp.run(args2, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    end = datetime.utcnow()
    if proc.returncode:
        logging.error('pass 2 returned {}.'.format(proc.returncode))
    else:
        reporttime(2, start, end)
    oidx = args2.index('-i') + 1
    origsize = os.path.getsize(args2[oidx])
    newsize = os.path.getsize(args2[-1])
    percentage = int(100 * newsize / origsize)
    sz = "the size of '{}' is {}% of the size of '{}'."
    logging.info(sz.format(args2[-1], percentage, args2[4]))


if __name__ == '__main__':
    main(sys.argv[1:])

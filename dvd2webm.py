#!/usr/bin/env python3
# file: dvd2webm.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-02-10 22:42:09 +0100
# Last modified: 2018-02-25 03:04:55 +0100
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

__version__ = '0.10.0'


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
        default=None,
        help="time (hh:mm:ss) at which to start encoding")
    parser.add_argument('-c', '--crop', type=str, help="crop (w:h:x:y) to use")
    parser.add_argument('-d', '--dummy', action="store_true",
                        help="print commands but do not run them")
    parser.add_argument(
        '-t', '--subtitle', type=str, help="srt file or dvdsub track number")
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
    starttime = datetime.now()
    logging.info('started at {}.'.format(str(starttime)[:-7]))
    logging.info('using audio stream {}.'.format(args.audio))
    if not args.crop:
        logging.info('looking for cropping.')
        args.crop = findcrop(args.fn)
        width, height, _, _ = args.crop.split(':')
        if width in ['720', '704'] and height == '576':
            logging.info('standard format, no cropping necessary.')
            args.crop = None
    if args.crop:
        logging.info('using cropping ' + args.crop)
    subtrack, srtfile = None, None
    if args.subtitle:
        try:
            subtrack = str(int(args.subtitle))
            logging.info('using subtitle track ' + subtrack)
        except ValueError:
            srtfile = args.subtitle
            logging.info('using subtitle file ' + srtfile)
    a1 = mkargs(args.fn, 1, crop=args.crop, start=args.start, subf=srtfile,
                subt=subtrack, atrack=args.audio)
    a2 = mkargs(args.fn, 2, crop=args.crop, start=args.start, subf=srtfile,
                subt=subtrack, atrack=args.audio)
    if not args.dummy:
        origbytes, newbytes = encode(a1, a2)
    else:
        logging.basicConfig(level='INFO')
        logging.info('first pass: ' + ' '.join(a1))
        logging.info('second pass: ' + ' '.join(a2))
    stoptime = datetime.now()
    logging.info('ended at {}.'.format(str(stoptime)[:-7]))
    runtime = stoptime - starttime
    logging.info('total running time {}.'.format(str(runtime)[:-7]))
    encspeed = origbytes/(runtime.seconds*1000)
    logging.info('average input encoding speed {:.2f} kB/s.'.format(encspeed))


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
        p: number of the pass.
        start: datetime.datetime instance.
        end: datetime.datetime instance.
    """
    dt = str(end - start)
    logging.info('pass {} took {}.'.format(p, dt[:-7]))


def mkargs(fn, npass, crop=None, start=None, subf=None, subt=None,
           atrack=0):
    """Create argument list for constrained quality VP9/vorbis encoding.

    Arguments:
        fn: String containing the path of the input file
        npass: Number of the pass. Must be 1 or 2.
        crop: Optional string containing the cropping to use. Must be in the
            format W:H:X:Y, where W, H, X and Y are numbers.
        start: Optional string containing the start time for the conversion.
            Must be in the format HH:MM:SS, where H, M and S are digits.
        subf: Optional string containing the name of the SRT file to use.
        subt: Optional string containing the index of the dvdsub stream to use.
        atrack: Optional number of the audio track to use. Defaults to 0.

    Returns:
        A list of strings suitable for calling a subprocess.
    """
    if npass not in (1, 2):
        raise ValueError('npass must be 1 or 2')
    if crop and not re.search('\d+:\d+:\d+:\d+', crop):
        raise ValueError('cropping must be in the format W:H:X:Y')
    if start and not re.search('\d{2}:\d{2}:\d{2}', start):
        raise ValueError('starting time must be in the format HH:MM:SS')
    numthreads = str(os.cpu_count() - 1)
    basename = fn.rsplit('.', 1)[0]
    args = ['ffmpeg',  '-loglevel',  'quiet']
    if start:
        args += ['-ss',  start]
    args += ['-i', fn, '-passlogfile', basename]
    speed = '2'
    if npass == 1:
        speed = '4'
    args += ['-c:v', 'libvpx-vp9', '-row-mt=1' '-threads', numthreads, '-pass',
             str(npass), '-b:v', '1400k', '-crf', '33', '-g', '250',
             '-speed', speed, '-tile-columns', '1']
    if npass == 2:
        args += ['-auto-alt-ref', '1', '-lag-in-frames', '25']
    args += ['-sn']
    if npass == 1:
        args += ['-an']
    elif npass == 2:
        args += ['-c:a', 'libvorbis', '-q:a', '3']
    args += ['-f', 'webm']
    if not subt:  # SRT file
        args += ['-map', '0:v', '-map', '0:a:{}'.format(atrack)]
        vf = []
        if subf:
            vf = ['subtitles={}'.format(subf)]
        if crop:
            vf.append('crop={}'.format(crop))
        if vf:
            args += ['-vf', ','.join(vf)]
    else:
        fc = '[0:v][0:s:{}]overlay'.format(subt)
        if crop:
            fc += ',crop={}[v]'.format(crop)
        args += ['-filter_complex', fc, '-map', '[v]', '-map',
                 '0:a:{}'.format(atrack)]
    if npass == 1:
        outname = '/dev/null'
    else:
        outname = basename + '.webm'
    args += ['-y',  outname]
    return args


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
        return None, None
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
    return origsize, newsize  # both in bytes.


if __name__ == '__main__':
    main(sys.argv[1:])

#!/usr/bin/env python3
# file: vid2av1.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2019-05-11T19:49:00+0200
# Last modified: 2019-05-12T21:30:41+0200
"""
Convert videos to an MP4 container with AV1 video and Opus audio.
"""

from datetime import datetime
import argparse
import logging
import os
import re
import subprocess as sp
import sys

__version__ = '0.1'


def main(argv):
    """Entry point for vid2webm.py."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--log',
        default='info',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'info')"
    )
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument(
        '-s', '--start', type=str, default=None, help="time (hh:mm:ss) at which to start encoding"
    )
    parser.add_argument(
        '-d', '--dummy', action="store_true", help="print commands but do not run them"
    )
    parser.add_argument("files", metavar='files', nargs='+', help="one or more files to process")
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None), format='%(levelname)s: %(message)s'
    )
    logging.debug(f'command line arguments = {argv}')
    logging.debug(f'parsed arguments = {args}')
    if not check_ffmpeg():
        return 1
    for fn in args.files:
        logging.info(f"processing '{fn}'.")
        starttime = datetime.now()
        startstr = str(starttime)[:-7]
        logging.info(f'started at {startstr}.')
        a1 = mkargs(fn, start=args.start)
        if not args.dummy:
            origbytes, newbytes = encode(a1)
        else:
            logging.basicConfig(level='INFO')
            logging.info('encoding command would be: ' + ' '.join(a1))
            continue
        stoptime = datetime.now()
        stopstr = str(stoptime)[:-7]
        logging.info(f'ended at {stopstr}.')
        runtime = stoptime - starttime
        runstr = str(runtime)[:-7]
        logging.info(f'total running time {runstr}.')
        encspeed = origbytes / (runtime.seconds * 1000)
        logging.info(f'average input encoding speed {encspeed:.2f} kB/s.')


def check_ffmpeg():
    """Check the minumum version requirement of ffmpeg, and that it is built with
    the needed drivers enabled."""
    args = ['ffmpeg']
    proc = sp.run(args, universal_newlines=True, stdout=sp.DEVNULL, stderr=sp.PIPE)
    verre = r'ffmpeg version (\d+)\.(\d+)(\.(\d+))? Copyright'
    major, minor, patch, *rest = re.findall(verre, proc.stderr)[0]
    if int(major) < 4 and int(minor) < 1:
        logging.error(f'ffmpeg 4.1 or later is required; found {major}.{minor}.{patch}')
        return False
    if not re.search(r'enable-libaom', proc.stderr):
        logging.error('ffmpeg is not built with AV1 video support.')
        return False
    if not re.search(r'enable-libopus', proc.stderr):
        logging.error('ffmpeg is not built with Opus audio support.')
        return False
    return True


def reporttime(dt):
    """
    Report the amount of time passed between start and end.

    Arguments:
        dt: datetime.timedelta instance.
    """
    s = str(dt)[:-7]
    logging.info(f'encoding took {s}.')


def mkargs(path, start=None):
    """Create argument list for constrained quality AV1/Opus encoding.

    Arguments:
        path: String containing the path of the input file
        start: Optional string containing the start time for the conversion.
            Must be in the format HH:MM:SS, where H, M and S are digits.

    Returns:
        A list of strings suitable for calling a subprocess.
    """
    if start and not re.search(r'\d{2}:\d{2}:\d{2}', start):
        raise ValueError('starting time must be in the format HH:MM:SS')
    pathpart, filepart = os.path.split(path)
    basename, ext = os.path.splitext(filepart)
    del filepart
    # Basic arguments
    args = ['ffmpeg', '-loglevel', 'quiet', '-probesize', '1G', '-analyzeduration', '1G']
    if start:
        args += ['-ss', start]
    # Input filename
    args += ['-i', path]
    # Video options
    args += [
        '-c:v', 'libaom-av1', '-crf', '30', '-b:v', '2M', '-strict', 'experimental',
        '-row-mt', '1', '-tiles', '3x1'
    ]
    # Audio options
    args += ['-c:a', 'libopus']
    # Stream mapping options
    args += ['-map', '0:v', '-map', '0:a']
    # Use prefix if original extenstion is already MP4.
    if ext == '.mp4':
        suffix = '-av1'
    else:
        suffix = ''
    outname = os.path.join(pathpart, ''.join([basename, suffix, '.mp4']))
    args += ['-y', outname]
    return args


def encode(args):
    """
    Run the encoding subproces.

    Arguments:
        args: Commands to run the encoding step as a subprocess.

    Return values:
        A 2-tuple of the original movie size in bytes and the encoded movie size in bytes.
    """
    oidx = args.index('-i') + 1
    origsize = os.path.getsize(args[oidx])
    logging.info('running enciding...')
    logging.debug('encoding command: {}'.format(' '.join(args)))
    start = datetime.utcnow()
    proc = sp.run(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    end = datetime.utcnow()
    if proc.returncode:
        logging.error(f'encoding returned {proc.returncode}.')
        return origsize, 0
    else:
        dt = end - start
        reporttime(1, dt)
    newsize = os.path.getsize(args[-1])
    percentage = int(100 * newsize / origsize)
    ifn, ofn = args[oidx], args[-1]
    logging.info(f"the size of '{ofn}' is {percentage}% of the size of '{ifn}'.")
    return origsize, newsize  # both in bytes.


if __name__ == '__main__':
    main(sys.argv[1:])

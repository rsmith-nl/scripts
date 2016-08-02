#!/usr/bin/env python3
# file: dvd2webm.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-02-10 22:42:09 +0100
# Last modified: 2016-08-02 19:32:31 +0200
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to dvd2webm.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert an mpeg stream from a DVD to a webm file."""

from datetime import datetime
import argparse
import json
import logging
import math
import os
import subprocess as sp
import sys

__version__ = '0.5.0'


def main(argv):
    """Entry point for dvd2webm.py."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', default='info',
                        choices=['debug', 'info', 'warning', 'error'],
                        help="logging level (defaults to 'info')")
    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__)
    parser.add_argument('-s', '--start', type=str,
                        help="time (hh:mm:ss) at which to start encoding")
    parser.add_argument('-c', '--crop', type=str,
                        help="crop (w:h:x:y) to use")
    parser.add_argument('-t', '--subtitle', type=str,
                        help="name of srt file for subtitles")
    parser.add_argument('fn', metavar='filename', help='MPEG file to process')
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                        format='%(levelname)s: %(message)s')
    logging.debug('command line arguments = {}'.format(argv))
    logging.debug('parsed arguments = {}'.format(args))
    logging.info("processing '{}'".format(args.fn))
    if args.crop:
        logging.info('using cropping {}'.format(args.crop))
    vdata = vidinfo(args.fn)
    encode(args.fn, args.crop, args.start, args.subtitle, vdata["width"])


def vidinfo(path):
    args = ['ffprobe', '-hide_banner', '-show_streams', '-select_streams',
            'v:0', '-of', 'json', path]
    rv = sp.check_output(args, stderr=sp.DEVNULL, universal_newlines=True)
    vdata = json.loads(rv)["streams"][0]
    return vdata


def reporttime(p, start, end):
    dt = str(end - start)
    logging.info('pass {} took {}.'.format(p, dt[:-7]))


def encode(fn, crop, start, subfname, width):
    basename = fn.rsplit('.', 1)[0]
    numcolumns = str(int(math.log2(width/256)))
    logging.info('using {} tile-columns'.format(numcolumns))
    numthreads = str(os.cpu_count() - 1)
    logging.info('using {} threads'.format(numthreads))
    args = ['ffmpeg', '-loglevel', 'quiet', '-i', fn, '-passlogfile', basename,
            '-c:v', 'libvpx-vp9', '-threads', numthreads, '-pass', '1', '-sn',
            '-b:v', '1400k', '-crf', '33', '-g', '250', '-speed', '4',
            '-tile-columns', numcolumns, '-an', '-f', 'webm',
            '-map', 'i:0x1e0', '-map', 'i:0x80', '-y', '/dev/null']
    args2 = ['ffmpeg', '-loglevel', 'quiet', '-i', fn,
             '-passlogfile', basename, '-c:v', 'libvpx-vp9',
             '-threads', numthreads, '-pass', '2', '-sn', '-b:v', '1400k',
             '-crf', '33', '-g', '250', '-speed', '2',
             '-tile-columns', numcolumns, '-auto-alt-ref', '1',
             '-lag-in-frames', '25', '-c:a', 'libvorbis', '-q:a', '3',
             '-f', 'webm', '-map', 'i:0x1e0', '-map', 'i:0x80',
             '-y', '{}.webm'.format(basename)]
    vf = []
    if subfname:
        vf.append('subtitles={}'.format(subfname))
    if crop:
        vf.append('crop={}'.format(crop))
    if vf:
        opts = ','.join(vf)
        logging.debug('vf options: {}'.format(opts))
        args.insert(-2, '-vf')
        args2.insert(-2, '-vf')
        args.insert(-2, opts)
        args2.insert(-2, opts)
    if start:
        args.insert(3, '-ss')
        args2.insert(3, '-ss')
        args.insert(4, start)
        args2.insert(4, start)
    logging.debug('first pass: ' + ' '.join(args))
    logging.debug('second pass: ' + ' '.join(args2))
    logging.info('running pass 1...')
    start = datetime.utcnow()
    proc = sp.run(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    end = datetime.utcnow()
    if proc.returncode:
        logging.error('pass 1 returned {}'.format(proc.returncode))
        return
    else:
        reporttime(1, start, end)
    logging.info('running pass 2...')
    start = datetime.utcnow()
    proc = sp.run(args2, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    end = datetime.utcnow()
    if proc.returncode:
        logging.error('pass 2 returned {}'.format(proc.returncode))
    else:
        reporttime(2, start, end)


if __name__ == '__main__':
    main(sys.argv[1:])

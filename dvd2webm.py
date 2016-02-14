#!/usr/bin/env python3
# file: dvd2webm.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-02-10 22:42:09 +0100
# Last modified: 2016-02-14 15:06:50 +0100
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to dvd2webm.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert an mpeg stream from a DVD to a webm file."""

from collections import Counter
import argparse
import logging
import re
import subprocess as sp
import sys

__version__ = '0.2.0'


def main(argv):
    """Entry point for dvd2webm.py."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', default='warning',
                        choices=['debug', 'info', 'warning', 'error'],
                        help="logging level (defaults to 'warning')")
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
    if not args.crop:
        args.crop = cropdetect(args.fn)
    logging.info('use cropping {}'.format(args.crop))
    encode(args.fn, args.crop, args.start, args.subtitle)


def cropdetect(fn):
    args = ['ffmpeg', '-hide_banner', '-ss', '00:08:00', '-i', fn, '-vf',
            'cropdetect', '-y', '-f', 'avi', '-to', '00:01:00', '/dev/null']
    proc = sp.run(args, stdout=sp.PIPE, stderr=sp.PIPE, timeout=60)
    croppings = re.findall('crop=([:0-9]+)', proc.stderr.decode('utf-8'))
    cnt = Counter(croppings)
    logging.info('{} croppings detected'.format(len(cnt)))
    return cnt.most_common(1)[0][0]


def encode(fn, crop, start, subfname):
    basename = fn.rsplit('.', 1)[0]
    args = ['ffmpeg', '-loglevel', 'quiet', '-i', fn, '-passlogfile', basename,
            '-c:v', 'libvpx-vp9', '-threads', '3', '-pass', '1', '-sn',
            '-b:v', '1400k', '-crf', '33', '-g', '250', '-speed', '4',
            '-tile-columns', '4', '-an', '-f', 'webm', '-map', 'i:0x1e0',
            '-map', 'i:0x80', '-y', '/dev/null']
    args2 = ['ffmpeg', '-loglevel', 'quiet', '-i', fn,
             '-passlogfile', basename, '-c:v', 'libvpx-vp9', '-threads', '3',
             '-pass', '2', '-sn', '-b:v', '1400k', '-crf', '33', '-g', '250',
             '-speed', '2', '-tile-columns', '4', '-auto-alt-ref', '1',
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
    logging.debug('first step: ' + ' '.join(args))
    logging.debug('second step: ' + ' '.join(args2))
    logging.info('running step 1...')
    proc = sp.run(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    if proc.returncode:
        logging.error('pass 1 returned {}'.format(proc.returncode))
        return
    logging.info('running step 2...')
    proc = sp.run(args2, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    if proc.returncode:
        logging.error('pass 2 returned {}'.format(proc.returncode))


if __name__ == '__main__':
    main(sys.argv[1:])

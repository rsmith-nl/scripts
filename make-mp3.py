#!/usr/bin/env python3
# file: make-mp3.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2012-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2012-12-22T01:26:10+01:00
# Last modified: 2020-04-01T00:21:33+0200
"""
Encodes WAV files from cdparanoia (“trackNN.cdda.wav”) to MP3 format.

Processing is done in parallel using as many subprocesses as the machine has
cores.

Information w.r.t. artist, song titles et cetera is gathered from a text file
called “album.json”, which should have the following info;

    {
        "title": "title of the album",
        "artist": "name of the artist",
        "year": 1985,
        "genre": "rock",
        "tracks": [
            "foo",
            "bar",
            "spam",
            "eggs"
        ]
    }
"""

from functools import partial
import argparse
import concurrent.futures as cf
import json
import logging
import os
import subprocess as sp
import sys

__version__ = '2.1.0'


def main():
    """Entry point for make-mp3."""
    tfn = 'album.json'
    with open(tfn) as jf:
        data = json.load(jf)
    keys = data.keys()
    for key in ['title', 'year', 'genre', 'artist', 'tracks']:
        if key not in keys:
            logging.error(f'key "{key}" not in "{tfn}"')
            sys.exit(1)
    logging.info('album name: ' + data['title'])
    logging.info('artist: ' + data['artist'])
    logging.info('year: ' + str(data['year']))
    logging.info('genre: ' + data['genre'])
    num = len(data['tracks'])
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        for idx, rv in tp.map(partial(runmp3, data=data), range(num)):
            tnum = idx + 1
            if rv == 0:
                tt = data['tracks'][idx]
                logging.info(f'finished track {tnum}, "{tt}"')
            else:
                logging.error(f'conversion of track {tnum} failed, return code {rv}')


def setup():
    """Process command-line arguments. Check for required programs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--log',
        default='warning',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'warning')"
    )
    parser.add_argument('-v', '--version', action='version', version=__version__)
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None), format='%(levelname)s: %(message)s'
    )
    logging.debug(f'command line arguments = {sys.argv}')
    logging.debug(f'parsed arguments = {args}')
    # Check for required programs.
    try:
        sp.run(['lame'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        logging.info('found “lame”')
    except FileNotFoundError:
        logging.error('the program “lame” cannot be found')
        sys.exit(1)


def runmp3(idx, data):
    """
    Use the lame(1) program to convert a music file to MP3 format.

    Arguments:
        idx: track index (starts from 0)
        data: album data dictionary

    Returns:
        A tuple containing the track index and return value of lame.
    """
    num = idx + 1
    args = [
        'lame', '-S', '--preset', 'standard', '--tt', data['tracks'][idx], '--ta', data['artist'],
        '--tl', data['title'], '--ty', str(data['year']), '--tn', '{:02d}'.format(num),
        '--tg', data['genre'], f'track{num:02d}.cdda.wav', f'track{num:02d}.mp3'
    ]
    p = sp.run(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    return (idx, p.returncode)


if __name__ == '__main__':
    main()

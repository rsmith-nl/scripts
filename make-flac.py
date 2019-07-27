#!/usr/bin/env python3
# file: make-flac.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2012-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2012-12-22T00:12:03+01:00
# Last modified: 2019-07-27T16:00:11+0200
"""
Encodes WAV files from cdparanoia (“trackNN.cdda.wav”) to FLAC format.

Processing is done in parallel using as many subprocesses as the machine has
cores.

Information w.r.t. artist, song titles et cetera is gathered from a text file
called “album.json”, which should have the following format;

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

__version__ = '2.2.0'


def main(argv):
    """Entry point for make-flac."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--log',
        default='warning',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'warning')"
    )
    parser.add_argument('-v', '--version', action='version', version=__version__)
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None), format='%(levelname)s: %(message)s'
    )
    logging.debug(f'command line arguments = {argv}')
    logging.debug(f'parsed arguments = {args}')
    checkfor('flac')
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
        for idx, rv in tp.map(partial(runflac, data=data), range(num)):
            tnum = idx + 1
            if rv == 0:
                tt = data['tracks'][idx]
                logging.info(f'finished track {tnum}, "{tt}"')
            else:
                logging.error(f'conversion of track {tnum} failed, return code {rv}')


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
    else:
        if not isinstance(args, (list, tuple)):
            raise ValueError('args should be a list or tuple')
        if not all(isinstance(x, str) for x in args):
            raise ValueError('args should be a list or tuple of strings')
    try:
        cp = sp.run(args)
    except FileNotFoundError as oops:
        logging.error(f'required program "{args[0]}" not found: {oops.strerror}.')
        sys.exit(1)
    if cp.returncode != rv:
        logging.error(f'returncode {cp.returncode} should be {rv}')
        sys.exit(1)
    logging.info(f'found required program "{args[0]}"')


def runflac(idx, data):
    """
    Use the flac(1) program to convert a music file to FLAC format.

    Arguments:
        idx: track index (starts from 0)
        data: album data dictionary

    Returns:
        A tuple containing the track index and return value of flac.
    """
    num = idx + 1
    ifn = f'track{num:02d}.cdda.wav'
    args = [
        'flac', '--best', '--totally-silent', '-TARTIST=' + data['artist'],
        '-TALBUM=' + data['title'], '-TTITLE=' + data['tracks'][idx],
        '-TDATE=' + str(data['year']), '-TGENRE=' + data['genre'],
        f'-TTRACKNUM={num:02d}', '-o', f'track{num:02d}.flac', ifn
    ]
    p = sp.run(args)
    return (idx, p.returncode)


if __name__ == '__main__':
    main(sys.argv[1:])

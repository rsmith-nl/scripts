#!/usr/bin/env python3
# file: make-flac.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2012-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2012-12-22T00:12:03+01:00
# Last modified: 2018-04-16T22:14:11+0200
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
import subprocess
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
    logging.debug('command line arguments = {}'.format(argv))
    logging.debug('parsed arguments = {}'.format(args))
    checkfor('flac')
    tfn = 'album.json'
    with open(tfn) as jf:
        data = json.load(jf)
    keys = data.keys()
    errmsg = 'key "{}" not in "{}"'
    for key in ['title', 'year', 'genre', 'artist', 'tracks']:
        if key not in keys:
            logging.error(errmsg.format(key, tfn))
            sys.exit(1)
    logging.info('album name: {}'.format(data['title']))
    logging.info('artist: {}'.format(data['artist']))
    logging.info('year: {}'.format(data['year']))
    logging.info('genre: {}'.format(data['genre']))
    errmsg = 'conversion of track {} failed, return code {}'
    okmsg = 'finished track {}, "{}"'
    num = len(data['tracks'])
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        for idx, rv in tp.map(partial(runflac, data=data), range(num)):
            if rv == 0:
                logging.info(okmsg.format(idx + 1, data['tracks'][idx]))
            else:
                logging.error(errmsg.format(idx + 1, rv))


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
        rc = subprocess.call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if rc != rv:
            raise OSError
        logging.info('found required program "{}"'.format(args[0]))
    except OSError as oops:
        outs = 'required program "{}" not found: {}.'
        logging.error(outs.format(args[0], oops.strerror))
        sys.exit(1)


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
    ifn = 'track{:02d}.cdda.wav'.format(num)
    args = [
        'flac', '--best', '--totally-silent', '-TARTIST=' + data['artist'],
        '-TALBUM=' + data['title'], '-TTITLE=' + data['tracks'][idx],
        '-TDATE={}'.format(data['year']), '-TGENRE={}'.format(data['genre']),
        '-TTRACKNUM={:02d}'.format(num), '-o', 'track{:02d}.flac'.format(num), ifn
    ]
    rv = subprocess.call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return (idx, rv)


if __name__ == '__main__':
    main(sys.argv[1:])

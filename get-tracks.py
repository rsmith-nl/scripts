#!/usr/bin/env python3
# file: get-tracks.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2017-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2017-09-10T12:15:13+02:00
# Last modified: 2019-07-30T15:31:11+0200
"""Retrieve the numbered tracks from a dvd."""

import logging
import sys
import subprocess as sp

__version__ = '1.1'


def main(argv):
    """
    Entry point for get-tracks.py.

    Arguments:
        argv: command line arguments
    """
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    DVD = '/dev/cd1'
    if len(argv) == 0:
        print('get-tracks version', __version__)
        print('Example: get-tracks 3 4 5 retrieves tracks 3, 4 and 5')
        exit(0)
    # Check for required programs.
    try:
        sp.run(['tccat'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        logging.info('found “tccat”')
    except FileNotFoundError:
        logging.error('the program “tccat” cannot be found')
        sys.exit(1)
    for a in argv:
        try:
            retrieve(DVD, int(a))
        except ValueError:
            print(f'"{a}" is not an integer, skipping')


def retrieve(dvddev, num):
    """Use `tccat` to retrieve a track from DVD.

    Without the -P argument some DVD's aren't retrieved correctly.

    Arguments:
        dvddev: String containing the device node for the DVD.
        num: The integer number of a track to retrieve.
    """
    args = ['tccat', '-i', dvddev, '-T', f'{num},-1', '-P']
    trackname = f'track{num:02d}.mpg'
    logging.info(f'writing track {num} as "{trackname}"... ')
    with open(trackname, 'wb') as outf:
        sp.run(args, stdout=outf, stderr=sp.DEVNULL)
    logging.info('done.')


if __name__ == '__main__':
    main(sys.argv[1:])

#!/usr/bin/env python3
# file: get-tracks.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2017-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2017-09-10T12:15:13+02:00
# Last modified: 2019-07-27T15:59:11+0200
"""Retrieve the numbered tracks from a dvd."""

import logging
import sys
import subprocess as sp

__version__ = '1.1'


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
    checkfor(['tccat', '-v'])
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

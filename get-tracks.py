#!/usr/bin/env python3
# file: get-tracks.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2017-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2017-09-10T12:15:13+02:00
# Last modified: 2018-04-16T22:05:29+0200
"""Retrieve the numbered tracks from a dvd."""

import logging
import sys
from subprocess import run, call, DEVNULL

__version__ = '1.1.0'


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
        rc = call(args, stdout=DEVNULL, stderr=DEVNULL)
        if rc != rv:
            raise OSError
        logging.info('found required program "{}"'.format(args[0]))
    except OSError as oops:
        outs = 'required program "{}" not found: {}.'
        logging.error(outs.format(args[0], oops.strerror))
        sys.exit(1)


def main(argv):
    """
    Entry point for get-tracks.py.

    Arguments:
        argv: command line arguments
    """
    logging.basicConfig(
        level=logging.INFO, format='%(levelname)s: %(message)s')
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
            print('"{}" is not an integer, skipping'.format(a))


def retrieve(dvddev, num):
    """Use `tccat` to retrieve a track from DVD.

    Without the -P argument some DVD's aren't retrieved correctly.

    Arguments:
        dvddev: String containing the device node for the DVD.
        num: The integer number of a track to retrieve.
    """
    args = ['tccat', '-i', dvddev, '-T', '{},-1'.format(num), '-P']
    trackname = 'track{:02d}.mpg'.format(num)
    logging.info(
        'writing track {} as "{}"... '.format(num, trackname))
    with open(trackname, 'wb') as outf:
        run(args, stdout=outf, stderr=DEVNULL)
    logging.info('done.')


if __name__ == '__main__':
    main(sys.argv[1:])

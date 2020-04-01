#!/usr/bin/env python3
# file: denylog.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2015-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-09-03T08:47:30+02:00
# Last modified: 2020-03-31T23:43:48+0200
"""
Summarize the deny log messages from ipfw.

Use the given file names, or /var/log/security if no filenames are given.
This program can handle compressed files like /var/log/security.?.bz2.
"""

import argparse
import bz2
import logging
import re
import sys

__version__ = '0.5'


def main():
    """
    Entry point for denylog.py.
    """
    args = setup()
    if not args.files:
        args.files = ['/var/log/security']
    reps = '  IP: {:16s} port: {:10s} rule: {}'
    serv = services()
    for f in args.files:
        print('File:', f)
        try:
            matches = parselogfile(f)
        except FileNotFoundError as e:
            print(e)
            continue
        if not matches:
            print('  Nothing to report.')
            continue
        for rule, IP, port in matches:
            print(reps.format(IP + ',', serv[int(port)] + ',', rule))


def setup():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument(
        '--log',
        default='warning',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'warning')"
    )
    parser.add_argument("files", metavar='file', nargs='*', help="one or more files to process")
    args =  parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None), format='%(levelname)s: %(message)s'
    )
    return args


def services(filename='/etc/services'):
    """
    Generate a dictionary of the available services from /etc/services.

    Arguments:
        filename: Name of the services file.

    Returns:
        A dict in the form of {25: 'smtp', 80: 'http', ...}
    """
    with open(filename) as serv:
        data = serv.read()
    matches = re.findall('\n' + r'(\S+)\s+(\d+)/', data)
    return {int(num): name for name, num in set(matches)}


def parselogfile(filename):
    """
    Extract deny rules for incoming packets from file and parse them.

    Arguments:
        filename: Name of the file to read.

    Returns:
        A tuple of (rule, source IP, port) tuples
    """
    if filename.endswith('.bz2'):
        df = bz2.open(filename, 'rt')
    else:
        df = open(filename)
    data = df.read()
    df.close()
    patt = r'ipfw: (\d+) Deny (?:\S+) ' \
           r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+).*in'
    return tuple(set(re.findall(patt, data)))


if __name__ == '__main__':
    main()

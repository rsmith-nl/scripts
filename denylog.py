#!/usr/bin/env python3
# file: denylog.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-09-03 03:04:01 +0200
# Last modified: 2017-06-04 13:16:16 +0200
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to denylog.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

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

__version__ = '0.4.1'


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
    matches = re.findall('\n(\S+)\s+(\d+)/', data)
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
    patt = 'ipfw: (\d+) Deny (?:\S+) ' \
           '(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+).*in'
    return tuple(set(re.findall(patt, data)))


def main(argv):
    """
    Entry point for denylog.py.

    Arguments:
        argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__)
    parser.add_argument('--log', default='warning',
                        choices=['debug', 'info', 'warning', 'error'],
                        help="logging level (defaults to 'warning')")
    parser.add_argument("files", metavar='file', nargs='*',
                        help="one or more files to process")
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                        format='%(levelname)s: %(message)s')
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
            print(reps.format(IP+',', serv[int(port)]+',', rule))


if __name__ == '__main__':
    main(sys.argv[1:])

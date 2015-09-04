# file: denylog.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-09-03 03:04:01 +0200
# Last modified: 2015-09-05 00:46:50 +0200

"""Summarize the deny log messages from ipfw in /var/log/security"""

import argparse
import bz2
import logging
import re
import sys

__version__ = '0.3.0'


def parselogfile(filename):
    """Extract deny rules from file and parse them

    Arguments:
        filename: Name of the file to read.

    Returns:
        A tuple of (rule, IP, port) tuples
    """
    if filename.endswith('.bz2'):
        df = bz2.open(filename, 'rt')
    else:
        df = open(filename)
    data = df.read()
    df.close()
    patt = 'ipfw: (\d+) Deny (?:TCP|UDP) ' \
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
    reps = '  IP: {:16s} port: {:6s} rule: {}'
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
            print(reps.format(IP+',', port+',', rule))


if __name__ == '__main__':
    main(sys.argv[1:])

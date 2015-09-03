# file: denylog.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-09-03 03:04:01 +0200
# Last modified: 2015-09-03 08:47:08 +0200

"""Summarize the deny log messages from ipfw in /var/log/security"""

import argparse
import logging
import sys
import re

__version__ = '0.0.1'


def parselogfile(filename):
    """Extract deny rules from file and parse them

    Arguments:
        filename: Name of the file to read.

    Returns:
        @todo
    """
    with open(filename) as df:
        data = df.read()
    patt = 'ipfw: (\d+) Deny (?:TCP|UDP) ' \
           '(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)'
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
    # The real program starts here...
    if not args.files:
        args.files = ['/var/log/security']
    for f in args.files:
        print('File:', f)
        matches = parselogfile(f)
        for rule, IP, port in matches:
            print('  IP: {}, port: {}, rule: {}'.format(IP, port, rule))


if __name__ == '__main__':
    main(sys.argv[1:])

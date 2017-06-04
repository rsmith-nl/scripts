#!/usr/bin/env python3
# vim:fileencoding=utf-8
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-02-10 21:43:11 +0100
# Last modified: 2017-06-04 13:48:45 +0200
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to old.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/
"""
Renames a directory by prefixing the name with 'old-'.

If the directory name starts with a period, it removes the period and prefixes
it with 'old-dot'.
"""

from datetime import datetime
import logging
import os
import sys

__version__ = '1.1.0'


def main(argv):
    """
    Entry point for old.

    Arguments:
        argv: command line arguments.
    """
    if len(argv) < 2:
        binary = os.path.basename(argv[0])
        print("{} ver. {}".format(binary, __version__), file=sys.stderr)
        print("Usage: {} directory ...".format(binary), file=sys.stderr)
        sys.exit(1)
    logging.basicConfig(format='%(levelname)s: %(message)s')
    for dirname in argv[1:]:
        if not os.path.isdir(dirname):
            dn = "'{}' is not a directory. Skipping."
            logging.warning(dn.format(dirname))
            continue
        if dirname.endswith(os.sep):
            dirname = dirname[:-1]
        dt = datetime.now().strftime('-%Y%m%dT%H%M')
        if dirname.startswith('.'):
            newname = ''.join(['old-dot', dirname[1:], dt])
        else:
            newname = ''.join(['old-', dirname, dt])
        if os.path.exists(newname):
            ren = "'{}' already exists. Skipping rename of '{}'."
            logging.warning(ren.format(newname, dirname))
            continue
        os.rename(dirname, newname)


if __name__ == '__main__':
    main(sys.argv)

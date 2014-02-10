#!/usr/bin/env python
# vim:fileencoding=utf-8
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-02-10 21:43:11 +0100
# Modified: $Date$
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to old.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Renames a directory by prefixing the name with 'old-'."""

from __future__ import print_function, division  # 2 and 3 compatibility.

import sys
import os

__version__ = '$Revision$'[11:-2]


def main(argv):
    """Entry point for this script.

    :param argv: command line arguments.
    """
    if len(argv) is not 2:
        binary = os.path.basename(argv[0])
        print("{} ver. {}".format(binary, __version__), file=sys.stderr)
        print("Usage: {} directory".format(binary), file=sys.stderr)
        sys.exit(1)
    dirname = argv[1]
    if not os.path.isdir(dirname):
        print("'{}' is not a directory. Exiting.".format(dirname))
        sys.exit(2)
    if dirname.startswith('.'):
        newname = ''.join(['old-dot', dirname[1:]])
    else:
        newname = ''.join(['old-', dirname])
    if os.path.exists(newname):
        print("'{}' already exists. Exiting.".format(newname))
        sys.exit(3)
    os.rename(dirname, newname)


if __name__ == '__main__':
    main(sys.argv)

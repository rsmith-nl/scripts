#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to nospaces.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Rename files mentioned on the command line, removing spaces from
their names and replacing them with underscores."""

__version__ = '$Revision$'[11:-2]

import os
import sys


def fixname(path):
    """Replaces spaces in a path by underscores.

    :param path: the path to change
    :returns: the updated path
    """
    path = os.path.normpath(path)
    head, tail = os.path.split(path)
    tl = tail.split()
    tail = '_'.join(tl)
    return os.path.join(head, tail)


def main(argv):
    """Main program.

    :param argv: command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print("{} version {}".format(binary, __version__), file=sys.stderr)
        print("Usage: {} [file ...]".format(binary), file=sys.stderr)
        sys.exit(0)
    del argv[0]  # delete the name of the script.
    for n in argv:
        try:
            os.rename(n, fixname(n))
        except OSError as e:
            print('Renaming "{}" failed: {}'.format(n, e.strerror))


if __name__ == '__main__':
    main(sys.argv)

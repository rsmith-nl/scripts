#!/usr/bin/env python3
# file: nospaces.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2012-2017 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2012-12-21T16:21:37+01:00
# Last modified: 2018-07-07T13:44:35+0200
"""Change whitespace in file names to underscores."""

import os
import sys

__version__ = '1.0.1'


def main(argv):
    """
    Entry point for nospaces.

    Arguments:
        argv: All command line arguments.
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print(f"{binary} version {__version__}", file=sys.stderr)
        print(f"Usage: {binary} [file ...]", file=sys.stderr)
        sys.exit(0)
    del argv[0]  # delete the name of the script.
    for n in argv:
        try:
            os.rename(n, fixname(n))
        except OSError as e:
            print(f'Renaming "{n}" failed: {e.strerror}')


def fixname(path):
    """
    Replace whitespace in a path by underscores.

    Arguments:
        path: The path to change.

    Returns:
        The updated path.
    """
    path = os.path.normpath(path)
    head, tail = os.path.split(path)
    tl = tail.split()
    tail = '_'.join(tl)
    return os.path.join(head, tail)


if __name__ == '__main__':
    main(sys.argv)

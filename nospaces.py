#!/usr/bin/env python3
# file: nospaces.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2012-2017 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2012-12-21T16:21:37+01:00
# Last modified: 2020-04-01T20:15:03+0200
"""Change whitespace in file names to underscores."""

import os
import sys

__version__ = '1.0.1'


def main():
    """
    Entry point for nospaces.
    """
    files = setup()
    for n in files:
        try:
            os.rename(n, fixname(n))
        except OSError as e:
            print(f'Renaming "{n}" failed: {e.strerror}')


def setup():
    """Process command-line."""
    if len(sys.argv) == 1:
        binary = os.path.basename(sys.argv[0])
        print(f"{binary} version {__version__}", file=sys.stderr)
        print(f"Usage: {binary} [file ...]", file=sys.stderr)
        sys.exit(0)
    return sys.argv[1:]


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
    main()

#!/usr/bin/env python3
# file: git-origdate.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2015-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-01-03T16:31:09+01:00
# Last modified: 2019-07-27T13:36:13+0200
"""Report when arguments were checked into git."""

import os.path
import subprocess as sp
import sys

__version__ = '1.0.1'


def main(argv):
    """
    Entry point for git-origdate.

    Arguments:
        argv: Command line arguments.
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print(f"{binary} ver. {__version__}", file=sys.stderr)
        print(f"Usage: {binary} [file ...]", file=sys.stderr)
        sys.exit(0)
    del argv[0]  # delete the name of the script.
    try:
        for fn in argv:
            args = ['git', 'log', '--diff-filter=A', '--format=%ai', '--', fn]
            date = sp.check_output(args, stderr=sp.PIPE)
            date = date.decode('utf-8').strip()
            print(f'{fn}: {date}')
    except sp.CalledProcessError as e:
        if e.returncode == 128:
            print("Not a git repository! Exiting.")
        else:
            print(f"git error: '{e.strerror}'. Exiting.")


if __name__ == '__main__':
    main(sys.argv)

#!/usr/bin/env python
# file: git-origdate.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2015-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-01-03T16:31:09+01:00
# Last modified: 2020-12-16T00:25:34+0100
"""Report when arguments were checked into git."""

import os.path
import subprocess as sp
import sys

__version__ = "2020.12.16"

if len(sys.argv) == 1:
    binary = os.path.basename(sys.argv[0])
    print(f"{binary} ver. {__version__}", file=sys.stderr)
    print(f"Usage: {binary} [file ...]", file=sys.stderr)
    sys.exit(0)

try:
    for fn in sys.argv[1:]:
        args = [
            "git",
            "--no-pager",
            "log",
            "--diff-filter=A",
            "--format=%ai",
            "--",
            fn,
        ]
        cp = sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL, text=True, check=True)
        # Sometimes this git command will return *multiple dates*!
        # In that case, select the oldest.
        date = cp.stdout.strip().splitlines()[-1]
        print(f'"{fn}": {date}')
except sp.CalledProcessError as e:
    if e.returncode == 128:
        print("Not a git repository! Exiting.")
    else:
        print(f"git error: '{e.strerror}'. Exiting.")

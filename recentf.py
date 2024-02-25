#!/usr/bin/env python
# file: recentf.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2021 R.F. Smith <rsmith@xs4all.nl>
# Created: 2021-09-05T14:00:45+0200
# Last modified: 2024-02-25T18:31:24+0100
"""For each given directory, recursively find the COUNT most recent modified files."""


import argparse
import logging
import os
import sys
from datetime import datetime

__version__ = "2024.02.25"


def main():
    """
    Entry point for .py.
    """
    args = setup()
    # Real work starts here.
    recentf = []
    for d in args.dirs:
        if not os.path.isdir(d):
            logging.info(f"“{d}” is not a directory; skipping it.")
            continue
        recentf += processdir(d)
    recentf.sort(key=lambda x: -x[1])
    for r in recentf[: args.count]:
        dt = datetime.fromtimestamp(r[1])
        dt = dt.replace(microsecond=0)
        print(dt.isoformat(), r[0])


def setup():
    """Program initialization"""
    # Process command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    defcount = 25
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=defcount,
        help=f"number of most resent files (default = {defcount})",
    )
    parser.add_argument(
        "dirs", metavar="dirs", nargs="*", help="one or more directories to process"
    )
    args = parser.parse_args(sys.argv[1:])
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    return args


def processdir(path):
    targetfiles = []
    logging.debug(f"gathering file info for “{path}”.")
    for dirpath, dirnames, filenames in os.walk(path):
        if len(dirpath) > 1 and "." in dirpath[1:]:
            logging.debug(f"“{dirpath}” is hidden; skipping it.")
            continue
        targetfiles += [
            (fullpath := os.path.join(dirpath, name), os.stat(fullpath).st_mtime)
            for name in filenames
        ]
    return targetfiles


if __name__ == "__main__":
    main()

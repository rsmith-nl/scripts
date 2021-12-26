#!/usr/bin/env python
# file: fixfn.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2021 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2021-12-26T09:19:01+0100
# Last modified: 2021-12-26T10:31:34+0100
"""Fix filenames by removing whitespace and ID numbers from filenames and
making them lower case."""

import argparse
import logging
import os
import re
import shutil
import sys

__version__ = "2021.12.26"


def main():
    """
    Entry point for .py.
    """
    args = setup()
    # Real work starts here.
    for path in args.files:
        # Split off the path
        origpath, fn = os.path.basename(path)
        # Remove IDs.
        newfn = re.sub(r"-\[.*?\]", "", fn)
        newfn = re.sub(r"-\d+", "", newfn)
        if newfn != fn:
            logging.info(f"removed ID from “{fn}”")
        # Replace whitespace
        newfn, n = re.subn("\s", args.replacement, newfn)
        logging.info(f"replaced {n} instances of whitespace in “{fn}”")
        # Make lowercase
        newfn = newfn.lower()
        # Rename the file.
        newpath = os.path.join(origpath, newfn)
        try:
            shutil.move(path, newpath)
            logging.info(f"moved “{path}” to “newpath”")
        except PermissionError as e:
            logging.error(e)


def setup():
    """Program initialization"""
    # Process command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--version", action="version", version=__version__)
    repdefault = "_"
    parser.add_argument(
        "-r",
        "--replacement",
        default=repdefault,
        help=f"character to replace whitespace with (defaults to “{repdefault}”)",
    )
    logdefault = "warning"
    parser.add_argument(
        "--log",
        default=logdefault,
        choices=["debug", "info", "warning", "error"],
        help=f"logging level (defaults to “{logdefault}”)",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        dest="dryrun",
        action="store_true",
        help="perform a trial run with no changes made",
    )
    parser.add_argument(
        "files", metavar="file", nargs="*", help="one or more files to process"
    )
    args = parser.parse_args(sys.argv[1:])
    # Configure logging
    if args.dryrun:
        logging.basicConfig(level="INFO", format="%(levelname)s: %(message)s")
        logging.info("performing dry run")
    else:
        logging.basicConfig(
            level=getattr(logging, args.log.upper(), None),
            format="%(levelname)s: %(message)s",
        )
    return args


if __name__ == "__main__":
    main()

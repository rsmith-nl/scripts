#!/usr/bin/env python
# file: fixfn.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2021 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2021-12-26T09:19:01+0100
# Last modified: 2021-12-26T13:00:53+0100
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
        origpath, fn = os.path.split(path)
        # Remove IDs at the end of the filename.
        newfn = re.sub(r"-\[?[0-9a-zA-Z_-]{6,11}\]?\.", ".", fn)
        if newfn != fn:
            logging.info(f"removed ID from “{fn}”")
        # Replace dashes
        dashes = r"\s+[\u002D\u058A\u05BE\u1806\u2010\u2011\u2012\u2013\u2014\u2015\u2E3A]+\s+"
        newfn, n = re.subn(dashes, "-", newfn)
        logging.info(f"replaced {n} instances of dashes with whitespace in “{fn}”")
        # Replace whitespace
        newfn, m = re.subn("\s+", args.replacement, newfn)
        logging.info(f"replaced {m} instances of whitespace in “{fn}”")
        # Make lowercase
        if not args.nolower:
            newfn = newfn.lower()
        else:
            logging.info(f"not converting “{newfn}” to lower case")
        # Rename the file.
        newpath = os.path.join(origpath, newfn)
        if newpath == path:
            logging.info("path “{path}” not modified")
            continue
        if args.dryrun:
            logging.info(f"“{path}” would be moved to “{newpath}”")
            continue
        try:
            shutil.move(path, newpath)
            logging.info(f"moved “{path}” to “{newpath}”")
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
        "-d",
        "--dry-run",
        dest="dryrun",
        action="store_true",
        help="perform a trial run with no changes made",
    )
    parser.add_argument(
        "-n",
        "--no-lower",
        dest="nolower",
        action="store_true",
        help="do not convert to lower case",
    )

    parser.add_argument(
        "files", metavar="file", nargs="*", help="one or more files to process"
    )
    args = parser.parse_args(sys.argv[1:])
    # Configure logging
    if args.dryrun:
        if args.log.upper() != "DEBUG":
            args.log = "info"
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    if args.dryrun:
        logging.info("performing dry run")
    logging.debug(f"command line arguments = {sys.argv}")
    logging.debug(f"parsed arguments = {args}")
    return args


if __name__ == "__main__":
    main()

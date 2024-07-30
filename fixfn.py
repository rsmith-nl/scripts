#!/usr/bin/env python
# file: fixfn.py
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2021 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2021-12-26T09:19:01+0100
# Last modified: 2024-07-30T22:03:34+0200
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
    for path in args.files:
        # We only want to modify the filename itself.
        origpath, fn = os.path.split(path)
        # Remove IDs from e.g. youtube at the end of the filename.
        newfn = re.sub(r"-\[?[0-9a-zA-Z_-]{6,11}\]?\.", ".", fn)
        if newfn != fn:
            logging.info(f"removed ID from “{fn}”")
        # Remove all dash-like Unicode characters surrounded by whitespace.
        # See https://jkorpela.fi/dashes.html
        dashes = (
            r"\s+[\-\u058A\u05BE\u1806\u2010-\u2015\u2053\u207B\u208B\u2212"
            r"\u2E3A\u2E3B\uFE58\uFE63\uFF0D]+\s+"
        )
        newfn, n = re.subn(dashes, "-", newfn)
        logging.info(f"replaced {n} instances of dashes in “{fn}”")
        newfn, m = re.subn("\s+", args.replacement, newfn)
        logging.info(f"replaced {m} instances of whitespace in “{fn}”")
        # Remove “waves” (_-_).
        newfn, p = re.subn("_-_", args.replacement, newfn)
        logging.info(f"replaced {p} instances of waves in “{fn}”")
        if not args.nolower:
            newfn = newfn.lower()
        else:
            logging.info(f"not converting “{newfn}” to lower case")
        newpath = os.path.join(origpath, newfn)
        if newpath == path:
            logging.info(f"path “{path}” not modified")
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

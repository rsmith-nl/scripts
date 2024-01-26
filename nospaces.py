#!/usr/bin/env python
# file: nospaces.py
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2024 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2024-01-20T10:59:10+0100
# Last modified: 2024-01-26T21:09:50+0100
"""Replaces spaces in filenames with underscores.

It processes the file names given on the command line.
If the given name is a directory, it processes all the names in that
directory, but not in subdirectories.
"""

import argparse
import logging
import os
import re
import sys

__version__ = "2024.01.26"


def main():
    """
    Entry point for .py.
    """
    options = setup()
    for path in options.files:
        if os.path.isfile(path):
            if not options.dryrun:
                rename(path, options.replace)
            else:
                newpath = new_path(path, options.replace)
                if newpath:
                    print(f"“{path}” would be renamed to “{newpath}”")
        elif os.path.isdir(path):
            logging.info(f"“{path}” is a directory")
            for de in os.scandir(path):
                if not de.is_file():
                    logging.info(f"skipping “{de.name}”, it is not a file")
                    continue
                if de.name.startswith("."):
                    logging.info(f"skipping hidden file “{de.name}”")
                    continue
                if not options.dryrun:
                    rename(de.path, options.replace)
                else:
                    newpath = new_path(de.path, options.replace)
                    if newpath:
                        print(f"“{de.path}” would be renamed to “{newpath}”")


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
    parser.add_argument(
        "-d", "--dryrun", action="store_true",
        help="do not rename, but show what would be renamed"
    )
    parser.add_argument(
        "-r", "--replace", type=ord, default="_",
        help="code point to use for replacing whitespace (defaults to '_')"
    )
    parser.add_argument(
        "files", metavar="file", nargs="*",
        help="one or more files or directories to process"
    )
    args = parser.parse_args(sys.argv[1:])
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.debug(f"replacement: ‘{args.replace}’")
    args.replace = chr(args.replace)
    logging.debug(f"args = {args}")
    if args.replace.isspace():
        logging.warning("replacing whitespace with whitespace doesn't make sense; exiting")
        sys.exit(0)
    return args


def new_path(path, rep="_"):
    """Return new name for path."""
    head, tail = os.path.split(path)
    newpath = os.path.join(head, re.sub("[-_]?\s+[-_]?|[-_]+", rep, tail))
    if newpath == path:
        return None
    return newpath


def rename(path, rep="_"):
    """Change the name of the file at the end of path, replacing whitespace
    with the contents of rep."""
    head, tail = os.path.split(path)
    newpath = new_path(path, rep)
    if not newpath:
        logging.info(f"{path} unchanged")
        return
    try:
        os.replace(path, newpath)
    except OSError as e:
        logging.error(f"renaming “{path}” to “{newpath}” failed: {e}")
    else:
        logging.info(f"“{path}” has been renamed to “{newpath}”")


if __name__ == "__main__":
    main()

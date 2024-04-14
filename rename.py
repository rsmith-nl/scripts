#!/usr/bin/env python
# file: rename.py
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2015-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-09-06T11:45:52+0200
# Last modified: 2021-12-31T14:56:39+0100
"""
Utility to rename files.

It renames the files given on the command line in the sequence that they are
given to <prefix><number>, keeping the extension of the original file.
"""

import argparse
import logging
import os
import re
import sys

__version__ = "2021.12.31"


def main():
    """
    Entry point for rename.py.
    """
    args = setup()
    if args.numbers:
        logging.info("sort files by number")
        args.files = sorted_by_number(args.files)
    pairs = newnames(args.files, args.prefix, args.start, args.width)
    if not args.dryrun:
        rename(pairs)
    else:
        logging.basicConfig(
            level=logging.INFO, format="%(levelname)s: %(message)s", force=True
        )
        logging.info("dry run")
        report(pairs)


def setup():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-p",
        "--prefix",
        default="picture-",
        help='prefix for the image name (default "picture-")',
    )
    parser.add_argument(
        "-s", "--start", type=int, default=1, help="first number to use (default 1)"
    )
    parser.add_argument(
        "-w", "--width", type=int, default=2, help="field width for number (default 2)"
    )
    parser.add_argument(
        "-n",
        "--numbers",
        action="store_true",
        help="sort filenames by the last number that is part of the name",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        dest="dryrun",
        action="store_true",
        help="do not actually rename, but report how files would be renamed",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    parser.add_argument(
        "files", metavar="file", nargs="*", help="one or more files to process"
    )
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    return args


def rename(pairs):
    for old, new in pairs:
        try:
            os.rename(old, new)
        except OSError as e:
            print(f'Could not rename "{old}" to "{new}": {e}')


def report(pairs):
    for old, new in pairs:
        logging.info(f"“{old}” would be renamed to “{new}”")


def sorted_by_number(paths):
    """Sort paths by the last number occurring in the filename."""
    combined = [(re.findall("\d+", p), p) for p in paths]
    cleaned = sorted([(int(nl[-1]), p) for nl, p in combined if nl], key=lambda x: x[0])
    return [p for n, p in cleaned]


def newnames(paths, prefix, start, precision):
    """
    Generate new filenames, keeping the path and extension.

    Arguments:
        path: Iterable of path names
        prefix: New filename prefix to use
        start: Initial number to use after the prefix.
        precision: How to format the number.

    Returns:
        List of (path, newpath) tuples
    """
    if not prefix:
        raise ValueError("empty prefix")
    number = int(start)
    if number < 0:
        raise ValueError("negative numbers not allowed")
    precision = int(precision)
    if precision < 0:
        raise ValueError("precision must be positive")
    if isinstance(paths, str):
        paths = [paths]
    req_prec = len(str(len(paths)))
    if req_prec > precision:
        logging.warning(f"precision changed from {precision} to {req_prec}")
        precision = req_prec
    rv = []
    for path in paths:
        head, tail = os.path.split(path)
        logging.debug(f"head = {head}")
        logging.debug(f"tail = {tail}")
        if not tail:
            number += 1
            continue
        if head and not head.endswith(os.path.sep):
            head = head + os.path.sep
        _, ext = os.path.splitext(tail)
        t = "".join([prefix, r"{:0", str(precision), r"d}", ext])
        newpath = "".join([head, t.format(number)])
        logging.debug(f"newpath = {newpath}")
        number += 1
        rv.append((path, newpath))
    return rv


if __name__ == "__main__":
    main()

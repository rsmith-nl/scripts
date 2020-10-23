#!/usr/bin/env python3
# file: missing-libs.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2016-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2016-01-17T15:48:11+01:00
# Last modified: 2020-04-01T18:08:48+0200
"""Check executables in the given directory for missing shared libraries."""

import argparse
import concurrent.futures as cf
import logging
import sys
import os
import subprocess as sp
from enum import Enum

__version__ = "2020.04.01"


class Ftype(Enum):
    """Enum for limited file type information."""

    script = 1
    executable = 2
    other = 3
    unaccessible = 4


def main():
    """
    Entry point for missing-libs.py.
    """
    args = setup()
    programs = (
        e.path
        for d in args.dirs
        for e in os.scandir(d)
        if get_type(e.path) == Ftype.executable
    )
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        for path, missing in tp.map(check_missing_libs, programs):
            for lib in missing:
                print(path, lib)


def setup():
    """Process the command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    parser.add_argument("dirs", nargs="*", help="one or more directory to process")
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.debug(f"Command line arguments = {sys.argv}")
    logging.debug(f"Parsed arguments = {args}")
    return args


def get_type(path):
    """
    Determine the Ftype of a file.

    Returns:
        The Ftype for the given path.
    """
    try:
        with open(path, "rb") as p:
            data = p.read(2)
    except OSError:
        logging.warning(f"cannot access {path}")
        return Ftype.unaccessible
    if data == b"#!":
        return Ftype.script
    elif data == b"\x7f\x45":
        return Ftype.executable
    else:
        return Ftype.other


def check_missing_libs(path):
    """
    Check if a program has missing libraries, using ldd.

    Arguments:
        path: String containing the path of a file to query.

    Returns:
        A tuple of the path and a list of missing libraries.
    """
    logging.info(f"checking {path}")
    p = sp.run(["ldd", path], stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True)
    if "not a dynamic executable" in p.stderr:
        logging.info(f'"path" is not a dynamic executable')
        rv = []
    else:
        rv = [
            ln for ln in p.stdout.splitlines() if "missing" in ln or "not found" in ln
        ]
    return (path, rv)


if __name__ == "__main__":
    main()

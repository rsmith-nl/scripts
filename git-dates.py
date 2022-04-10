#!/usr/bin/env python
# file: git-dates.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2012 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2012-10-28T14:07:21+01:00
# Last modified: 2022-04-10T14:12:48+0200
"""
Get the short hash and most recent commit date for files under the current
working directory.
"""

from concurrent.futures import ThreadPoolExecutor
import argparse
import logging
import os
import subprocess as sp
import sys

__version__ = "2022.04.10"


def main():
    """Entry point for git-dates."""
    setup()
    # List of all files
    allfiles = []
    # Get a list of excluded files.
    if ".git" not in os.listdir("."):
        logging.error("This directory is not managed by git.")
        sys.exit(0)
    exargs = ["git", "ls-files", "-i", "-o", "--exclude-standard"]
    exc = sp.run(
        exargs, universal_newlines=True, stdout=sp.PIPE, stderr=sp.DEVNULL
    ).stdout.split()
    for root, dirs, files in os.walk("."):
        for d in [".git", "__pycache__"]:
            try:
                dirs.remove(d)
                logging.info(f"skipping {d}")
            except ValueError:
                pass
        tmp = [os.path.join(root, f) for f in files if f not in exc]
        allfiles += tmp
    # Gather the files' data using a ThreadPoolExecutor.
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        res = tp.map(filecheck, allfiles)
    filedata = [r for r in res if r is not None]
    # Sort the data (latest modified last) and print it
    filedata.sort(key=lambda a: a[2])
    maxlen = max(len(n) for n, _, _ in filedata)
    sep = " | "
    for name, tag, date in filedata:
        print(f"{name:{maxlen}s}{sep}{tag}{sep}{date}")


def setup():
    """Parse command-line arguments. Check for required programs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.debug(f"Command line arguments = {sys.argv}")
    logging.debug(f"Parsed arguments = {args}")
    # Check for required programs.
    try:
        sp.run(["git"], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        logging.debug("found “git”")
    except FileNotFoundError:
        logging.error("the required program “git” cannot be found")
        sys.exit(1)
    return args


def filecheck(fname):
    """
    Start a git process to get file info.

    Return a string containing the filename, the abbreviated commit hash and the
    author date in ISO 8601 format.

    Arguments:
        fname: Name of the file to check.

    Returns:
        A 3-tuple containing the file name, latest short hash and latest
        commit date.
    """
    args = ["git", "--no-pager", "log", "-1", "--format=%h|%aI", fname]
    try:
        b = sp.run(
            args, stdout=sp.PIPE, stderr=sp.DEVNULL, text=True, check=True
        ).stdout
        if len(b) == 0:
            return None
        data = b[:-1]
        h, t = data.split("|")
        out = (fname[2:], h, t)
    except (sp.CalledProcessError, ValueError) as e:
        logging.error(f"git log failed for {fname}: {e}")
        return None
    return out


if __name__ == "__main__":
    main()

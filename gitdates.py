#!/usr/bin/env python
# file: gitdates.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2012-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2012-10-28T14:07:21+01:00
# Last modified: 2020-01-13T19:08:56+0100
"""Get the short hash and most recent commit date for files."""

from concurrent.futures import ThreadPoolExecutor
import logging
import os
import subprocess as sp
import sys
import time


def main():
    """Entry point for gitdates."""
    logging.basicConfig(level="WARNING", format="%(levelname)s: %(message)s")
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
            except ValueError:
                pass
        tmp = [os.path.join(root, f) for f in files if f not in exc]
        allfiles += tmp
    # Gather the files' data using a ThreadPoolExecutor.
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        res = tp.map(filecheck, allfiles)
    filedata = [r for r in res if r is not None]
    # Sort the data (latest modified first) and print it
    filedata.sort(key=lambda a: a[2], reverse=True)
    dfmt = "%Y-%m-%d %H:%M:%S %Z"
    for name, tag, date in filedata:
        ds = time.strftime(dfmt, date)
        print(f"{name}|{tag}|{ds}")


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
    args = ["git", "--no-pager", "log", "-1", "--format=%h|%at", fname]
    try:
        b = sp.run(
            args, stdout=sp.PIPE, stderr=sp.DEVNULL, universal_newlines=True, check=True
        ).stdout
        if len(b) == 0:
            return None
        data = b[:-1]
        h, t = data.split("|")
        out = (fname[2:], h, time.gmtime(float(t)))
    except (sp.CalledProcessError, ValueError):
        logging.error('git log failed for "{}"'.format(fname))
        return None
    return out


if __name__ == "__main__":
    main()

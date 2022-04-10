#!/usr/bin/env python
# file: git-origdate.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2015-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-01-03T16:31:09+01:00
# Last modified: 2022-04-10T12:56:09+0200
"""Report when files named on the command line were checked into git."""

import argparse
import logging
import os
import subprocess as sp
import sys

__version__ = "2022.04.10"


def main():
    args = setup()
    origdir = os.getcwd()
    for path in args.files:
        dirname, filename = os.path.split(path)
        args = [
            "git",
            "--no-pager",
            "log",
            "--diff-filter=A",
            "--format=%ai",
            "--",
            filename,
        ]
        if dirname:
            logging.info(f"changing to directory {dirname}")
            os.chdir(dirname)
        cp = sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL, text=True)
        logging.debug(f"file {path}, returncode = {cp.returncode}")
        os.chdir(origdir)
        if cp.returncode == 128:
            logging.warning(f"“{path}” not in a git repository; skipping")
            continue
        elif cp.returncode != 0:
            logging.warning(f"git returned {cp.returncode}; skipping “{path}”")
            continue
        dates = cp.stdout.strip().splitlines()
        if len(dates) > 1:
            logging.debug(f"multiple dates returned for {path}:")
            for d in dates:
                logging.debug(f"{d}")
        # Sometimes this git command will return *multiple dates*!
        # In that case, select the oldest.
        print(f'{path}: {dates[-1]}')


def setup():
    """Parse command-line arguments. Check for required programs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'info')",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "files", nargs="*", help="one or more files to process"
    )
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
        logging.error("the program “git” cannot be found")
        sys.exit(1)
    return args


if __name__ == "__main__":
    main()

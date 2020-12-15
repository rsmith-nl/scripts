#!/usr/bin/env python
# file: lk.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2016-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2016-10-09T11:59:41+02:00
# Last modified: 2020-04-01T18:27:54+0200
"""
Lock down files or directories.

This makes files read-only for the owner and inaccessible for the group and
others. Then it sets the user immutable and user undeletable flag on the files.
For directories, it recursively treats the files as mentioned above. It then
sets the sets the directories to read/execute only for the owner and
inaccessible for the group and others. Then it sets the user immutable and
undeletable flag on the directories as well.

Using the -u flag unlocks the files or directories, making them writable for
the owner only.
"""

import argparse
import logging
import os
import sys
import stat

__version__ = "2020.04.01"


def main():
    """
    Entry point for lk.py.
    """
    args = setup()
    fmod = stat.S_IRUSR
    dmod = stat.S_IRUSR | stat.S_IXUSR
    if args.unlock:
        logging.info("unlocking files")
        fmod = stat.S_IRUSR | stat.S_IWUSR
        dmod = stat.S_IRWXU
        action = unlock_path
    else:
        action = lock_path
        logging.info("locking files")
    for p in args.paths:
        if os.path.isfile(p):
            action("", p, fmod)
        elif os.path.isdir(p):
            if args.unlock:
                action("", p, dmod)
            for root, dirs, files in os.walk(p, topdown=False):
                for fn in files:
                    action(root, fn, fmod)
                for d in dirs:
                    action(root, d, dmod)
            if not args.unlock:
                action("", p, dmod)


def setup():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-u",
        "--unlock",
        action="store_true",
        help="unlock the files instead of locking them",
    )
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "paths", nargs="*", metavar="path", help="files or directories to work on"
    )
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.debug(f"Command line arguments = {sys.argv}")
    logging.debug(f"Parsed arguments = {args}")
    if not args.paths:
        parser.print_help()
        sys.exit(0)
    return args


def lock_path(root, name, mode):
    """Lock down a path"""
    addflags = stat.UF_IMMUTABLE | stat.UF_NOUNLINK
    p = os.path.join(root, name)
    pst = os.stat(p)
    if pst.st_flags & stat.UF_IMMUTABLE:
        # Temporarily remove user immutable flag, so we can chmod.
        os.chflags(p, pst.st_flags ^ stat.UF_IMMUTABLE)
    logging.info(f"locking path “{p}”")
    os.chmod(p, mode)
    os.chflags(p, pst.st_flags | addflags)


def unlock_path(root, name, mode):
    rmflags = stat.UF_IMMUTABLE | stat.UF_NOUNLINK
    p = os.path.join(root, name)
    pst = os.stat(p)
    logging.info(f"unlocking path “{p}”")
    os.chflags(p, pst.st_flags & ~rmflags)
    os.chmod(p, mode)


if __name__ == "__main__":
    main()

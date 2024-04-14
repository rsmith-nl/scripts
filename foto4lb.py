#!/usr/bin/env python
# file: foto4lb.py
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2011-2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2011-11-07T21:40:58+01:00
# Last modified: 2024-01-05T23:25:38+0100
"""Shrink fotos to a size suitable for use in my logbook."""

from datetime import datetime
import argparse
import concurrent.futures as cf
import logging
import os
import subprocess as sp
import sys

# For performance measurments
# import time

from PIL import Image
from PIL.ExifTags import TAGS

__version__ = "2024.01.05"
outdir = "foto4lb"
extensions = (".jpg", ".jpeg", ".raw")


def main():
    """
    Entry point for foto4lb.
    """
    args = setup()
    pairs = []
    count = 0
    for path in args.path:
        if os.path.exists(path + os.sep + outdir):
            logging.warning(
                f'"{outdir}" already exists in "{path}", skipping this path.'
            )
            continue
        files = [
            f.name
            for f in os.scandir(path)
            if f.is_file() and f.name.lower().endswith(extensions)
        ]
        count += len(files)
        pairs.append((path, files))
        logging.debug(f'Path: "{path}"')
        logging.debug(f"Files: {files}")
    if len(pairs) == 0:
        logging.info("nothing to do.")
        return
    logging.info(f"found {count} files.")
    logging.info("creating output directories.")
    for dirname, _ in pairs:
        os.mkdir(dirname + os.sep + outdir)
    infodict = {
        0: "file '{}' processed.",
        1: "file '{}' is not an image, skipped.",
        2: "error running convert on '{}'.",
    }
    # For performance measurements.
    # start = time.monotonic()
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        agen = ((p, fn, args.width) for p, flist in pairs for fn in flist)
        for fn, rv in tp.map(processfile, agen):
            logging.info(infodict[rv].format(fn))
    # For performance measurements.
    # dt = time.monotonic() - start
    # logging.info(f'startup preparations took {dt:.2f} s')


def setup():
    """Process the command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-w",
        "--width",
        default=1920,
        type=int,
        help="width of the images in pixels (default 1920)",
    )
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("path", nargs="*", help="directory in which to work")
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.debug(f"Command line arguments = {sys.argv}")
    logging.debug(f"Parsed arguments = {args}")
    if not args.path:
        parser.print_help()
        sys.exit(0)
    # Check for required programs.
    try:
        sp.run(["convert"], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        logging.debug("found “convert”")
    except FileNotFoundError:
        logging.error("the program “convert” cannot be found")
        sys.exit(1)
    return args


def processfile(packed):
    """
    Read an image file and write a smaller version.

    Arguments:
        packed: A 3-tuple of (path, filename, output width)

    Returns:
        A 2-tuple (input file name, status).
        Status 0 indicates a succesful conversion,
        status 1 means that the input file was not a recognized image format,
        status 2 means a subprocess error.
    """
    # For performance measurements.
    # start = time.monotonic()
    path, name, newwidth = packed
    fname = os.sep.join([path, name])
    oname = os.sep.join([path, outdir, name.lower()])
    try:
        img = Image.open(fname)
        ld = {}
        for tag, value in img._getexif().items():
            decoded = TAGS.get(tag, tag)
            ld[decoded] = value
        want = set(["DateTime", "DateTimeOriginal", "CreateDate", "DateTimeDigitized"])
        available = sorted(list(want.intersection(set(ld.keys()))))
        fields = ld[available[0]].replace(" ", ":").split(":")
        dt = datetime(*map(int, fields))
    except Exception:
        logging.warning("exception raised when reading the file time.")
        dt = datetime.today()
    args = [
        "convert",
        fname,
        "-strip",
        "-resize",
        str(newwidth),
        "-units",
        "PixelsPerInch",
        "-density",
        "300",
        "-unsharp",
        "2x0.5+0.7+0",
        "-quality",
        "80",
        oname,
    ]
    rp = sp.run(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    if rp.returncode != 0:
        return (name, 2)
    modtime = dt.timestamp()
    os.utime(oname, (modtime, modtime))
    # For performance measurements.
    # dt = time.monotonic() - start
    # logging.info(f'processfile took {dt:.2f} s')
    return (fname, 0)


if __name__ == "__main__":
    main()

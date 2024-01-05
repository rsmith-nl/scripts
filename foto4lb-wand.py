#!/usr/bin/env python
# file: foto4lb-wand.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2011-2021 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2011-11-07T21:40:58+01:00
# Last modified: 2024-01-05T23:25:09+0100
"""Shrink fotos to a size suitable for use in my logbook."""

from datetime import datetime
from os import utime
from time import mktime
import argparse
import concurrent.futures as cf
import logging
import os
import sys

from wand.exceptions import MissingDelegateError
from wand.image import Image

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
    with cf.ProcessPoolExecutor(max_workers=os.cpu_count()) as tp:
        agen = ((p, fn, args.width) for p, flist in pairs for fn in flist)
        for fn, rv in tp.map(processfile, agen):
            logging.info(infodict[rv].format(fn))


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
    path, name, newwidth = packed
    fname = os.sep.join([path, name])
    oname = os.sep.join([path, outdir, name.lower()])
    try:
        with Image(filename=fname) as img:
            w, h = img.size
            scale = newwidth / w
            exif = {k[5:]: v for k, v in img.metadata.items() if k.startswith("exif:")}
            img.units = "pixelsperinch"
            img.resolution = (300, 300)
            img.resize(width=newwidth, height=round(scale * h))
            img.strip()
            img.compression_quality = 80
            img.unsharp_mask(radius=2, sigma=0.5, amount=0.7, threshold=0)
            img.save(filename=oname)
        want = set(["DateTime", "DateTimeOriginal", "DateTimeDigitized"])
        try:
            available = list(want.intersection(set(exif.keys())))
            available.sort()
            fields = exif[available[0]].replace(" ", ":").split(":")
            dt = datetime(
                int(fields[0]),
                int(fields[1]),
                int(fields[2]),
                int(fields[3]),
                int(fields[4]),
                int(fields[5]),
            )
        except Exception:
            dt = datetime.today()
        modtime = mktime(
            (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, 0, 0, -1)
        )
        utime(oname, (modtime, modtime))
        return fname, 0
    except MissingDelegateError:
        return fname, 1


if __name__ == "__main__":
    main()

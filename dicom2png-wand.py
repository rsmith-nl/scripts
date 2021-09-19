#!/usr/bin/env python
# file: dicom2png.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2012-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2012-04-11T19:21:19+02:00
# Last modified: 2021-09-19T11:35:11+0200
"""
Convert DICOM files from an X-ray machine to PNG format.

During the conversion process, blank areas are removed. The blank area removal
is based on the image size of a Philips flat detector. The image goes from
2048x2048 pixels to 1574x2048 pixels.
"""

from datetime import datetime
from functools import partial
import argparse
import concurrent.futures as cf
import logging
import os
import sys

from wand.image import Image


__version__ = "2021.09.19"


def main():
    """
    Entry point for dicom2png.

    Arguments:
        argv: command line arguments
    """
    args = setup()
    if not args.fn:
        logging.error("no files to process")
        sys.exit(1)
    if args.quality != 80:
        logging.info(f"quality set to {args.quality}")
    if args.level:
        logging.info("applying level correction.")
    convert_partial = partial(convert, quality=args.quality, level=args.level)
    starttime = str(datetime.now())[:-7]
    logging.info(f"started at {starttime}.")
    with cf.ProcessPoolExecutor(max_workers=os.cpu_count()) as tp:
        for infn, outfn, errmsg in tp.map(convert_partial, args.fn):
            if errmsg:
                logging.error(f"error during conversion of {infn}: {errmsg}")
            else:
                logging.info(f"finished conversion of {infn} to {outfn}")
    endtime = str(datetime.now())[:-7]
    logging.info(f"completed at {endtime}.")


def setup():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "-l",
        "--level",
        action="store_true",
        default=False,
        help="Correct color levels (default: no)",
    )
    parser.add_argument(
        "-q", "--quality", type=int, default=80, help="PNG quailty level (default: 80)"
    )
    parser.add_argument(
        "fn", nargs="*", metavar="filename", help="DICOM files to process"
    )
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.debug(f"command line arguments = {sys.argv}")
    logging.debug(f"parsed arguments = {args}")
    return args


def convert(filename, quality, level):
    """
    Convert a DICOM file to a PNG file.

    Removing the blank areas from the Philips detector.

    Arguments:
        filename: name of the file to convert.
        quality: PNG quality to apply
        level: Boolean to indicate whether level adustment should be done.
    Returns:
        Tuple of (input filename, output filename, error message or None)
    """
    outname = filename.strip() + ".png"
    with Image(filename=filename) as img:
        if img.format != "DCM":
            return (filename, outname, "not a DICOM file")
        img.units = "pixelsperinch"
        img.resolution = (300, 300)
        img.depth = 8
        img.crop(232, 0, width=1574, height=2048)
        img.page = (1574, 2048, 0, 0)
        img.compression_quality = int(quality)
        if level:
            img.level(-0.35, 0.70, 0.5)
        img.save(filename=outname)
    return (filename, outname, None)


if __name__ == "__main__":
    main()

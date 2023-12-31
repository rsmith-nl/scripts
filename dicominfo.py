# file: dicominfo.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2023 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2023-12-31T16:54:04+0100
# Last modified: 2023-12-31T22:18:52+0100
"""
Show information about DICOM files.

Use “https://dicom.innolitics.com/ciods” to find out what the attributes mean.
"""

import pydicom
import argparse
import logging
import os
import sys

__version__ = "2023.12.31"


def main():
    """Entry point for dicominfo.py"""
    args = setup()
    if not args.fn:
        logging.error("no files to process")
        sys.exit(1)
    for path in args.fn:
        report(path)


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


def report(path):
    """Print the properties of a DICOM file."""
    abspath = os.path.abspath(path)
    logging.debug(f"reading DICOM file {abspath}")
    try:
        dataset = pydicom.dcmread(abspath)
        print("------------------------------------------------------------")
        print(f"file: “{abspath}”")
        for ln in dataset.formatted_lines():
            print(ln)
        if 'PixelData' in dataset:
            print(f"Image shape: {dataset.Columns}×{dataset.Rows} pixels (W×H)")
            print(f"Image bits/pixel: {dataset.BitsAllocated}")
            print(f"Image size: {dataset.pixel_array.nbytes} bytes")
        else:
            logging.warning(f"“{path}” has no image data.")
        print("------------------------------------------------------------")
    except pydicom.errors.InvalidDicomError:
        logging.error(f"“{path}” is not a valid DICOM file.")


if __name__ == "__main__":
    main()

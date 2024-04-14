#!/usr/bin/env python
# file: dicom2jpg.py
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2012-2021 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2012-04-11T19:21:19+02:00
# Last modified: 2024-02-24T15:41:38+0100
"""
Convert DICOM files from an X-ray machine to JPG format.

"""

from datetime import datetime
import argparse
import concurrent.futures as cf
import logging
import os
import sys
import pydicom
from PIL import Image
import numpy as np


__version__ = "2024.02.24"


def main():
    """
    Entry point for dicom2png.
    """
    args = setup()
    if not args.fn:
        logging.error("no files to process")
        sys.exit(1)
    starttime = str(datetime.now())[:-7]
    logging.info(f"started at {starttime}.")
    with cf.ProcessPoolExecutor(max_workers=os.cpu_count()) as tp:
        for infn, outfn, rv in tp.map(convert, args.fn):
            logging.info(f"finished conversion of {infn} to {outfn} (returned {rv})")
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


def convert(filename):
    """
    Convert a DICOM file to a JPG file.

    Arguments:
        filename: name of the file to convert.
    Returns:
        Tuple of (input filename, output filename, error string)
    """
    try:
        dataset = pydicom.dcmread(filename)
        if 'PixelData' not in dataset:
            return filename, "", "no pixel data"
    except pydicom.errors.InvalidDicomError:
        return filename, "", "not a valid dicom file"
    if 'WindowWidth' in dataset and 'WindowCenter' in dataset:
        ww, wc = int(dataset.WindowWidth), int(dataset.WindowCenter)
        data = dataset.pixel_array
        # From github.com/pydicom/contrib-pydicom/blob/master/viewers/pydicom_PIL.py
        image = np.piecewise(
            data,
            [data <= (wc - 0.5 - (ww - 1) / 2), data > (wc - 0.5 + (ww - 1) / 2)],
            [0, 255, lambda data: ((data - (wc - 0.5)) / (ww - 1) + 0.5) * (255 - 0)]
        )
        img = Image.fromarray(image).convert('L')
        outname = filename.strip() + ".jpg"
        img.save(outname)
        del img, dataset
        return (filename, outname, "OK")
    return (filename, "", "data without LUT")


if __name__ == "__main__":
    main()

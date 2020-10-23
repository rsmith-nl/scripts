#!/usr/bin/env python3
# file: vid2mp4.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2013-2017 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2013-11-16T18:41:21+01:00
# Last modified: 2020-04-01T21:03:12+0200
"""Convert video files to H.264/AAC streams in an MP4 container."""

from functools import partial
import argparse
import concurrent.futures as cf
import logging
import os
import subprocess as sp
import sys

__version__ = "2020.04.01"


def main():
    """
    Entry point for vid2mp4.
    """
    args = setup()
    starter = partial(runencoder, crf=args.crf, preset=args.preset)
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        fl = [tp.submit(starter, t) for t in args.files]
        for fut in cf.as_completed(fl):
            fn, rv = fut.result()
            if rv == 0:
                logging.info(f'finished "{fn}"')
            elif rv < 0:
                logging.warning(f'file "{fn}" has unknown extension, ignoring it.')
            else:
                logging.error(f"conversion of {fn} failed, return code {rv}")


def setup():
    parser = argparse.ArgumentParser(description=__doc__)
    crfh = "constant rate factor (lower is better, default 29)"
    parser.add_argument("-c", "--crf", type=int, default=29, help=crfh)
    parser.add_argument(
        "-p",
        "--preset",
        default="medium",
        choices=[
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
        ],
        help="preset (default medium) slower is smaller file",
    )
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "files", metavar="file", nargs="+", help="one or more files to process"
    )
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.debug(f"command line arguments = {sys.argv}")
    logging.debug(f"parsed arguments = {args}")
    # Check for required programs.
    try:
        sp.run(["ffmpeg"], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        logging.debug("found “ffmpeg”")
    except FileNotFoundError:
        logging.error("the “ffmpeg” program cannot be found")
        sys.exit(1)
    return args


def runencoder(fname, crf, preset):
    """
    Convert a video file to H.264/AAC streams in an MP4 container.

    Arguments:
        fname: Name of the file to convert.
        crf: Constant rate factor. See ffmpeg docs.
        preset: Encoding preset. See ffmpeg docs.

    Returns:
        (fname, return value)
    """
    basename, ext = os.path.splitext(fname)
    known = [
        ".mp4",
        ".avi",
        ".wmv",
        ".flv",
        ".mpg",
        ".mpeg",
        ".mov",
        ".ogv",
        ".mkv",
        ".webm",
        ".gif",
    ]
    if ext.lower() not in known:
        return fname, -1
    ofn = basename + ".mp4"
    args = [
        "ffmpeg",
        "-i",
        fname,
        "-c:v",
        "libx264",
        "-crf",
        str(crf),
        "-preset",
        preset,
        "-flags",
        "+aic+mv4",
        "-c:a",
        "aac",
        "-sn",
        "-y",
        ofn,
    ]
    logging.debug(" ".join(args))
    logging.info(f'starting conversion of "{fname}".')
    cp = sp.run(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    return fname, cp.returncode


if __name__ == "__main__":
    main()

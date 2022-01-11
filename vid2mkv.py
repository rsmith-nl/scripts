#!/usr/bin/env python
# file: vid2mkv.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2013-2017 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2013-11-16T18:41:21+01:00
# Last modified: 2022-01-11T21:05:11+0100
"""Convert video files to Theora/Vorbis streams in a Matroska container."""

from functools import partial
import argparse
import concurrent.futures as cf
import logging
import os
import subprocess as sp
import sys

__version__ = "2022.01.11"


def main():
    """
    Entry point for vid2mkv.
    """
    args = setup()
    starter = partial(runencoder, vq=args.videoquality, aq=args.audioquality)
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        fl = [tp.submit(starter, t) for t in args.files]
        for fut in cf.as_completed(fl):
            fn, rv = fut.result()
            if rv == 0:
                logging.info(f'finished "{fn}"')
            elif rv < 0:
                logging.warning(f'file "{fn}" has unknown extension, ignoring it.')
            else:
                logging.error(f'conversion of "{fn}" failed, return code {rv}')


def setup():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-q",
        "--videoquality",
        type=int,
        default=6,
        help="video quality (0-10, default 6)",
    )
    parser.add_argument(
        "-a",
        "--audioquality",
        type=int,
        default=3,
        help="audio quality (0-10, default 3)",
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
    logging.debug(f"command line arguments = {args}")
    logging.debug(f"parsed arguments = {args}")
    # Check for required programs.
    try:
        sp.run(["ffmpeg"], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        logging.debug("found “ffmpeg”")
    except FileNotFoundError:
        logging.error("the “ffmpeg” program cannot be found")
        sys.exit(1)
    return args


def runencoder(fname, vq, aq):
    """
    Convert a video file to Theora/Vorbis streams in a Matroska container.

    Arguments:
        fname: Name of the file to convert.
        vq : Video quality. See ffmpeg docs.
        aq: Audio quality. See ffmpeg docs.

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
        return (fname, -1)
    if ext.lower() == ".mkv":
        ofn = basename + "_mod.mkv"
    else:
        ofn = basename + ".mkv"
    args = [
        "ffmpeg",
        "-i",
        fname,
        "-c:v",
        "libtheora",
        "-q:v",
        str(vq),
        "-c:a",
        "libvorbis",
        "-q:a",
        str(aq),
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

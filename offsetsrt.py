#!/usr/bin/env python
# file: offsetsrt.py
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2016-2017 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2016-02-14T14:54:32+01:00
# Last modified: 2020-04-01T20:29:02+0200
"""
Manipulate the times in an SRT file.

Reads an SRT file and applies the given offset to all time values. Then prints
the modified data to stdout.
"""

import argparse
import logging
import sys

__version__ = "2020.04.01"


def main():
    """
    Entry point for offsetsrt.py.
    """
    args = setup()
    offs = int(1000 * args.offset)
    srtdata = parsesrt(args.filename)
    infs = "loaded {} records from {}"
    logging.info(infs.format(len(srtdata), args.filename))
    for n, ((start, end), lines) in enumerate(srtdata, start=1):
        print(n)
        print(ms2str(start + offs), "-->", ms2str(end + offs))
        for ln in lines:
            print(ln)
        print()


def setup():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    parser.add_argument("filename", type=str, help="file to process")
    parser.add_argument("offset", type=float, help="offset in seconds")
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    return args


def str2ms(s):
    """
    Convert the time strings from an SRT file to milliseconds.

    Arguments:
        s: A time value in the format HH:MM:SS,mmm where H, M, S and m are
           digits.

    Returns:
        The time string converted to an integer value in milliseconds.
    """
    s = s.strip()
    time, ms = s.split(",")
    h, m, s = time.split(":")
    return int(ms) + 1000 * (int(s) + 60 * (int(m) + 60 * int(h)))


def ms2str(v):
    """
    Convert a time in milliseconds to a time string.

    Arguments:
        v: a time in milliseconds.

    Returns:
        A string in the format HH:MM:SS,mmm.
    """
    v, ms = divmod(v, 1000)
    v, s = divmod(v, 60)
    h, m = divmod(v, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def split_time(s):
    """
    Parse a time-line string.

    These strings have the format
    HH:MM:SS,mmm --> HH:MM:SS,mmm

    Arguments:
        s: a time-line string.

    Returns:
        a tuple (start, end) times in milliseconds
    """
    start, sym, end = s.split()
    if sym != "-->":
        logging.debug(f'line "{s}"')
        raise ValueError("not a valid time-line")
    return (str2ms(start), str2ms(end))


def parsesrt(path):
    """
    Read an SRT file and splits it up into a list of data.

    Arguments:
        path: path of an SRT file.

    Returns:
        A list of tuples ((start-time, end-time), lines).
    """
    with open(path, encoding="utf-8") as srt:
        lines = srt.readlines()
    lines = [ln.strip() for ln in lines]
    emptyidx = [n for n, ln in enumerate(lines) if not ln]
    timeidx = [n + 2 for n in emptyidx]
    timeidx.insert(0, 1)
    srtdata = [
        (split_time(lines[t]), lines[t + 1 : e]) for t, e in zip(timeidx, emptyidx)
    ]
    return srtdata


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# file: csvcolumn.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2016-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2016-03-19T13:03:26+01:00
# Last modified: 2020-03-31T23:30:54+0200
"""Prints a single column from a CSV file."""

import csv
import sys
import argparse

__version__ = "2020.03.31"


def main():
    """Entry point for csvcolumn.py."""
    args = setup()
    for path in args.path:
        print("file:", path)
        results = getdata(path, args.column, args.delimiter)
        if args.rows:
            rg = range(args.rows[0], args.rows[1] + 1)
            results = [(n, d) for n, d in results if n in rg]
        for n, d in results:
            print("row {:2d}: '{}'".format(n, d))


def setup():
    """Process command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "-r",
        "--rows",
        nargs=2,
        type=int,
        metavar=("min", "max"),
        help="only show rows min--max",
    )
    parser.add_argument(
        "-d", "--delimiter", default=";", help="delimiter to use (defaults to ';')"
    )
    parser.add_argument(
        "column", type=int, help="number of the column to print (starts at 0)"
    )
    parser.add_argument("path", type=str, nargs="*", help="path of the file to process")
    return parser.parse_args(sys.argv[1:])


def getdata(fn, colnum, delim=";"):
    """
    Read a column of data from a CSV file.

    Arguments:
        fn: Path of the file to read.
        colnum: Index of the column to read.
        delim: Delimiter to use (defaults to ';').

    Returs:
        A list of extracted data.
    """
    data = []
    with open(fn) as df:
        for num, row in enumerate(csv.reader(df, delimiter=delim)):
            if len(row) > colnum:
                data.append((num, row[colnum]))
    return data


if __name__ == "__main__":
    main()

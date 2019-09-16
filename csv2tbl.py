#!/usr/bin/env python3
# file: csv2tbl.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2012-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2012-06-17T19:25:53+02:00
# Last modified: 2019-09-16T21:54:30+0200
"""Convert a CSV file to a LaTeX table."""

from collections import Counter
from datetime import date
import os.path
import sys

__version__ = '1.1'


def main(argv):
    """
    Entry point for csv2tbl.

    Arguments:
        argv: Command line arguments.
    """
    binary = os.path.basename(argv[0])
    if len(argv) < 2:
        print(f"{binary} ver. {__version__}")
        print(f"Usage: {binary} file", file=sys.stderr)
        sys.exit(0)
    # Read the data into a list of lines.
    lines = readlines(argv[1])
    # Check which seperator is used.
    sep = csvsep(lines)
    # Get the filename and remove the extension.
    fname = os.path.basename(argv[1])
    if fname.endswith(('.csv', '.CSV')):
        fname = fname[:-4]
    # Create a format definition for the tabular environment.
    columns = len(lines[1].split(sep))
    columns = 'l' * columns
    # Print the output.
    print('% Generated from ' + str(argv[1]))
    print('% by csv2tbl.py on ' + str(date.today()))
    print(r'\begin{table}[!htbp]')
    print(r'  \centering')
    print(r'  \caption{\label{tb:' + fname + r'}' + fname + r'}')
    print(r'  \begin{tabular}{' + columns + r'}')
    print(r'    \toprule')
    fmtcsv(lines[0], sep)
    print(r'    \midrule')
    for l in lines[1:]:
        fmtcsv(l, sep)
    print(r'    \bottomrule')
    print(r'  \end{tabular}')
    print(r'\end{table}')


def readlines(filename):
    """
    Read a file and return the contents as a list of lines.

    Arguments:
        filename name of the file to read

    Returns:
        A list of stripped lines.
    """
    with open(filename) as infile:
        lines = infile.readlines()
    return [l.strip() for l in lines]


def csvsep(lines, separators=',\t;:'):
    """
    Determine the separator used in the lines of csv data.

    Arguments:
        lines: CSV data as a list of strings.
        separator: String of separators.

    Returns:
        The most occuring separator character.
    """
    letters, sep = Counter(), Counter()
    for ln in lines:
        letters.update(ln)
    for s in ',\t;:':
        sep[s] = letters[s]
    return sep.most_common()[0][0]


def fmtcsv(line, sep):
    """
    Format a single line of CSV data as a LaTeX table cells.

    Arguments:
        line: The string of CSV data to convert
        sep: The separator to use.
    """
    # Skip empty lines.
    if len(line) == line.count(sep):
        return
    if line.endswith(sep):
        line = line[:-len(sep)]
    # Escape existing ampersands.
    line = line.replace(r'&', r'\&')
    outs = '    ' + line.replace(sep, r' & ') + r'\\'
    print(outs)


if __name__ == '__main__':
    main(sys.argv)

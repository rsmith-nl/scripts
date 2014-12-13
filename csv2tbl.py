#!/usr/bin/env python2
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to csv2tbl.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Convert a CSV file to a LaTeX table"""

from __future__ import print_function

__version__ = '$Revision$'[11:-2]

from datetime import date
import os.path
import sys


def readlines(filename):
    """Read a file and return the contents as a list of lines.

    :param filename: name of the file to read
    """
    with open(filename) as infile:
        lines = infile.readlines()
    lines = [l.strip() for l in lines]
    return lines


def csvsep(lines, separators=',\t;:'):
    """Determine and return the separator used in the lines of csv data.

    :param lines: csv data
    :param separator: string of separators
    """
    mx = 0
    sep = ''
    for c in separators:
        n = lines[1].count(c)
        if n > mx:
            mx = n
            sep = c
    return sep


def fmtcsv(line, sep):
    """Format a single line of CSV data as a LaTeX table cells.

    Keyword arguments:
    line -- the string of CSV data to convert
    sep  -- the separator to use
    """
    # Skip empty lines.
    if len(line) == line.count(sep):
        return
    items = line.split(sep)
    outs = '    '
    for it in items:
        outs += it + r' & '
    outs = outs[:-3]
    outs += r'\\'
    outs = outs.replace(r' & \\', r'\\')
    print(outs)


def main(argv):
    """Main program.

    Keyword arguments:
    argv -- command line arguments
    """
    binary = os.path.basename(argv[0])
    if len(argv) < 2:
        print("{} ver. {}".format(binary, __version__))
        print("Usage: {} file".format(binary), file=sys.stderr)
        sys.exit(0)
    # Read the data into a list of lines.
    lines = readlines(argv[1])
    # Check which seperator is used.
    sep = csvsep(lines)
    # Get the filename and remove the extension.
    fname = os.path.basename(argv[1])
    shortname = fname[:]
    if fname.endswith(('.csv', '.CSV')):
        fname = fname[:-4]
    # Create a format definition for the tabular environment.
    columns = len(lines[1].split(sep))
    columns = 'l'*columns
    # Print the output.
    print('% Generated from ' + str(shortname))
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


if __name__ == '__main__':
    main(sys.argv)

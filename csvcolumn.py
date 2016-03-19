# file: csvcolumn.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-03-19 12:42:04 +0100
# Last modified: 2016-03-19 13:00:02 +0100
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to csvcolumn.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Prints a single column from a CSV file."""

import csv
import sys
import argparse

__version__ = '0.1.0'


def getdata(fn, colnum, delim=';'):
    data = []
    with open(fn) as df:
        for num, row in enumerate(csv.reader(df, delimiter=delim)):
            if len(row) > colnum:
                data.append((num, row[colnum]))
    return data


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-v', '--version', action='version',
                    version=__version__)
parser.add_argument('-d', '--delimiter', default=';',
                    help="delimiter to use (defaults to ';')")
parser.add_argument('column', type=int,
                    help='number of the column to print (starts at 0)')
parser.add_argument('path', type=str,
                    help='path of the file to process')
args = parser.parse_args(sys.argv[1:])
results = getdata(args.path, args.column, args.delimiter)
for n, d in results:
    print("row {:2d}: '{}'".format(n, d))

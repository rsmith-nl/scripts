#!/usr/bin/env python
# file: histdata.py
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2012-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2012-07-23T01:18:29+02:00
# Last modified: 2019-07-27T13:50:29+0200
"""Make a histogram and calculate entropy of files."""

import math
import os.path
import subprocess as sp
import sys


def main(argv):
    """
    Entry point for histdata.

    Arguments:
        argv: List of file names.
    """
    if len(argv) < 1:
        sys.exit(1)
    for fn in argv:
        hdata, size = readdata(fn)
        e = entropy(hdata, size)
        print(f"entropy of {fn} is {e:.4f} bits/byte")
        histogram_gnuplot(hdata, size, fn)


def readdata(name):
    """
    Read the data from a file and count it.

    Arguments:
        name: String containing the filename to open.

    Returns:
        A tuple (counts list, length of data).
    """
    f = open(name, "rb")
    data = f.read()
    f.close()
    ba = bytearray(data)
    del data
    counts = [0] * 256
    for b in ba:
        counts[b] += 1
    return (counts, float(len(ba)))


def entropy(counts, sz):
    """
    Calculate the entropy of the data represented by the counts list.

    Arguments:
        counts: List of counts.
        sz: Length of the data in bytes.

    Returns:
        Entropy value.
    """
    ent = 0.0
    for b in counts:
        if b == 0:
            continue
        p = float(b) / sz
        ent -= p * math.log(p, 256)
    return ent * 8


def histogram_gnuplot(counts, sz, name):
    """
    Use gnuplot to create a histogram from the data in the form of a PDF file.

    Arguments
        counts: List of counts.
        sz: Length of the data in bytes.
        name: Name of the output file.
    """
    counts = [100 * c / sz for c in counts]
    rnd = 1.0 / 256 * 100
    pl = ["set terminal pdfcairo size 18 cm,10 cm"]

    pl += ["set style line 1 lc rgb '#E41A1C' pt 1 ps 1 lt 1 lw 4"]
    pl += ["set style line 2 lc rgb '#377EB8' pt 6 ps 1 lt 1 lw 4"]
    pl += ["set style line 3 lc rgb '#4DAF4A' pt 2 ps 1 lt 1 lw 4"]
    pl += ["set style line 4 lc rgb '#984EA3' pt 3 ps 1 lt 1 lw 4"]
    pl += ["set style line 5 lc rgb '#FF7F00' pt 4 ps 1 lt 1 lw 4"]
    pl += ["set style line 6 lc rgb '#FFFF33' pt 5 ps 1 lt 1 lw 4"]
    pl += ["set style line 7 lc rgb '#A65628' pt 7 ps 1 lt 1 lw 4"]
    pl += ["set style line 8 lc rgb '#F781BF' pt 8 ps 1 lt 1 lw 4"]
    pl += ["set palette maxcolors 8"]
    pl += [
        "set palette defined ( 0 '#E41A1C', 1 '#377EB8', 2 '#4DAF4A',"
        " 3 '#984EA3',4 '#FF7F00', 5 '#FFFF33', 6 '#A65628', 7 '#F781BF' )"
    ]
    pl += ["set style line 11 lc rgb '#808080' lt 1 lw 5"]
    pl += ["set border 3 back ls 11"]
    pl += ["set tics nomirror"]
    pl += ["set style line 12 lc rgb '#808080' lt 0 lw 2"]
    pl += ["set grid back ls 12"]
    nm = os.path.basename(name)
    pl += [f"set output 'hist-{nm}.pdf'"]
    pl += ["set xrange[-1:256]"]
    pl += ["set yrange[0:*]"]
    pl += ["set key right top"]
    pl += ['set xlabel "byte value"']
    pl += ['set ylabel "occurance [%]"']
    pl += [f"rnd(x) = {rnd:.6f}"]
    pl += [
        f"plot '-' using 1:2 with points ls 1 title '{name}', "
        f"rnd(x) with lines ls 2 title 'continuous uniform ({rnd:.6f}%)'"
    ]
    for n, v in enumerate(counts):
        pl += [f"{n} {v}"]
    pl += ["e"]
    pt = "\n".join(pl)
    sp.run(["gnuplot"], input=pt.encode("utf-8"), check=True)


if __name__ == "__main__":
    main(sys.argv[1:])

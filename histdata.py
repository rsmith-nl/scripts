#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
# file: histdata.py
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-07-12 01:38:08 +0200
# $Date$
# $Revision$

'''Make a histogram of the bytes in the input files, and calculate their
entropy.'''

import math
import os.path
import subprocess
import sys


def readdata(name):
    '''Read the data from a file and count it.'''
    f = open(name, 'rb')
    data = f.read()
    f.close()
    ba = bytearray(data)
    del data
    counts = [0]*256
    for b in ba:
        counts[b] += 1
    return (counts, float(len(ba)))


def entropy(counts, sz):
    '''Calculate the entropy of the data represented by the counts list'''
    ent = 0.0
    for b in counts:
        if b == 0:
            continue
        p = float(b)/sz
        ent -= p*math.log(p, 256)
    return ent*8


def histogram_gnuplot(counts, sz, name):
    '''Use gnuplot to create a histogram from the data'''
    counts = [100*c/sz for c in counts]
    rnd = 1.0/256*100
    pl = ['set terminal pdfcairo size 18 cm,10 cm']

    pl += ["set style line 1 lc rgb '#E41A1C' pt 1 ps 1 lt 1 lw 4"]
    pl += ["set style line 2 lc rgb '#377EB8' pt 6 ps 1 lt 1 lw 4"]
    pl += ["set style line 3 lc rgb '#4DAF4A' pt 2 ps 1 lt 1 lw 4"]
    pl += ["set style line 4 lc rgb '#984EA3' pt 3 ps 1 lt 1 lw 4"]
    pl += ["set style line 5 lc rgb '#FF7F00' pt 4 ps 1 lt 1 lw 4"]
    pl += ["set style line 6 lc rgb '#FFFF33' pt 5 ps 1 lt 1 lw 4"]
    pl += ["set style line 7 lc rgb '#A65628' pt 7 ps 1 lt 1 lw 4"]
    pl += ["set style line 8 lc rgb '#F781BF' pt 8 ps 1 lt 1 lw 4"]
    pl += ["set palette maxcolors 8"]
    pl += ["set palette defined ( 0 '#E41A1C', 1 '#377EB8', 2 '#4DAF4A',"
           " 3 '#984EA3',4 '#FF7F00', 5 '#FFFF33', 6 '#A65628', 7 '#F781BF' )"]
    pl += ["set style line 11 lc rgb '#808080' lt 1 lw 5"]
    pl += ["set border 3 back ls 11"]
    pl += ["set tics nomirror"]
    pl += ["set style line 12 lc rgb '#808080' lt 0 lw 2"]
    pl += ["set grid back ls 12"]
    pl += ["set output 'hist-{}.pdf'".format(os.path.basename(name))]
    pl += ['set xrange[-1:256]']
    pl += ['set yrange[0:*]']
    pl += ['set key right top']
    pl += ['set xlabel "byte value"']
    pl += ['set ylabel "occurance [%]"']
    pl += ['rnd(x) = {:.6f}'.format(rnd)]
    cont = "rnd(x) with lines ls 2 title 'continuous uniform ({:.6f}%)'"
    pl += ["plot '-' using 1:2 with points ls 1 title '{}', ".format(name) +
           cont.format(rnd)]
    for n, v in enumerate(counts):
        pl += ['{} {}'.format(n, v)]
    pl += ['e']
    pt = '\n'.join(pl)
    gp = subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE)
    gp.communicate(pt.encode('utf-8'))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(1)
    for fn in sys.argv[1:]:
        hdata, size = readdata(fn)
        e = entropy(hdata, size)
        print("entropy of {} is {:.4f} bits/byte".format(fn, e))
        histogram_gnuplot(hdata, size, fn)

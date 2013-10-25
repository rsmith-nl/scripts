#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Make a histogram of the bytes in the input files, and calculate their
entropy."""

import sys
import math
import matplotlib.pyplot as plt
import os


def readdata(name):
    """Read the data from a file and count how often each byte value
    occurs.

    :param name: name of the file to read
    """
    with open(name, 'rb') as f:
        ba = bytearray(os.path.getsize(name))
        f.readinto(ba)
    counts = [0]*256
    for b in ba:
        counts[b] += 1
    return (counts, len(ba))


def entropy(counts, sz):
    """Calculate the entropy of the data represented by the counts list.

    :param counts: number of occurance of each bite in a dataset
    :param sz: length of the dataset
    """
    ent = 0.0
    for b in counts:
        if b == 0:
            continue
        p = float(b)/sz
        ent -= p*math.log(p, 256)
    return ent*8


def histogram(counts, sz, name):
    """Use matplotlib to create a histogram from the data"""
    xdata = [n for n in xrange(0, 256)]
    counts = [100*c/sz for c in counts]
    top = math.ceil(max(counts)*10.0)/10.0
    rnd = [1.0/256*100]*256
    plt.figure(None, (7, 4), 100)
    plt.axis([0, 255, 0, top])
    plt.xlabel('byte value')
    plt.ylabel('occurance [%]')
    plt.plot(xdata, counts, label=name)
    plt.plot(xdata, rnd, label='continuous uniform')
    plt.legend(loc=(0.49, 0.15))
    plt.savefig('hist-' + name+'.png', bbox_inches='tight')
    plt.close()


def main(argv):
    """Main program.

    :param argv: command line arguments
    """
    if len(argv) < 1:
        print 'No arguments given. Quitting.'
        sys.exit(1)
    for fn in argv:
        hdata, size = readdata(fn)
        e = entropy(hdata, size)
        print "entropy of {} is {:.4f} bits/byte".format(fn, e)
        histogram(hdata, size, fn)


if __name__ == '__main__':
    main(sys.argv[1:])

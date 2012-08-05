#!/usr/bin/env python

"""Make a histogram of the bytes in the input files, and calculate their
entropy."""

import sys
import math
import subprocess
import matplotlib.pyplot as plt

def readdata(name):
    """Read the data from a file and count how often each byte value
    occurs."""
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
    """Calculate the entropy of the data represented by the counts list"""
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
    fig = plt.figure(None, (7, 4), 100)
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

    Keyword arguments:
    argv -- command line arguments
    """
    if len(argv) < 2:
        sys.exit(1)
    for fn in argv[1:]:
        hdata, size = readdata(fn)
        e = entropy(hdata, size)
        print "entropy of {} is {:.4f} bits/byte".format(fn, e)
        histogram(hdata, size, fn)

if __name__ == '__main__':
    def main(sys.argv)

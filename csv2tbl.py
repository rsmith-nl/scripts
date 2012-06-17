#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Time-stamp: <2012-06-17 19:27:28 rsmith>
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to csv2tbl.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

import sys
import os.path

def readlines(filename):
    '''Read a file and return the contents as a list of lines.'''
    infile = open(filename)
    lines = infile.readlines()
    infile.close()
    lines = [l.rstrip() for l in lines]
    return lines

def fmt(line, sep):
    '''Format a single line of CSV as a LaTeX table cells.'''
    items = line.split(sep)
    outs =  '    '
    for it in items:
        outs += it + r' & '
    outs = outs[:-3]
    outs += r'\\'
    outs = outs.replace(r' & \\', r'\\')
    print outs

if len(sys.argv) < 2:
    print "Usage: {} file".format(sys.argv[0])
    sys.exit(0)
# Read the data into a list of lines.
lines = readlines(sys.argv[1])
# Check which seperator is used.
mx = 0
sep = ''
for c in ';,\t':
    n = lines[0].count(c)
    if n > mx:
        mx = n
        sep = c
# Get the filename and remove the extension.
fname = os.path.basename(sys.argv[1])
if fname.endswith(('.csv', '.CSV')):
    fname = fname[:-4]
# Create a format definition for the tabular environment.
columns = len(lines[0].split(sep))
columns = 'l'*columns
# Print the output.
print r'\begin{table}[!htbp]'
print r'  \centering'
print r'  \caption{\label{tb:' + fname + r'}'+ fname +r'}'
print r'  \begin{tabular}{' + columns + r'}'
print r'    \toprule'
fmt(lines[0], sep)
print r'    \midrule'
for l in lines[1:]:
    fmt(l, sep)
print r'    \bottomrule'
print r'  \end{tabular}'
print r'\end{table}'


#!/usr/bin/env python
# file: ccx-dat-quantiles.py
# vim:fileencoding=utf-8:ft=python
#
# In CalculiX use “*EL PRINT” to save the stresses in integration points
# to a file. E.g:
#
#   *EL PRINT,ELSET=Eadh,FREQUENCY=1000
#   S
#
# This script reads the stresses in the integration points from a .dat file
# and quantizes them. It assumes that only one element set was saved this way.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: Unlicense
# Created: 2026-05-25T13:03:12+0200
# Last modified: 2026-05-25T14:14:44+0200

import statistics as stat

# Constants
S11, S22, S33, S12, S13, S23 = 2, 3, 4, 5, 6, 7

# Settings
INPUT = "job.dat"
INDEX = S13
OUTPUT = "quantiles.d"

stresses = []
with open(INPUT) as f:
    lines = f.readlines()
for n, ln in enumerate(lines):
    if 'stresses (elem' in ln:
        break
for ln in lines[n+2:]:
    # Contents of these lines: node, ip, s11, s22, s33, s12, s13, s23
    #                   index:  0    1    2    3    4    5    6    7
    items = ln.strip().split()
    stresses.append(float(items[INDEX]))
perc = stat.quantiles(stresses, n=100)
print(f'50th percentile: {perc[50]/1e6:.2f} MPa')
print(f'95th percentile: {perc[-5]/1e6:.2f} MPa')
print(f'99th percentile: {perc[-1]/1e6:.2f} MPa')
with open(OUTPUT, "w") as outf:
    for n, p in enumerate(perc, start=1):
        outf.write(f"{n} {p/1e6:.3f}\n")

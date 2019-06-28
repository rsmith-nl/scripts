#!/usr/bin/env python3
# file: texfilehash.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2019-06-28T16:13:39+0200
# Last modified: 2019-06-28T20:12:41+0200
"""
Create a file containing the abbreviated git commit hash for a TeX source file.
If the file has uncommitted changes, it appends the status in red text.

Usage: texfilehash.py <filename>.tex

Result: a file <filename>.hash
"""

import subprocess
import sys

infn = sys.argv[1]
if not infn.endswith('.tex'):
    sys.exit(1)  # Error

outfn = infn[:-4] + '.hash'

logcmd = ['git', '--no-pager', 'log', '-1', '--pretty=format:%h', sys.argv[1]]
logdata = subprocess.check_output(logcmd).decode('ascii')

statcmd = ['git', '--no-pager', 'status', '-s', '--', sys.argv[1]]
statdata = subprocess.check_output(statcmd)[:2].decode('ascii').strip()

if statdata:
    logdata = logdata + r'\,\textcolor{red}{' + statdata + r'}%'
else:
    logdata += '%'

with open(outfn, 'wt') as outf:
    outf.write(logdata)

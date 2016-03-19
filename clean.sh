#!/bin/sh
# Cleans up a directory, removing unnecessary files.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2016-03-19 10:44:07 +0100
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to clean. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/


# (La)TeX stuff
TEXF="*.dvi *.aux *.lof *.log *.toc"

# C(++) stuff
CF="*.o *.a *.so* *.la *.lo"

# Editor stuff
EDF="*~"

PY2F="*.pyc *.pyo"

# Python 3 stuff
PY3F=__pycache__/*

# Removing all unnecessary stuff.
rm -f $TEXF $CF $EDF $PY2F $PY3F

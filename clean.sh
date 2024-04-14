#!/bin/sh
# file: clean.sh
# vim:fileencoding=utf-8:ft=sh
# Cleans up a directory, removing unnecessary files.
#
# Copyright © 2015-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-05-08T22:12:45+02:00
# Last modified: 2018-04-16T21:24:49+0200

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

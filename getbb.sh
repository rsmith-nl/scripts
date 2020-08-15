#!/bin/sh
# file: getbb.sh
# vim:fileencoding=utf-8:fdm=marker:ft=sh
# Determine the bounding box for postscript files.
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2018-11-13T23:13:24+0100
# Last modified: 2020-08-15T14:25:41+0200

for f in $*; do
    echo -n "${f}: "
    gs -q -dNOPAUSE -dBATCH -sDEVICE=bbox "$f" 2>&1 | grep %%BoundingBox
done

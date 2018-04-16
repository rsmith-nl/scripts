#!/bin/sh
# file: tolower.sh
# vim:fileencoding=utf-8:fdm=marker:ft=sh
# Converts file names to lower case.
#
# Copyright © 2015-2016 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-05-08T22:12:45+02:00
# Last modified: 2018-04-16T22:40:43+0200

set -eu

if [ $# -eq 0 ]; then
    echo "Usage: tolower filenames"
fi

for f in $*; do
    n=$(echo $f|tr [:upper:] [:lower:])
    #echo "moving $f to $n"
    mv $f $n
done

#!/bin/sh
# file: setres.sh
# vim:fileencoding=utf-8:fdm=marker:ft=sh
#
# Copyright © 2006-2017 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2006-02-19T16:52:08+01:00
# Last modified: 2020-08-15T14:31:48+0200

# Check for arguments
if [ $# -lt 2 ]; then
    echo "Usage: $(basename $0) resolution filename [filenames]"
    exit 1
fi

# Check for special programs that are used in this script.
PROGS="mogrify"
for P in $PROGS; do
    which $P >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "$(basename $0): The program \"$P\" cannot be found."
        exit 1
    fi
done

RES=$1
shift

set -e
for f in "$@"; do
    mogrify -units PixelsPerInch -density $RES $f
done

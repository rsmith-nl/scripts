#!/bin/sh
# file: mkpdf.sh
# vim:fileencoding=utf-8:ft=sh
# Creates a PDF file from scanned images @ 150 DPI.
#
# Copyright © 2015-2016 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-05-14 19:25:57 +0200
# Last modified: 2021-02-28T20:46:58+0100

set -e

RES=150 # Scanner resolution
PAGE=a4 # Page size
ID=$(basename $0)

# Check for arguments
if [ $# -lt 2 ]; then
    echo "Usage: $ID outname file1 [file2 ...]"
    exit 1
fi
OUTF=$1
shift 1

# Check for special programs that are used in this script.
PROGS="convert"
for P in $PROGS; do
    which $P >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "$(basename $0): The program \"$P\" cannot be found."
        exit 1
    fi
done

echo -n "Gathering pages in PDF file..."
convert "$@" -adjoin -page $PAGE -density $RES -units PixelsPerInch $OUTF
echo "done."

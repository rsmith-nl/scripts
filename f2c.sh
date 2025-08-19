#!/bin/sh
# file: f2c.sh
# vim:fileencoding=utf-8:ft=sh
# Convert a file to an array for inclusion in a C program.
#
# Copyright © 2025 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2025-08-19T10:17:13+0200
# Last modified: 2025-08-19T11:46:40+0200

set -e

# Check for arguments
ID=$(basename $0)
if [ $# -lt 2 ]; then
    echo "Usage: $ID infile outfile.c"
    echo ""
    echo "Convert “infile” to an array of unsigned characters in “outfile.c”"
    echo "that can be included in to a program written in C."
    echo "The name of the array is derived from the name of the input file."
    echo ""
    exit 0
fi
INF=$1
OUTF=$2
shift 2

# Determine the size of the input in bytes.
SIZE=`cat $INF| wc -c|tr -d ' \n'`
# Name the asset
NAME=`echo $INF|tr '.,-' '_'`

# Create initial file
echo "// Contents of “$INF”:" >$OUTF
echo "unsigned char $NAME[$SIZE] = {" >>$OUTF
hexdump -v -e '"  " 16/1 "0x%02X," "\n"' $INF >>$OUTF
echo "};" >>$OUTF
# Remove trailing nonsense
sed -i '' -e 's/,0x .*$//' $OUTF

#!/bin/sh
# file: mkindexpic.sh
# vim:fileencoding=utf-8:ft=sh
# Make an index jpg of all pictures given as arguments.
#
# Copyright © 2015 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-05-08T22:12:45+02:00
# Last modified: 2021-02-28T20:46:39+0100

set -e

# Check for arguments
if [ -z "$1" ]; then
    echo "Usage: $0 filenames"
    echo "Creates the file \"index.jpg\""
    exit 0
fi

# Check for special programs that are used in this script.
PROGS="montage"
for P in $PROGS; do
    which $P >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "$(basename $0): The program \"$P\" cannot be found."
        exit 1
    fi
done

# Do the actual work
rm -f index.jpg
montage -tile 8 -label "%f\n%wx%h\n%[EXIF:DateTime]" "$@" index.jpg

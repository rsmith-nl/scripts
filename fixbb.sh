#!/bin/sh
# file: fixbb.sh
# vim:fileencoding=utf-8:fdm=marker:ft=sh
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-05-08T22:12:45+02:00
# Last modified: 2018-04-16T21:58:58+0200

# Check for arguments
if [ $# -eq 0 ]; then
    echo "Usage: $(basename $0) filename"
    exit 1
fi

if [ ! -f "$1" ]; then
    echo "File "$1" doesn't exist!"
    exit 0
fi

# Check for special programs that are used in this script.
P=gs
which $P >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "$(basename $0): The program \"$P\" cannot be found."
    exit 1
fi

if ! grep '%%Pages\?:.*1' >/dev/null $1; then
    echo "Sorry, this script only works for single-page documents!"
    exit 0
fi

# Determine the new BoundingBox.
# This only works properly for single-page documents!
NEWBB=$(echo|gs -sDEVICE=bbox $1 -c quit 2>&1|grep '^%%B')

sed -I .bak -e "s/^%%Bound.*/$NEWBB/" $1

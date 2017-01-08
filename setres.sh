#!/bin/sh
# Sets the resolution of pictures to the provided value.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2017-01-08 14:27:45 +0100
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to 'setres'. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

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
for f in $@; do
    mogrify -units PixelsPerInch -density $RES $f
done

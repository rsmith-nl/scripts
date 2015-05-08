#!/bin/sh
#
# Create a distinfo file for a FreeBSD port.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to mkdistinfo. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

if [ ! "$1" ]; then
    echo "Usage: $0 file";
    exit 1;
fi

rm -f distinfo
sha256 $1 >> distinfo
SZ=$(ls -l $1|awk '{print $5};')
echo "SIZE ($1) = ${SZ}" >>distinfo

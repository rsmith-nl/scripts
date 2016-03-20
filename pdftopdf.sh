#!/bin/sh
# Re-write a PDF file with ghostscript.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-02-27 00:15:14 +0100
# Last modified: 2016-03-20 18:53:22 +0100
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to pdftopdf. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

if [ $# -lt 1 ]; then
    echo "Usage: $(basename $0) file"
    exit 1
fi

# Check for special programs that are used in this script.
PROGS="gs"
for P in $PROGS; do
    which $P >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "$(basename $0): The program \"$P\" cannot be found."
        exit 1
    fi
done

TMPNAME=$(mktemp)
INNAME=$1

set -e
gs -DNOPAUSE -sDEVICE=pdfwrite \
    -sOutputFile=$TMPNAME $INNAME -c quit >/dev/null 2>&1
mv $INNAME ${INNAME%.pdf}-orig.pdf
cp $TMPNAME $INNAME
rm -f $TMPNAME

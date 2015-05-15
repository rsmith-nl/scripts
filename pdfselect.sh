#!/bin/sh
# Select consecutive pages from a PDF document
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-05-15 18:41:46 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to pdfselect. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/


if [ $# -lt 3 ]; then
    echo "Usage: $(basename $0) N M file"
    echo "Where 'N' to 'M' are the numbers of the page you want to extract."
    echo "'file' is the name of the file you want to extract from."
    echo "The page will be written to a file pageN(-M).pdf."
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

N=$1
M=$2

if [ ! -f $3 ]; then
    echo "File "$3" does not exist.";
    exit 1;
fi

if [ ${N} -eq ${M} ]; then
    OUTNAME=page${N}.pdf
else
    OUTNAME=page${N}-${M}.pdf
fi

gs -DNOPAUSE -sDEVICE=pdfwrite -dFirstPage=${N} -dLastPage=${M} \
    -sOutputFile=$OUTNAME $3 -c quit >/dev/null 2>&1

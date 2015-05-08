#!/bin/sh
# Creates a PDF file from scanned images @ 150 DPI.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to mkpdf. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

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
PROGS="jpeg2ps epspdf"
for P in $PROGS; do
    which $P >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "$(basename $0): The program \"$P\" cannot be found."
        exit 1
    fi
done

echo -n "Gathering pages in PostScript file..."
rm -f ${OUTF}.ps
touch ${OUTF}.ps
for f in $@; do
    jpeg2ps -q -r $RES -p $PAGE $f >>${OUTF}.ps
done
echo "done."
echo -n "Converting to pdf... "
epspdf ${OUTF}.ps ${OUTF}.pdf
rm ${OUTF}.ps
echo "done."

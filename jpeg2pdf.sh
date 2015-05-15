#!/bin/sh
# Converts a list of JPEG files to a PDF file.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-05-15 18:39:47 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to jpeg2pdf. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

# Check for arguments
if [ $# -lt 2 ]; then
    echo "Usage: $(basename $0) output input-files"
    exit 1
fi

# Check for special programs that are used in this script.
PROGS="jpeg2ps ps2pdf pdftk"
for P in $PROGS; do
    which $P >/dev/null 2>&1
    if [ $? -ne 0 ]; then
	echo "$(basename $0): The program \"$P\" cannot be found."
	exit 1
    fi
done

OUT=${1}.pdf
PDFS=
INFO=$(mktemp -q info.XXXXXXXX)
INTM=$(mktemp -q pdf.XXXXXXXX)
cat >$INFO <<EOF
InfoKey: Title
InfoValue: $1
InfoKey: Author
InfoValue: $USER
EOF
shift
for f in $*; do
    #echo "Converting $f to ${f%.jpg}.pdf."
    jpeg2ps -b -o ${f%.jpg}.eps -p a4 -q $f
    ps2pdf ${f%.jpg}.eps
    rm -f ${f%.jpg}.eps
    PDFS=$PDFS' '${f%.jpg}.pdf
done
#echo "Merging the pages $PDFS into $OUT."
pdftk $PDFS output $INTM
pdftk $INTM update_info $INFO output $OUT
rm -f $PDFS $INFO $INTM

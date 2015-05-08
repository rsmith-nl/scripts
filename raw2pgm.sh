#!/bin/sh
# raw2pgm: Convert raw DICOM files to portable graymap
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to raw2pgm. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

# Check for arguments
if [ $# -eq 0 ]; then
    echo "Usage: $(basename $0) filename"
    exit 1
fi
FN=$1

# Check for special programs that are used in this script.
PROGS="convert"
for P in $PROGS; do
    which $P >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "$(basename $0): The program \"$P\" cannot be found."
        exit 1
    fi
done


# Size of the header
HS=$(awk '/^headerLength.*[0-9]+/ {print $2;}' $FN)

# Height and width of the picture
HEIGHT=$(awk '/^numberOfScanLines.*[0-9]+/ {print $2;}' $FN)
WIDTH=$(awk '/^numberOfPixelsInScanLine.*[0-9]+/ {print $2;}' $FN)

# Number of colors; 16 bit data.
NC=65535

# file size
FS=$(ls -l $FN|cut  -f 8 -d ' ' -)

# Output file basename
OF=$(basename $FN .xxx)

# data size
DS=$(($FS-$HS))

#echo "File: $FN"
#echo "Size: $FS bytes"
#echo "Header: $HS bytes"
#echo "Data size: $(($FS-$HS))"
#echo "Check: $(($HEIGHT*$WIDTH*2))"

# Convert to a Portable GrayMap.
echo "Converting: 1st stage..."
echo "P5" > ${OF}.pgm
echo "$WIDTH $HEIGHT" >> ${OF}.pgm
echo "65535" >> ${OF}.pgm
dd if=$FN ibs=1 obs=4096 count=$DS iseek=$HS >> ${OF}.pgm 2>/dev/null

# Now, normalize the contrast and convert to JPEG.
echo "Converting: 2nd stage..."
convert ${OF}.pgm -normalize ${OF}.jpg
rm ${OF}.pgm


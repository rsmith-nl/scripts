#!/bin/sh
# Make an index jpg of all pictures given as arguments.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-05-15 18:40:52 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to mkindexpic. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

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
montage -tile 8 -label "%f\n%wx%h\n%[EXIF:DateTime]" $@ index.jpg

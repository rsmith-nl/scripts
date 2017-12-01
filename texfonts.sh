#!/bin/sh
# The purpose of this script is to find OpenType fonts from a TeXLive installation
# and make them useable for other applications via fontconfig.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-10-18 22:12:31 +0200
# Last modified: 2017-12-01 19:49:51 +0100
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to texfonts.sh. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

set -eu

TEXOTF=/usr/local/texlive/2017/texmf-dist/fonts/opentype
INSTDIR=/usr/local/share/fonts/texlive
#INSTDIR=/tmp/foo

FNTS=`find $TEXOTF -type f -name '*.otf'`

echo "Removing old install directory"
rm -rf $INSTDIR
echo "Creating install directory"
mkdir -p $INSTDIR
cd $INSTDIR
echo -n "Filling install directory: "
for fp in $FNTS; do
    fn=`basename $fp`
    echo -n .
    ln -s $fp $fn
done
echo " done"
# Remove some fonts.
rm -f drm* cm* ffm* smf* DANTE* ocrb[5-9]* emmentaler*
echo "Updating font cache for $INSTDIR"
fc-cache $INSTDIR

#!/bin/sh
# The purpose of this script is to find OpenType fonts from a TeXLive installation
# and make them useable for other applications via fontconfig.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-10-18 22:12:31 +0200
# Last modified: 2017-12-02 22:24:13 +0100
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to texfonts.sh. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

set -eu
umask 022

TEXOTF=`ls -d /usr/local/texlive/*/texmf-dist/fonts/opentype`
INSTDIR=/usr/local/share/fonts/texlive
#INSTDIR=/tmp/foo

if [ -z ${TEXOTF} ]; then
    echo "Cannot find TeX OpenType fonts."
    exit 1
fi

if [ `id -u` != 0 ]; then
    echo "This command must be run as root."
    exit 2
fi

FNTS=`find $TEXOTF -type f -name '*.otf'`

echo "Removing old install directory."
rm -rf $INSTDIR
echo "Creating install directory."
mkdir -p $INSTDIR
cd $INSTDIR
echo -n "Filling install directory: "
for fp in $FNTS; do
    fn=`basename $fp`
    echo -n .
    ln -s $fp $fn
done
echo " done."
echo -n "Doing some housekeeping... "
# Remove some fonts.
rm -f lm*[1-9]-* lm*1[1-9]-* MnSymbol[5-9].otf MnSymbol12.otf drm* ffm* smf* DANTE* ocrb[5-9]* emmentaler*
echo " done."

echo -n "Updating font cache for $INSTDIR..."
fc-cache $INSTDIR
echo " done."

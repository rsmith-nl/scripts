#!/bin/sh
# Front-end for the POV-ray raytracer.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2016-06-11 23:10:17 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to povmake. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

# Check for special programs that are used in this script.
P=povray
which $P >/dev/null 2>&1
if [ $? -ne 0 ]; then
    P=povray37
    which $P >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "$(basename $-1): The program \"povray[37]\" cannot be found."
        exit 0
    fi
fi

if [ $# -ne 3 ]; then
    echo "Usage: povmake <size> <quality> file";
    echo "where <size> is one of: s[mall] m[edium] l[arge] x[large] h[uge]";
    echo "and <quality> is one of: l[ow] m[ed] h[igh] [e]x[tra]";
    echo "Saves files in PNG format.";
    exit 1;
fi

set -e
# get the filename without the extension
FILEBASE=`basename $3|sed -E -e 's/(.*)(\..*)/\1/g'`
#echo $FILEBASE

# get the file's extension
FILEEXT=$(echo $3|sed -E -e 's/(.*\.)([^\.+])/\2/g')
#echo $FILEEXT

if [ ! "$FILEEXT" = "pov" ]; then
    echo "$3 is not a POVray-source file!";
    exit 3;
fi

OPTIONS='+I'$3' +O'$FILEBASE'.png +FN +D -P'

case $1 in
    s|small) OPTIONS=$OPTIONS' +W320 +H200';;
    m|medium) OPTIONS=$OPTIONS' +W640 +H480';;
    l|large) OPTIONS=$OPTIONS' +W800 +H600';;
    x|xlarge) OPTIONS=$OPTIONS' +W1024 +H768';;
    h|huge) OPTIONS=$OPTIONS' +W1280 +H1024';;
    *) echo "Unknown option?"; exit 3;;
esac

case $2 in
    l|low) OPTIONS=$OPTIONS' +SP16 +EP8 +Q3';;
    m|medium) OPTIONS=$OPTIONS' +SP8 +EP4 +Q7';;
    h|high) OPTIONS=$OPTIONS' +SP2 +EP2 +A0.05 +R9 +Q9';;
    x|extra) OPTIONS=$OPTIONS' +SP2 +EP2 +A0.05 +R9 +Q11';;
    *) echo "Unknown option?"; exit 4;;
esac

echo "options: "$OPTIONS
echo -n "povray is running... "
$P $OPTIONS
echo "done."

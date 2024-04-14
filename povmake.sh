#!/bin/sh
# file: povmake.sh
# vim:fileencoding=utf-8:ft=sh
# Front-end for the POV-ray raytracer.
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-05-08T22:12:45+02:00
# Last modified: 2018-04-16T22:28:44+0200

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

case $1 in
    s|small)  W=640; H=480; D='+D +P';;
    m|medium) W=800; H=600; D='+D +P';;
    l|large) W=1024; H=768; D='+D +P';;
    x|xlarge) W=1280; H=1024; D='+D +P';;
    h|huge) W=2560; H=2048; D='-D -P';;
    *) echo "Unknown option?"; exit 3;;
esac
OFN=$FILEBASE'-'$W'x'$H'.png'
OPTIONS='+I'$3' +O'$OFN' +FN +W'$W' +H'$H' '$D

case $2 in
    l|low) OPTIONS=$OPTIONS' +SP16 +EP8 +Q3';;
    m|medium) OPTIONS=$OPTIONS' +SP8 +EP4 +Q7';;
    h|high) OPTIONS=$OPTIONS' +SP2 +EP2 +AM2 +A0.05 +R9 +Q9';;
    x|extra) OPTIONS=$OPTIONS' +SP2 +EP2 +AM2 +A0.05 +R9 +Q11';;
    *) echo "Unknown option?"; exit 4;;
esac

echo "options: "$OPTIONS
echo -n "povray is running... "
$P $OPTIONS
echo "done."

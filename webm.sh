#!/bin/sh
# file: webm.sh
# vim:fileencoding=utf-8:ft=sh
# Two-pass webm encoding
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-06-21T16:44:34+0200
# Last modified: 2018-04-16T22:43:29+0200

# Check for non-standard programs that are used in this script.
FF=ffmpeg
which $FF >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "$(basename $0): The program \"$FF\" cannot be found."
    exit 1
fi

set -e

if [ $# -lt 2 ]; then
    echo "Usage: webm <vod|crq|con|bq> file";
    echo "where;";
    echo "- vod means video on demand,";
    echo "- crq means constrained rate quality,";
    echo "- con means constant rate quality and";
    echo "- bq means best quality.";
    echo "Constrained quality gives small file size.";
    exit 1;
fi

INP=$2
FILEBASE=`basename $2|sed -E -e 's/(.*)(\..*)/\1/g'`

# Settings from:
# http://wiki.webmproject.org/ffmpeg/vp9-encoding-guide
# But using Vorbis instead of Opus.
case $1 in
    vod) echo "Encoding for video on demand.";
        FP="-c:v libvpx-vp9 -threads 8 -pass 1 -b:v 1000K -g 250 -speed 4 -tile-columns 6 -frame-parallel 0 -an -f webm -y /dev/null";
         SP="-c:v libvpx-vp9 -threads 8 -pass 2 -b:v 1000K -g 250 -speed 1 -tile-columns 6 -frame-parallel 0 -auto-alt-ref 1 -lag-in-frames 25 -c:a libvorbis -q:a 3 -f webm -y";;
    crq) echo "Encoding for constrained rate quality.";
         FP="-c:v libvpx-vp9 -threads 8 -pass 1 -b:v 1400k -crf 33 -g 250 -speed 4 -tile-columns 6 -frame-parallel 0 -an -f webm -y /dev/null";
        SP="-c:v libvpx-vp9 -threads 8 -pass 2 -b:v 1400k -crf 33 -g 250 -speed 2 -tile-columns 6 -frame-parallel 0 -auto-alt-ref 1 -lag-in-frames 25 -c:a libvorbis -q:a 3 -f webm -y";;
    con) echo "Encoding for constant quality.";
         FP="-c:v libvpx-vp9 -threads 8 -pass 1 -b:v 0 -crf 25 -g 250 -speed 4 -tile-columns 6 -frame-parallel 0 -an -f webm -y /dev/null";
        SP="-c:v libvpx-vp9 -threads 8 -pass 2 -b:v 0 -crf 25 -g 250 -speed 2 -tile-columns 6 -frame-parallel 0 -auto-alt-ref 1 -lag-in-frames 25 -c:a libvorbis -q:a 3 -f webm -y";;
    bq) echo "Encoding for best quality.";
         FP="-c:v libvpx-vp9 -threads 1 -pass 1 -b:v 1000K -g 250 -speed 4 -tile-columns 0 -frame-parallel 0 -g 9999 -aq-mode 0 -an -f webm -y /dev/null";
        SP="-c:v libvpx-vp9 -threads 1 -pass 2 -b:v 1000K -g 250 -speed 0 -tile-columns 0 -frame-parallel 0 -auto-alt-ref 1 -lag-in-frames 25 -g 9999 -aq-mode 0 -c:a libvorbis -q:a 3 -f webm -y";;
    *) echo "Unknown command"; exit 1;;
esac

echo -n "First pass... "
FPSTART=`date "+%s"`
$FF -i $INP -passlogfile $FILEBASE $FP >/dev/null 2>&1
FPEND=`date "+%s"`
echo "done ($(($FPEND-$FPSTART)) seconds)"
echo -n "Second pass... "
SPSTART=`date "+%s"`
$FF -i $INP -passlogfile $FILEBASE $SP ${FILEBASE}.webm >/dev/null 2>&1
SPEND=`date "+%s"`
rm -f ${FILEBASE}*.log
echo "done ($(($SPEND-$SPSTART)) seconds)"

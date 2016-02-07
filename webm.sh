#!/bin/sh
# file: webm.sh
# vim:fileencoding=utf-8:ft=sh
# Two-pass webm encoding
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-06-21 16:44:34 +0200
# Last modified: 2016-02-07 17:27:59 +0100

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
FF=ffmpeg

# Settings from:
# https://sites.google.com/a/webmproject.org/wiki/ffmpeg/vp9-encoding-guide
# But using Vorbis instead of Opus.
case $1 in
    vod) echo "Encoding for video on demand.";
        FP="-c:v libvpx-vp9 -threads 4 -pass 1 -b:v 1000K -g 250 -speed 4 -tile-columns 6 -frame-parallel 1 -an -f webm -y /dev/null";
         SP="-c:v libvpx-vp9 -threads 4 -pass 2 -b:v 1000K -g 250 -speed 1 -tile-columns 6 -frame-parallel 1 -auto-alt-ref 1 -lag-in-frames 25 -c:a libvorbis -q:a 3 -f webm -y";;
    crq) echo "Encoding for constrained rate quality.";
         FP="-c:v libvpx-vp9 -threads 4 -pass 1 -b:v 1400k -crf 33 -g 250 -speed 4 -tile-columns 6 -frame-parallel 1 -an -f webm -y /dev/null";
        SP="-c:v libvpx-vp9 -threads 4 -pass 2 -b:v 1400k -crf 33 -g 250 -speed 2 -tile-columns 6 -frame-parallel 1 -auto-alt-ref 1 -lag-in-frames 25 -c:a libvorbis -q:a 3 -f webm -y";;
    con) echo "Encoding for constant quality.";
         FP="-c:v libvpx-vp9 -pass 1 -b:v 0 -crf 25 -g 250 -speed 4 -tile-columns 6 -frame-parallel 1 -an -f webm -y /dev/null";
        SP="-c:v libvpx-vp9 -pass 2 -b:v 0 -crf 25 -g 250 -speed 2 -tile-columns 6 -frame-parallel 1 -auto-alt-ref 1 -lag-in-frames 25 -c:a libvorbis -q:a 3 -f webm -y";;
    bq) echo "Encoding for best quality.";
         FP="-c:v libvpx-vp9 -threads 1 -pass 1 -b:v 1000K -g 250 -speed 4 -tile-columns 0 -lag-in-frames 25 -g 9999 -aq-mode 0 -an -f webm -y /dev/null";
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

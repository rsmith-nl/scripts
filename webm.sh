#!/bin/sh
# file: webm.sh
# vim:fileencoding=utf-8:ft=sh
# Two-pass webm encoding
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-06-21 16:44:34 +0200
# Last modified: 2015-06-21 20:27:12 +0200

if [ $# -lt 2 ]; then
    echo "Usage: webm <vod|cq|bq> file";
    echo "where;";
    echo "- vod means video on demand,";
    echo "- cq means constant quality and";
    echo "- bq means best quality.";
    echo "\nConstant quality gives small file size.";
    exit 1;
fi

INP=$2
FILEBASE=`basename $2|sed -E -e 's/(.*)(\..*)/\1/g'`
FF=ffmpeg26

# Settings from:
# https://sites.google.com/a/webmproject.org/wiki/ffmpeg/vp9-encoding-guide
case $1 in
    vod) echo "Encoding for video on demand.";
        FP="-c:v libvpx-vp9 -pass 1 -b:v 1000K -threads 8 -speed 4 -tile-columns 6 -frame-parallel 1 -auto-alt-ref 1 -lag-in-frames 25 -an -f webm -y /dev/null";
         SP="-c:v libvpx-vp9 -pass 2 -b:v 1000K -threads 8 -speed 1 -tile-columns 6 -frame-parallel 1 -auto-alt-ref 1 -lag-in-frames 25 -c:a libopus -b:a 64k -f webm -y";;
    cq) echo "Encoding for constant quality.";
         FP="-c:v libvpx-vp9 -pass 1 -b:v 0 -crf 33 -threads 8 -speed 4 -tile-columns 6 -frame-parallel 1 -auto-alt-ref 1 -lag-in-frames 25 -an -f webm -y /dev/null";
        SP="-c:v libvpx-vp9 -pass 2 -b:v 0 -crf 33 -threads 8 -speed 2 -tile-columns 6 -frame-parallel 1 -auto-alt-ref 1 -lag-in-frames 25 -c:a libopus -b:a 64k -f webm -y";;
    bq) echo "Encoding for best quality.";
         FP="-c:v libvpx-vp9 -pass 1 -b:v 1000K -threads 1 -speed 4 -tile-columns 0 -frame-parallel 0 -auto-alt-ref 1 -lag-in-frames 25 -g 9999 -aq-mode 0 -an -f webm -y /dev/null";
        SP="-c:v libvpx-vp9 -pass 2 -b:v 1000K -threads 1 -speed 0 -tile-columns 0 -frame-parallel 0 -auto-alt-ref 1 -lag-in-frames 25 -g 9999 -aq-mode 0 -c:a libopus -b:a 64k -f webm -y";;
    *) echo "Unknown command"; exit 1;;
esac

echo -n "First pass... "
FPSTART=`date "+%s"`
$FF -i ${INP} $FP >/dev/null 2>&1
FPEND=`date "+%s"`
echo "done ($(($FPEND-$FPSTART)) seconds)"
echo -n "Second pass... "
SPSTART=`date "+%s"`
$FF -i ${INP} $SP ${FILEBASE}.webm >/dev/null 2>&1
SPEND=`date "+%s"`
echo "done ($(($SPEND-$SPSTART)) seconds)"

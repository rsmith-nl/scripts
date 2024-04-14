#!/bin/sh
# file: eps2png.sh
# vim:fileencoding=utf-8:ft=sh
# Script to convert EPS images to PNG format using ghostscript.
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2018-11-15T22:05:09+0100
# Last modified: 2021-02-28T20:49:59+0100

set -e

RES=300
DEV=png16m
args=`getopt r:d:h $*`
if [ $? -ne 0 ]; then
        echo "Usage: $0 [-r 300] [-d png16m]"
        exit 2
fi
set -- $args
while :; do
    case "$1" in
        -r)
            RES=$2
            echo "* Using ${RES} ppi."
            shift; shift
            ;;
        -d)
            DEV=$2
            BEGIN=`echo $DEV|cut -c 1-3`
            if [ $BEGIN = 'png' ]; then
                echo "* Using the ${DEV} device."
            else
                echo "\'$BEGIN\' is not a PNG device. Using png16m."
                DEV=png16m
            fi
            shift; shift
            ;;
        -h)
            echo "Script to convert EPS images to PNG format."
            echo ""
            exit 0
            ;;
        --)
            shift; break
            ;;
    esac
done

for f in $@; do
    OUTNAME=${f%.eps}.png
    BB=`gs -q -sDEVICE=bbox -dBATCH -dNOPAUSE $f 2>&1 | grep %%BoundingBox`
    WIDTH=`echo $BB | cut -d ' ' -f 4`
    HEIGHT=`echo $BB | cut -d ' ' -f 5`
    WPIX=$(($WIDTH*$RES/72))
    HPIX=$(($HEIGHT*$RES/72))
    gs -q -sDEVICE=${DEV} -dBATCH -dNOPAUSE -g${WPIX}x${HPIX} \
        -dTextAlphaBits=4 -dGraphicsAlphaBits=4 \
        -dFIXEDMEDIA -dPSFitPage -r${RES} -sOutputFile=${OUTNAME} $f
    echo "${f}: width= ${WIDTH} pt, height= ${HEIGHT} pt → ${OUTNAME} (${WPIX}x${HPIX})"
done

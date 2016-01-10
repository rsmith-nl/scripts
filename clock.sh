#!/bin/sh
#
# Script to show all the times that are important for me.
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2016-01-10 21:24:11 +0100
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to 'clock'. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

ZONES="UTC Europe/Amsterdam EST Asia/Shanghai Asia/Seoul Pacific/Auckland"

for z in $ZONES; do
    printf "%16s: " $z
    TZ=$z LC_ALL="nl_NL.UTF-8" date "+%A %d %B %Y, %H:%M:%S"
done

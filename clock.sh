#!/bin/sh
# file: clock.sh
# Script to show all the times that are important for me.
# vim:fileencoding=utf-8:fdm=marker:ft=sh
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-05-08T22:12:45+02:00
# Last modified: 2018-04-16T21:25:46+0200

set -eu

ZONES="UTC Europe/Amsterdam Europe/London Asia/Shanghai Asia/Seoul Pacific/Auckland"

for z in $ZONES; do
    printf "%16s: " $z
    TZ=$z LC_ALL="nl_NL.UTF-8" date "+%A %d %B %Y, %H:%M:%S"
done

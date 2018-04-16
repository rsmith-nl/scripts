#!/bin/sh
# file: find-modified.sh
# vim:fileencoding=utf-8:fdm=marker:ft=sh
#
# Copyright © 2015-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-05-08T22:12:45+02:00
# Last modified: 2018-04-16T21:57:25+0200

if [ -z $1 ]; then
   echo "Error: you must give a number of days as the argument."
   echo "usage: $(basename $0) [number]"
   echo "This finds the files from the current directory downwards,"
   echo "that have been modified up to [number] days ago."
   exit 0
fi

EXCLUDED="/\..*|WWW/output|tmp"

cd $HOME
find . -mtime -$1 -type f |grep -Ev $EXCLUDED|cut -c 3-

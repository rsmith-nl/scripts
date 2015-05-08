#!/bin/sh
# finds files that have been modified at most $1 days ago.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to find-modified. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

if [ -z $1 ]; then
   echo "Error: you must give a number of days as the argument."
   echo "usage: $(basename $0) [number]"
   echo "This finds the files from your home directory downwards,"
   echo "that have been modified up to [number] days ago."
   exit 0
fi

EXCLUDED="/\..*|WWW/output|tmp"

cd $HOME
find . -mtime -$1 -type f |grep -Ev $EXCLUDED|cut -c 3-

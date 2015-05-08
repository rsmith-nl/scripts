#!/bin/sh
# Starts the git daemon for all git repositories under the current working
# directory.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to serve-git. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

# Check for special programs that are used in this script.
PROGS="git"
for P in $PROGS; do
    which $P >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "$(basename $0): The program \"$P\" cannot be found."
        exit 1
    fi
done

WD=$(pwd)
GITDIRS=$(find $WD -type d -name '.git'|sort)
echo "Starting git-daemon for the following directories:"
echo $GITDIRS|fmt
echo "Press CTRL-C to quit."
git daemon --reuseaddr --verbose --export-all --base-path=/home/rsmith $GITDIRS


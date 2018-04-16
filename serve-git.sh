#!/bin/sh
# file: serve-git.sh
# vim:fileencoding=utf-8:fdm=marker:ft=sh
# Starts the git daemon for all git repositories under the current working
# directory.
#
# Copyright © 2015-2016 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2016-03-19T10:35:02+0100
# Last modified: 2018-04-16T22:33:31+0200

# Check for special programs that are used in this script.
PROGS="git"
for P in $PROGS; do
    which $P >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "$(basename $0): The program \"$P\" cannot be found."
        exit 1
    fi
done

set -eu
WD=$(pwd)
GITDIRS=$(find $WD -type d -name '.git'|sort)
echo "Starting git-daemon for the following directories:"
echo $GITDIRS|fmt
echo "Press CTRL-C to quit."
git daemon --reuseaddr --verbose --export-all --base-path=/home/rsmith $GITDIRS


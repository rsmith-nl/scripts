#!/bin/sh
# file: genbackup.sh
# vim:fileencoding=utf-8:fdm=marker:ft=sh
# Generate a full backup of the current directory.
#
# Copyright © 2013-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2013-08-13T22:13:23+0200
# Last modified: 2020-08-14T18:37:20+0200

set -e

CURDIR=$(basename "$(pwd)")
EXCLUDE=""
# Process the options
while [ "$1" != "" ]; do
    case $1 in
        -h | --help )           echo "Usage: $0 [-n name] [-x exclude] [-h]"
                                exit
                                ;;
        -n | --name )           shift
                                OUTNAME=$1
                                ;;
        -x | --exclude )        shift
                                EXCLUDE=${EXCLUDE}" --exclude $1"
                                ;;
    esac
done
# The base of the name is the last part of the current directory, unless
# another name was given in the options.
NAME=$(echo $CURDIR|sed -e 's/^\./dot/' -e 's/\.//g' -e 's/ /-/g')
OUTNAME=${OUTNAME:-$NAME}
# Use the date in the filename of the archive.
NUM=-$(date -u '+%Y%m%dT%H%M%SZ')
# Add the short hashtag if the current directory is revision control by git.
if [ -d .git ]; then
    NUM=${NUM}-$(git log -n 1 --oneline |cut -c 1-7)
fi
# Remove old backups first
rm -f backup-${OUTNAME}*.tar*
# Use tar for backup. Compress with gzip.
DF=backup-${OUTNAME}${NUM}.tar.gz
echo "A copy of ${CURDIR} is stored in ${DF}."
cd .. ; tar -a -cf "/tmp/${DF}" ${EXCLUDE} "${CURDIR}/"
mv "/tmp/${DF}" "${CURDIR}/"

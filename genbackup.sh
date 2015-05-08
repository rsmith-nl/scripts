#!/bin/sh
# vim:fileencoding=utf-8
# Shell script to generate a full backup of the current directory.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2013-08-13 22:13:23 +0200
# Modified: $Date$
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to genbackup. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

CURDIR=$(basename $(pwd))
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
    shift
done
# The base of the name is the last part of the current directory, unless
# another name was given in the options.
NAME=$(echo $CURDIR|sed 's/^\./dot/')
OUTNAME=${OUTNAME:-$NAME}
# Add the short hashtag if the current directory is revision control by git.
if [ -d .git ]; then
    NUM=-$(git log -n 1 --oneline |cut -c 1-7)
else
    NUM=''
fi
# Remove old backups first
rm -f backup-${OUTNAME}*.tar
# Use tar for backup. Standard compression with gzip.
DF=backup-${OUTNAME}${NUM}.tar
echo "A copy of ${CURDIR} is stored in ${DF}."
cd .. ; tar cf /tmp/${DF} ${EXCLUDE} ${CURDIR}/
mv /tmp/${DF} ${CURDIR}/

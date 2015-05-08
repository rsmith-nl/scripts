#!/bin/sh
# file: usr/local/sbin/backup-local
# vim:fileencoding=utf-8:ft=sh
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2008-05-26 22:59:14 +0200
# Last modified: 2015-05-08 19:32:28 +0200
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to backup-local. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

# Check for non-standard programs that are used in this script.
PROGS="rsync"
for P in $PROGS; do
    which $P >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "$(basename $0): The program \"$P\" cannot be found."
        exit 1
    fi
done

FLAGS="-axq -H --delete"
LOG="logger -t 'backup-local'"

# This script assumes that the backups are not mounted.

__mkbackup() { # 1=origin 2=dest
    echo mount ${2}
    if df|grep ${2} >/dev/null; then
        echo rsync $FLAGS ${1%/}/ ${2} && $LOG "${1} successfully backed-up."
        echo umount ${2}
    else
        echo "Backup for ${1} not mounted! Not backed up."
    fi
}

# The main program
__mkbackup / /mnt/bk/root
__mkbackup /usr /mnt/bk/usr
__mkbackup /var /mnt/bk/var

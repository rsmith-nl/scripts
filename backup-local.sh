#!/bin/sh
# Backs up mount points to other mount points.
# This script is designed to be run from cron.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2008-05-26 22:59:14 +0200
# Last modified: 2016-03-19 10:41:20 +0100
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

# __mkbackup origin dest
#
# Backs up a mount point to another mount point.
# This function assumes that the backups are *not* mounted.
#
# Arguments:
#     origin: mount point to copy.
#     dest: mount point to back up to.
#
# Requires:
#   * rsync
__mkbackup() { # 1=origin 2=dest
    mount ${2}
    if df|grep ${2} >/dev/null; then
        rsync $FLAGS ${1%/}/ ${2} && $LOG "${1} successfully backed-up."
        umount ${2}
    else
        $LOG "Backup for ${1} not mounted! Not backed up."
    fi
}

# The main program;
__mkbackup / /mnt/bk/root
__mkbackup /usr /mnt/bk/usr
__mkbackup /var /mnt/bk/var
__mkbackup /home /mnt/bk/home

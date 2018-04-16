#!/bin/sh
# file: backup-local.sh
# vim:fileencoding=utf-8:fdm=marker:ft=sh
#
# Copyright © 2008-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2008-05-26 22:59:14 +0200
# Last modified: 2018-04-16 20:06:49 +0200

# Check for non-standard programs that are used in this script.
PROGS="/usr/local/bin/rsync"
for P in $PROGS; do
    which $P >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "$(basename $0): The program \"$P\" cannot be found."
        exit 1
    fi
done

FLAGS="-axq -H --delete"
LOG="/usr/bin/logger -t 'backup-local'"

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
    /sbin/mount ${2}
    if /bin/df|/usr/bin/grep ${2} >/dev/null; then
        /usr/local/bin/rsync $FLAGS ${1%/}/ ${2} && $LOG "${1} successfully backed-up."
        /sbin/umount ${2}
    else
        $LOG "Backup for ${1} not mounted! Not backed up."
    fi
}

# The main program;
__mkbackup / /mnt/bk/root
__mkbackup /usr /mnt/bk/usr
__mkbackup /var /mnt/bk/var
__mkbackup /home /mnt/bk/home

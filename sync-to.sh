#!/bin/sh
# Use rsync to syncronize a directory to/from another computer.
#
# Copyright © 2015-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-25 17:55:24 +0200
# Last modified: 2022-01-22T21:25:37+0100

set -eu

usage="Usage: sync-to <host> [-h][[-f][-r][-c] <dir>]

Uses rsync to syncronize files between two computers.

The rsync(1) daemon should be running on <host>.  The /home directory on
<host> should be listed as the [home] module in the rsyncd.conf(5) on <host>.

Options:
  -h: Display help.
  -a: Don't hide files related to revision control.
  -c: Use checksum instead of date to look for changed files.
  -r: Transfer in reverse direction; from <host> to us.
  -f: Really sync files. the default is to perform a dry run.

The <host> parameter contains the hostname of the host to synchronize to.
The <dir> parameter is the directory to syncronize, relative to the current directory.
It should be the same on both machines.
"

US=`hostname -s`
HOST=${1}
shift
args=`getopt fhrca $*`
if [ $? -ne 0 ]; then
    echo "$usage"
    exit 1
fi
set -- $args
FORCE=""
ALL=""
REVERSE=""
CHECKSUM=""
while true; do
    case "$1" in
        -h)
            echo "$usage"
            exit 1
            ;;
        -a)
            ALL='yes'
            shift
            ;;
        -f)
            FORCE='yes'
            shift
            ;;
        -r)
            REVERSE='yes'
            shift
            ;;
        -c)
            CHECKSUM='yes'
            shift
            ;;
        --)
            shift; break
            ;;
        esac
done
if [ $# -ne 1 ]; then
    echo "$usage"
    exit 1
fi
DIR=$(pwd)/${1%%/}
#echo "DEBUG: host=${HOST}, dir=${DIR}"
if ! ping -q -c 1 ${HOST} > /dev/null; then
    echo "${HOST} cannot be pinged!"
    exit 2
fi
if [ ! -d ${DIR} ]; then
    echo "${DIR} is not a directory!"
    exit 3
fi
DIR=${DIR##/home/${USER}/}

OPTS='-avCn'
if [ $FORCE ]; then
    OPTS='-av'
elif [ $ALL ]; then
    OPTS='-avn'
fi
if [ $CHECKSUM ]; then
    OPTS=${OPTS}'c'
fi
if [ $REVERSE ]; then
    echo "Syncing from ${HOST} to ${US}."
    rsync ${OPTS} --delete ${HOST}::home/${USER}/${DIR}/ /home/${USER}/${DIR}
else
    echo "Syncing from ${US} to ${HOST}."
    rsync ${OPTS} --delete /home/${USER}/${DIR}/ ${HOST}::home/${USER}/${DIR}
fi

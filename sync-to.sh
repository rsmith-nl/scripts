#!/bin/sh
# Use rsync to syncronize a directory to/from my laptop.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-25 17:55:24 +0200
# Last modified: 2017-12-10 18:46:56 +0100

set -eu

usage="Usage: sync-laptop [-h][[-f][-r] <host> <dir>]

Uses rsync to syncronize files between my desktop and laptop.

Options:
  -h: help
  -r: Transfer from laptop to desktop.
  -f: Really sync files. the default is to perform a dry run.

The <host> parameter contains the hostname of the host to synchronize to.
The <dir> parameter is the directory to syncronize, relative to the current directory.
"


args=`getopt fhr $*`
if [ $? -ne 0 ]; then
    echo "$usage"
    exit 1
fi
set -- $args
FORCE=""
REVERSE=""
while true; do
    case "$1" in
        -h)
            echo "$usage"
            exit 1
            ;;
        -f)
            FORCE='yes'
            shift
            ;;
        -r)
            REVERSE='yes'
            shift
            ;;
        --)
            shift; break
            ;;
        esac
done
if [ $# -ne 2 ]; then
    echo "$usage"
    exit 1
fi
HOST=${1}
DIR=$(pwd)/${2%%/}
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
OPTS='-avn'
if [ $FORCE ]; then
    OPTS='-av'
fi
if [ $REVERSE ]; then
    rsync ${OPTS} --delete ${HOST}::home/${USER}/${DIR}/ /home/${USER}/${DIR}
else
    rsync ${OPTS} --delete /home/${USER}/${DIR}/ ${HOST}::home/${USER}/${DIR}
fi

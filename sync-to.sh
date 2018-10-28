#!/bin/sh
# Use rsync to syncronize a directory to/from my laptop.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-25 17:55:24 +0200
# Last modified: 2018-10-28T12:31:05+0100

set -eu

usage="Usage: sync-laptop <host> [-h][[-f][-r] <dir>]

Uses rsync to syncronize files between my desktop and laptop.

Options:
  -h: help
  -r: Transfer in reverse direction; from <host> to us.
  -f: Really sync files. the default is to perform a dry run.

The <host> parameter contains the hostname of the host to synchronize to.
The <dir> parameter is the directory to syncronize, relative to the current directory.
"

US=`hostname -s`
HOST=${1}
shift
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
OPTS='-avn'
if [ $FORCE ]; then
    OPTS='-av'
fi
if [ $REVERSE ]; then
    echo "Syncing from ${HOST} to ${US}."
    rsync ${OPTS} --delete ${HOST}::home/${USER}/${DIR}/ /home/${USER}/${DIR}
else
    echo "Syncing from ${US} to ${HOST}."
    rsync ${OPTS} --delete /home/${USER}/${DIR}/ ${HOST}::home/${USER}/${DIR}
fi

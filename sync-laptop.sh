#!/bin/sh
# Use rsync to syncronize a directory to/from my laptop.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-25 17:55:24 +0200
# Last modified: 2016-03-19 12:37:48 +0100

set -eu

usage="Usage: sync-laptop [-h][[-f][-r] <dir>]

Uses rsync to syncronize files between my desktop and laptop.

Options:
  -h: help
  -r: Transfer from laptop to desktop.
  -f: Really sync files. the default is to perform a dry run.
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
if [ ! $1 ]; then
    echo "$usage"
    exit 1
fi
DIR=$(pwd)/${1%%/}
if [ ! -d ${DIR} ]; then
    echo "${DIR} is not a directory!"
    exit 2
fi
DIR=${DIR##/home/${USER}/}
OPTS='-avn'
if [ $FORCE ]; then
    OPTS='-av'
fi
if [ $REVERSE ]; then
    rsync ${OPTS} --delete rfs::home/${USER}/${DIR}/ /home/${USER}/${DIR}
else
    rsync ${OPTS} --delete /home/${USER}/${DIR}/ rfs::home/${USER}/${DIR}
fi

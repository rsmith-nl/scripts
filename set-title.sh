#!/bin/sh
# file: set-title.sh
# vim:fileencoding=utf-8:ft=sh
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2014-11-16T02:22:35+0100
# Last modified: 2021-02-28T20:48:16+0100

set -e

VAR=`hostname`
if [ $1 ]; then
    VAR=$1
fi
printf "\033]2;${VAR}\007"

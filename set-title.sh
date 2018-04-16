#!/bin/sh
# file: set-title.sh
# vim:fileencoding=utf-8:fdm=marker:ft=sh
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2014-11-16T02:22:35+0100
# Last modified: 2018-04-16T22:34:04+0200

VAR=`hostname`
if [ $1 ]; then
    VAR=$1
fi
printf "\033]2;${VAR}\007"

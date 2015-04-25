#!/bin/sh
# vim:fileencoding=utf-8
# file: set-title.sh
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-11-16 02:22:35 +0100
# $Date$
# $Revision$
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to set-title.sh. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

VAR=`hostname`
if [ $1 ]; then
    VAR=$1
fi
printf "\033]2;${VAR}\007"

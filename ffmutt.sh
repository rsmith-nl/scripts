#!/bin/sh
# file: ffmutt.sh
# vim:fileencoding=utf-8:fdm=marker:ft=sh
#
# Copyright © 2015-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-05-08T22:12:45+02:00
# Last modified: 2018-04-16T21:55:39+0200
exec urxvt -e sh -c "mutt $$@"

#!/bin/sh
# Lauch Mutt for a mailto link.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-12-26 22:49:16 +0100
# Last modified: 2016-03-19 10:26:24 +0100
exec urxvt -e sh -c "mutt $$@"

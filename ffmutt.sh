#!/bin/sh
# file: ffmutt
# vim:fileencoding=utf-8:ft=sh
# Lauch Mutt for a mailto link.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-12-26 22:49:16 +0100
# $Date$
# $Revision$
exec urxvt -e sh -c "mutt $$@"

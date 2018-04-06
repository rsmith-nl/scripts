#!/usr/bin/env python3
# file: osversion.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2018-04-06 22:34:00 +0200
# Last modified: 2018-04-06 22:39:44 +0200

from ctypes import CDLL

with open('/usr/include/osreldate.h') as h:
    lines = h.readlines()
line = [ln for ln in lines if ln.startswith('#define')][0]
print('Compilation environment release date:', line.split()[-1])

libc = CDLL("/lib/libc.so.7")
print('Execution environment release date:', libc.getosreldate())

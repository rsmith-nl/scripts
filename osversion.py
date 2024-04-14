#!/usr/bin/env python
# file: osversion.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2018-04-06 22:34:00 +0200
# Last modified: 2018-08-19T14:18:16+0200
"""Print the __FreeBSD_version. This is also called OSVERSION in scripts."""

from ctypes import CDLL
import sys

if "freebsd" not in sys.platform:
    print("This script only works on FreeBSD!")
    sys.exit(1)

with open("/usr/include/osreldate.h") as h:
    lines = h.readlines()
line = [ln for ln in lines if ln.startswith("#define")][0]
print("Compilation environment version:", line.split()[-1])

libc = CDLL("/lib/libc.so.7")
print("Execution environment version:", libc.getosreldate())

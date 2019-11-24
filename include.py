#!/usr/bin/env python3
# file: include.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2019-11-24T14:37:36+0100
# Last modified: 2019-11-24T15:02:01+0100
"""Convert files to a format that can be included into a Python script."""

import base64
import os
import sys


def to_include(path):
    linelen = 74
    with open(path, 'rb') as img:
        data = base64.b85encode(img.read()).decode('ascii')
    i = 0
    print('# ' + path)
    print('data = base64.b85decode(')
    while i < len(data):
        print("    '" + data[i:i+linelen] + "'")
        i += linelen
    print(")" + os.linesep)


if __name__ == '__main__':
    for fn in sys.argv[1:]:
        to_include(fn)

# file: py-include.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-03-25T23:20:47+0100
# Last modified: 2020-03-27T18:45:39+0100
"""Program to prepare files for inclusion in Python code."""

import argparse
import base64
import os
import sys
import zlib

__version__ = '0.1'


def main(argv):
    opts = argparse.ArgumentParser(prog='open', description=__doc__)
    opts.add_argument('-v', '--version', action='version', version=__version__)
    opts.add_argument(
        '-c', '--compress', action='store_true', default=False,
        help='compress files before encoding (off by default)'
    )
    opts.add_argument(
        '-t', '--text', action='store_true', default=False,
        help='decode the file into text (off by default)'
    )
    opts.add_argument(
        "files", metavar='file', nargs='*', help="one or more files to process"
    )
    args = opts.parse_args(argv)
    codec = None
    if args.text:
        codec = 'utf-8'
    for path in args.files:
        print(to_include(path, args.compress, codec))


def to_include(path, compress=False, decode=None):
    """Reads a file and produces an encoded image of the file as Python source code.

    Arguments:
        path (str): Path of the file to process.
        compress (bool): If True, compress the file before encoding.
        decode (str): If not None, de codec for decoding the bytes

    Returns:
        The file as a piece of Python code to reproduce its contents.
    """
    linelen = 74
    with open(path, 'rb') as img:
        data = img.read()
    if compress:
        data = zlib.compress(data, level=9)
    data = base64.b85encode(data).decode('ascii')
    i = 0
    lines = ['# ' + path]
    if compress:
        lines.append('data = zlib.decompress(base64.b85decode(')
        end = '))'
    else:
        lines.append('data = base64.b85decode(')
        end = ')'
    while i < len(data):
        lines.append("    '" + data[i:i+linelen] + "'")
        i += linelen
    if decode:
        lines.append(end + f'.decode("{decode}")' + os.linesep)
    else:
        lines.append(end + os.linesep)
    return os.linesep.join(lines)


if __name__ == '__main__':
    main(sys.argv[1:])

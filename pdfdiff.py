# file: pdfdiff.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2019-07-11T00:22:30+0200
# Last modified: 2019-07-11T22:17:12+0200
"""
Script to try and show a diff between two PDF files.

Requires pdftotext from the poppler utilities,
and a diff that supports the -w option to ignore whitespace.
"""

from enum import IntEnum
import binascii
import os
import subprocess as sp
import sys


class Color(IntEnum):
    """Standard ANSI colors."""

    black = 0
    red = 1
    green = 2
    yellow = 3
    blue = 4
    magenta = 5
    cyan = 6
    white = 7


def pdftotext(path):
    """
    Generate a text rendering of a PDF file in the form of a list of lines.
    """
    args = ['pdftotext', '-layout', path, '-']
    result = sp.run(args, capture_output=True)
    return result.stdout.decode('utf-8')


def ansiprint(s, fg='', bg='', i=False):
    """
    Print a colored text with ansi escape sequences.

    Arguments
        fg: Optional foreground color.
        bg: Optional background color.
        i: Boolean to indicate intense colors (default False)
    """
    esc = '\033[{:d}{}m'
    iv = ''
    if i:
        iv = ";1"
    if fg != '':
        fg = esc.format(30 + fg, iv)
    if bg != '':
        bg = esc.format(40 + bg, iv)
    print(''.join([fg, bg, s, esc.format(0, '')]))


def colordiff(txt):
    """
    Print a colored diff.

    Arguments:
        txt: diff list or generator to print
    """
    for line in txt:
        line = line.rstrip()
        if line.startswith(('+++ ', '--- ')):
            ansiprint(line, fg=Color.yellow, i=True)
            continue
        if line.startswith('+'):
            ansiprint(line, fg=Color.green, i=True)
            continue
        if line.startswith('-'):
            ansiprint(line, fg=Color.red, i=True)
            continue
        if line.startswith('@@'):
            ansiprint(line, fg=Color.magenta, i=True)
            continue
        print(line)


def main(argv):
    """
    Entry point for pdfdiff.py.

    Arguments:
        argv: command line arguments
    """
    if len(argv) != 2:
        print('Usage: pdfdiff.py first second')
        sys.exit(1)
    tmpnam = []
    for j in range(2):
        tmpnam.append(binascii.hexlify(os.urandom(10)).decode('ascii') + '.txt')
        with open(tmpnam[j], 'w') as f:
            f.write(pdftotext(argv[j]))
    diffargs = ['diff', '-d', '-u', '-w'] + tmpnam
    print("DEBUG: diffargs = ", diffargs)
    result = sp.run(diffargs, capture_output=True)
    lines = result.stdout.decode('utf-8').splitlines()
    os.remove(tmpnam[0])
    os.remove(tmpnam[1])
    lines[0] = lines[0].replace(tmpnam[0], argv[0])
    lines[1] = lines[1].replace(tmpnam[1], argv[1])
    colordiff(lines)


if __name__ == '__main__':
    main(sys.argv[1:])

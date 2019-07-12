# file: pdfdiff.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2019-07-11T00:22:30+0200
# Last modified: 2019-07-12T20:47:58+0200
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


def brightprint(s, fg=None):
    """
    Print a text with bright foreground color using ansi escape sequences.

    Arguments
        s (str): Text to print.
        fg (int): Optional foreground color.
    """
    print(f'\033[{30+fg};1m' if fg else '', s, '\033[0m')


def colordiff(txt):
    """
    Print a colored diff.

    Arguments:
        txt: diff list or generator to print
    """
    for line in txt:
        line = line.rstrip()
        if line.startswith(('+++ ', '--- ')):
            brightprint(line, fg=Color.yellow)
            continue
        if line.startswith('+'):
            brightprint(line, fg=Color.green)
            continue
        if line.startswith('-'):
            brightprint(line, fg=Color.red)
            continue
        if line.startswith('@@'):
            brightprint(line, fg=Color.magenta)
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
    result = sp.run(diffargs, capture_output=True)
    lines = result.stdout.decode('utf-8').splitlines()
    os.remove(tmpnam[0])
    os.remove(tmpnam[1])
    lines[0] = lines[0].replace(tmpnam[0], argv[0])
    lines[1] = lines[1].replace(tmpnam[1], argv[1])
    try:
        colordiff(lines)
    except BrokenPipeError:
        pass


if __name__ == '__main__':
    main(sys.argv[1:])

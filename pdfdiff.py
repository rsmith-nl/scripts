# file: pdfdiff.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2019-07-11T00:22:30+0200
# Last modified: 2019-07-30T15:51:58+0200
"""
Script to try and show a diff between two PDF files.

Requires pdftotext from the poppler utilities,
and a diff that supports the -w option to ignore whitespace.
"""

from types import SimpleNamespace
import binascii
import os
import subprocess as sp
import sys

# Standard ANSI colors.
fgcolor = SimpleNamespace(
    brightred='\033[31;1m', brightgreen='\033[32;1m', brightyellow='\033[33;1m',
    brightmagenta='\033[35;1m', reset='\033[0m'
)


def pdftotext(path):
    """
    Generate a text rendering of a PDF file in the form of a list of lines.
    """
    args = ['pdftotext', '-layout', path, '-']
    result = sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL, check=True)
    return result.stdout.decode()


def colordiff(txt):
    """
    Print a colored diff.

    Arguments:
        txt: diff list or generator to print
    """
    for line in txt:
        line = line.rstrip()
        if line.startswith(('+++ ', '--- ')):
            print(fgcolor.brightyellow, line)
            continue
        if line.startswith('+'):
            print(fgcolor.brightgreen, line)
            continue
        if line.startswith('-'):
            print(fgcolor.brightred, line)
            continue
        if line.startswith('@@'):
            print(fgcolor.brightmagenta, line)
            continue
        print(fgcolor.reset, line)


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
    result = sp.run(diffargs, stdout=sp.PIPE, stderr=sp.DEVNULL, check=True)
    lines = result.stdout.decode().splitlines()
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

#!/usr/bin/env python3
# file: genotp.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2014-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2014-03-08T14:04:00+01:00
# Last modified: 2018-04-16T22:03:09+0200
"""
Generate an old-fashioned one-time pad.

The format of the one-time pad is:
65 lines of 12 groups of 5 random capital letters.
"""

from os import urandom


def main():
    """Entry point."""
    ident = '+++++ {} +++++'
    print(ident.format(rndcaps(10)))
    print(otp())


def otp(n=65):
    """
    Return a one-time pad.

    Arguments:
        n: number of lines in the key

    Returns:
        n lines of 12 groups of 5 random capital letters.
    """
    lines = []
    for num in range(1, n + 1):
        i = ['{:02d} '.format(num)]
        i += [rndcaps(5) for j in range(0, 12)]
        lines.append(' '.join(i))
    return '\n'.join(lines)


def rndcaps(n):
    """
    Generates a string of random capital letters.

    Arguments:
        n: Length of the output string.

    Returns:
        A string of n random capital letters.
    """
    b = urandom(n)
    return ''.join([chr(int(c / 9.808) + 65) for c in b])


if __name__ == '__main__':
    main()

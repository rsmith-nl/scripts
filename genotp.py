#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to genotp.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Generates a one-time pad."""

from __future__ import division, print_function
from os import urandom


def rndcaps(n):
    """Generates a string of n random capital letters."""
    b = urandom(n)
    return ''.join([chr(int(round(ord(c)/10.2))+65) for c in b])


if __name__ == '__main__':
    for num in range(1, 67):
        ls = ['{:02d} '.format(num)]
        cb = [rndcaps(5) for j in range(0, 12)]
        print(' '.join(ls+cb))

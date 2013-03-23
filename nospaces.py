#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to nospaces.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Rename files mentioned on the command line, removing spaces from
their names and replacing them with underscores."""

import os
import sys

def fixname(path):
    path = os.path.normpath(path)
    head, tail = os.path.split(path)
    tl = tail.split()
    tail = '_'.join(tl)
    return os.path.join(head, tail)

def main(argv):
    """Main program.

    Arguments:
    argv -- command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print("Usage: {} [file ...]".format(binary))
        sys.exit(0)
    del sys.argv[0] # delete the name of the script.
    for n in sys.argv:
        try:
            os.rename(n, fixname(n))
        except OSError as e:
            print('Renaming "{}" failed: {}'.format(n, e.strerror))

if __name__ == '__main__':
    main(sys.argv)

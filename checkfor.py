#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all
# copyright and related or neighboring rights to checkfor.py This work
# is published from the Netherlands. See
# http://creativecommons.org/publicdomain/zero/1.0/

import subprocess
import sys
import os

def checkfor(args, rv = 0):
    """Make sure that a program necessary for using this script is
    available.

    Arguments:
    args  -- string or list of strings of commands. A single string may
             not contain spaces.
    rv    -- expected return value from evoking the command.
    """
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('no spaces in single command allowed')
        args = [args]
    try:
        with open(os.devnull, 'w') as bb:
            rc = subprocess.call(args, stdout=bb, stderr=bb)
        if rc != rv:
            raise OSError
    except OSError as oops:
        outs = "Required program '{}' not found: {}."
        print outs.format(args[0], oops.strerror)
        sys.exit(1)

if __name__ == '__main__':
    for p in ['ls', 'foo']:
        checkfor(p)
        print 'found', p

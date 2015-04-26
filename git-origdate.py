#!/usr/bin/env python3
# file: git-origdate.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-01-03 15:48:13 +0100
# $Date$
# $Revision$
#
# To the extent possible under law, <rsmith@xs4all.nl> has waived all
# copyright and related or neighboring rights to git-origdate.py. This work is
# published from the Netherlands. See
# http://creativecommons.org/publicdomain/zero/1.0/

"""Find out for all command-line arguments when they were first checked in to
git."""

import os.path
import subprocess
import sys

__version__ = '$Revision$'[11:-2]


def main(argv):
    """Entry point for this script.

    :param argv: command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print("{} ver. {}".format(binary, __version__), file=sys.stderr)
        print("Usage: {} [file ...]".format(binary), file=sys.stderr)
        sys.exit(0)
    del argv[0]  # delete the name of the script.
    # Real work starts here.
    for fn in argv:
        args = ['git', 'log', '--diff-filter=A', '--format=%ai', '--', fn]
        try:
            date = subprocess.check_output(args, stderr=subprocess.PIPE)
            date = date.decode('utf-8').strip()
            print('{}: {}'.format(fn, date))
        except subprocess.CalledProcessError as e:
            if e.returncode == 128:
                print("Not a git repository! Exiting.")
            break


if __name__ == '__main__':
    main(sys.argv)

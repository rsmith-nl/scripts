#!/usr/bin/env python3
# file: lk.py
# vim:fileencoding=utf-8:ft=python:spelllang=en
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2016-10-08 21:07:58 +0200
# Last modified: 2017-01-29 10:49:44 +0100
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to lk.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/
"""
Lock down files or directories.

This makes files read-only for the owner and inaccessible for the group and
others. Then it sets the user immutable and user undeletable flag on the files.
For directories, it recursively treats the files as mentioned above. It then
sets the sets the directories to read/execute only for the owner and
inaccessible for the group and others. Then it sets the user immutable and
undeletable flag on the directories as well.

Using the -u flag unlocks the files or directories, making them writable for
the owner only.
"""

import argparse
import logging
import os
import sys
import stat

__version__ = '1.0.0'


def lock_path(root, name, mode):
    """Lock down a path"""
    flags = stat.UF_IMMUTABLE | stat.UF_NOUNLINK
    p = os.path.join(root, name)
    logging.info('locking path “{}”'.format(p))
    os.chmod(p, mode)
    os.chflags(p, flags)


def unlock_path(root, name, mode):
    flags = 0
    p = os.path.join(root, name)
    logging.info('unlocking path “{}”'.format(p))
    os.chflags(p, flags)
    os.chmod(p, mode)


def main(argv):  # noqa
    """
    Entry point for lck.py.

    Arguments:
        argv: command line arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-u', '--unlock', action='store_true',
                        help='unlock the files instead of locking them')
    parser.add_argument('--log', default='warning',
                        choices=['debug', 'info', 'warning', 'error'],
                        help="logging level (defaults to 'warning')")
    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__)
    parser.add_argument('paths', nargs='*', metavar='path',
                        help='files or directories to work on')
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                        format='%(levelname)s: %(message)s')
    logging.debug('Command line arguments = {}'.format(argv))
    logging.debug('Parsed arguments = {}'.format(args))
    if not args.paths:
        parser.print_help()
        sys.exit(0)
    fmod = stat.S_IRUSR
    dmod = stat.S_IRUSR | stat.S_IXUSR
    action = lock_path
    if args.unlock:
        logging.info('unlocking files')
        fmod = stat.S_IRUSR | stat.S_IWUSR
        dmod = stat.S_IRWXU
        action = unlock_path
    for p in args.paths:
        if os.path.isfile(p):
            action('', p, fmod)
        elif os.path.isdir(p):
            if args.unlock:
                action('', p, dmod)
            for root, dirs, files in os.walk(p, topdown=False):
                for fn in files:
                    action(root, fn, fmod)
                for d in dirs:
                    action(root, d, dmod)
            if not args.unlock:
                action('', p, dmod)


if __name__ == '__main__':
    main(sys.argv[1:])

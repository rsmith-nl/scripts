#!/usr/bin/env python3
# file: find-pkg-updates.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2017-11-26 13:19:00 +0100
# Last modified: 2017-11-26 14:34:40 +0100
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to find-pkg-updates.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/
"""Find updated packages for FreeBSD."""

import argparse
import concurrent.futures as cf
import re
import subprocess as sp
import sys
import time
import requests

__version__ = '1.0'


def get_remote_pkgs(version, arch):
    """Get a dict of the latest packages from the FreeBSD repo.

    Arguments:
        version: The FreeBSD major version number.
        arch: The CPU architecture for which packages are to be retrieved.
    """
    t = re.compile('href="(.*?)"', re.MULTILINE)
    ps = 'http://pkg.freebsd.org/FreeBSD:{:d}:{}/latest/All/'
    pkgpage = requests.get(ps.format(version, arch))
    data = [ln[:-4].rsplit('-', 1) for ln in t.findall(pkgpage.text)]
    return dict(ln for ln in data if len(ln) == 2)


def get_local_pkgs():
    """Get a list of local packages."""
    p = sp.run(['pkg', 'info', '-a', '-q'], stdout=sp.PIPE, stderr=sp.DEVNULL)
    return dict([ln.rsplit('-', 1) for ln in p.stdout.decode('utf-8').splitlines()])


def main(argv):
    """
    Entry point for find-pkg-updates.py.


    Arguments:
        argv: Command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-v', '--version', action='version', version=__version__)
    parser.add_argument(
        '-m',
        '--major',
        type=int,
        default=11,
        help='FreeBSD major version (default 11)')
    parser.add_argument(
        '-a',
        '--arch',
        type=str,
        default='amd64',
        help='FreeBSD architecture (default amd64)')
    args = parser.parse_args(argv)
    print('# Retrieving package lists')
    with cf.ProcessPoolExecutor(max_workers=2) as ex:
        remote = ex.submit(get_remote_pkgs, args.major, args.arch)
        local = ex.submit(get_local_pkgs)
        rd, ld = False, False
        while not (rd and ld):
            if remote.done() and not rd:
                rd = True
                print('# * Finished retrieving remote packages.')
            if local.done() and not ld:
                ld = True
                print('# * Finished retrieving local packages.')
            time.sleep(0.25)
        remotepkg = remote.result()
        localpkg = local.result()
    not_remote = []
    for name in localpkg.keys():
        if name in remotepkg:
            lv, rv = localpkg[name], remotepkg[name]
            if lv != rv:
                print('{}-{}: remote has {}'.format(name, lv, rv))
        else:
            not_remote.append(name)
    print('# Not in remote repo:')
    print('# ' + ' '.join(not_remote))


if __name__ == '__main__':
    main(sys.argv[1:])

#!/usr/bin/env python3
# file: find-pkg-upgrades.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2017-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2017-11-26T14:38:15+01:00
# Last modified: 2019-07-27T15:48:15+0200
"""Find newer packages for FreeBSD."""

from enum import Enum
from functools import partial
import argparse
import logging
import concurrent.futures as cf
import os
import re
import subprocess as sp
import sys
import time
import requests

__version__ = '2.0'


class Comparison(Enum):
    SAME = 0
    CHANGED = 1
    UNKNOWN = 2


class Check(Enum):
    UP_TO_DATE = 0
    REBUILD_SOURCE = 1
    NOT_IN_REMOTE = 2
    USE_PACKAGE = 3


def get_remote_pkgs(version, arch):
    """Get a dict of the latest packages from the FreeBSD repo.

    Arguments:
        version: The FreeBSD major version number.
        arch: The CPU architecture for which packages are to be retrieved.

    Returns:
        A dict of packages, indexed by package name and containing the version string.
    """
    t = re.compile('href="(.*?)"', re.MULTILINE)
    ps = 'http://pkg.freebsd.org/FreeBSD:{:d}:{}/latest/All/'
    pkgpage = requests.get(ps.format(version, arch))
    data = [ln[:-4].rsplit('-', 1) for ln in t.findall(pkgpage.text)]
    return dict(ln for ln in data if len(ln) == 2)


def run(args):
    """
    Run a subprocess and return the standard output.

    Arguments:
        args (list): List of argument strings. Typically a command name
            followed by options.

    Returns:
        Standard output of the program, converted to UTF-8 and split into lines.
    """
    if not isinstance(args, (list, tuple)):
        raise ValueError('args should be a list or tuple')
    if not all(isinstance(x, str) for x in args):
        raise ValueError('args should be a list or tuple of strings')
    comp = sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL)
    return comp.stdout.decode('utf-8').splitlines()


def uses_default_options(name, origin):
    """
    Check of a given package uses the default options or
    if options have been changed.

    Arguments:
        name (str): Name of the package.
        origin (str): Directory relative to /usr/ports from which the package was built.

    Returns:
        A Comparison
    """
    optionlines = run(['pkg', 'query', '%Ok %Ov', name])
    options_set = set(opt.split()[0] for opt in optionlines if opt.endswith('on'))
    try:
        os.chdir(f'/usr/ports/{origin}')
    except FileNotFoundError:
        return Comparison.UNKNOWN
    default = run(['make', '-V', 'OPTIONS_DEFAULT'])
    if not default[0]:
        return Comparison.SAME
    options_default = set(default[0].split())
    if options_default == options_set:
        v = Comparison.SAME
    else:
        v = Comparison.CHANGED
    return v


def get_local_pkgs():
    """Get a list of local packages.

    Returns:
        A list of (name, version, origin) tuples.
    """
    lines = run(['pkg', 'info', '-a', '-o'])
    rv = []
    for ln in lines:
        pkg, origin = ln.split()
        name, ver = pkg.rsplit('-', 1)
        rv.append((name, ver, origin))
    return rv


def pkgver_decode(versionstring):
    """Decode a package version into prefix and suffix version."""
    factor = 100
    if '_' in versionstring:
        prefixstring, suffixstring = versionstring.split('_', maxsplit=1)
        try:
            suffix = [int(n) for n in suffixstring.split(',')]
            snum = 0
            for n in suffix:
                snum = factor * snum + n
        except ValueError:
            snum = suffixstring
    else:
        prefixstring = versionstring
        suffixstring = None
        snum = 0
    try:
        prefix = [int(n) for n in prefixstring.split('.')]
        pnum = 0
        for n in prefix:
            pnum = factor * pnum + n
    except ValueError:
        pnum = prefixstring
    return (pnum, snum)


def remote_is_newer(local, remote):
    """Return True if the remote version is later than the local version.

    Arguments:
        local: Local package version, e.g. '4.0.1_4'
        remote: Remote package version.

    Returns:
        True if the remote version is larger than the local version.
    """
    localprefix, localsuffix = pkgver_decode(local)
    remoteprefix, remotesuffix = pkgver_decode(remote)
    try:
        if remoteprefix > localprefix:
            return True
        elif remoteprefix == localprefix and remotesuffix > localsuffix:
            return True
        return False
    except TypeError:  # Comparing str and int doesn't work.
        return True


def checkpkg(localpkg, remotepkg):
    """Worker function to check the status of a local package."""
    name, version, origin = localpkg
    if name in remotepkg:
        c = uses_default_options(name, origin)
        if remote_is_newer(version, remotepkg[name]):
            if c == Comparison.SAME:
                return (name, Check.USE_PACKAGE)
            else:
                return (name, Check.REBUILD_SOURCE)
        else:
            return (name, Check.UP_TO_DATE)
    return (name, Check.NOT_IN_REMOTE)


def main(argv):
    """
    Entry point for find-pkg-upgrades.py.


    Arguments:
        argv: Command line arguments.
    """
    cp = sp.run(['uname', '-p', '-U'], stdout=sp.PIPE, stderr=sp.DEVNULL, text=True)
    uname = cp.stdout.split()
    major = int(uname[1][:2])
    arch = uname[0]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument(
        '-m',
        '--major',
        type=int,
        default=major,
        help=f'FreeBSD major version (default {major})'
    )
    parser.add_argument(
        '-a',
        '--arch',
        type=str,
        default=arch,
        help=f'FreeBSD architecture (default {arch})'
    )
    parser.add_argument(
        '--log',
        default='info',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'info')"
    )
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None), format='%(levelname)s: %(message)s'
    )
    parser.parse_args(argv)
    if major == args.major:
        extra = '(detected)'
    else:
        extra = '(override)'
    logging.info(f'FreeBSD major version: {args.major} {extra}')
    if arch == args.arch:
        extra = '(detected)'
    else:
        extra = '(override)'
    logging.info(f'FreeBSD processor architecture: {args.arch} {extra}')
    logging.info('retrieving local and remote package lists')
    # I'm using concurrent.futures here because especially get_remote_pkgs
    # can take a long time. This way we can reduce the time as much as possible.
    with cf.ProcessPoolExecutor(max_workers=2) as ex:
        remote = ex.submit(get_remote_pkgs, args.major, args.arch)
        local = ex.submit(get_local_pkgs)
        rd, ld = False, False
        while not (rd and ld):
            if remote.done() and not rd:
                rd = True
                logging.info('finished retrieving remote packages.')
            if local.done() and not ld:
                ld = True
                logging.info('finished retrieving local packages.')
            time.sleep(0.25)
        remotepkg = remote.result()
        logging.debug('{len(remotepkg)} remote packages')
        localpkg = local.result()
    choose = {Check.UP_TO_DATE: [], Check.REBUILD_SOURCE: [],
              Check.NOT_IN_REMOTE: [], Check.USE_PACKAGE: []}
    with cf.ProcessPoolExecutor(max_workers=4) as chk:
        total = len(localpkg)
        i = 1
        logging.info('checking packages')
        for name, result in chk.map(partial(checkpkg, remotepkg=remotepkg), localpkg):
            print(f'\r{i:3d}/{total:3d}', end='', flush=True)
            i += 1
            choose[result].append(name)
    print()
    if choose[Check.USE_PACKAGE]:
        logging.info('Upgrade from packages:')
        print(' '.join(choose[Check.USE_PACKAGE]))
    else:
        print('No packages to upgrade!')
    logging.info('the following should be rebuilt from source (non-default options):')
    logging.info(' '.join(choose[Check.REBUILD_SOURCE]))
    logging.info('not found in remote repo:')
    logging.info(' '.join(choose[Check.NOT_IN_REMOTE]))


if __name__ == '__main__':
    main(sys.argv[1:])

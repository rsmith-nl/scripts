#!/usr/bin/env python3
# file: find-pkg-updates.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2017-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2017-11-26T14:38:15+01:00
# Last modified: 2018-05-06T15:35:14+0200
"""Find updated packages for FreeBSD.



"""

from enum import Enum
import argparse
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
    comp = sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL)
    return comp.stdout.decode('utf-8').splitlines()


def check_options(pkgdata):
    """
    Check of a given package uses the default options or
    if options have been changed.

    Arguments:
        pkgdata (tuple): (name, version, origin)

    Returns:
        A tuple (name, version, origin, Comparison)
    """
    name, version, origin = pkgdata
    optionlines = run(['pkg', 'query', '%Ok %Ov', name])
    options_set = set(opt.split()[0] for opt in optionlines if opt.endswith('on'))
    try:
        os.chdir('/usr/ports/{}'.format(origin))
    except FileNotFoundError:
        return (name, version, origin, Comparison.UNKNOWN)
    default = run(['make', '-V', 'OPTIONS_DEFAULT'])
    if not default[0]:
        return (name, version, origin, Comparison.SAME)
    options_default = set(default[0].split())
    if options_default == options_set:
        v = Comparison.SAME
    else:
        v = Comparison.CHANGED
    return (name, version, origin, v)


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


def compare(local, remote):
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


def main(argv):
    """
    Entry point for find-pkg-updates.py.


    Arguments:
        argv: Command line arguments.
    """
    uname = sp.check_output(['uname', '-p', '-U']).decode('ascii').split()
    major = int(uname[1][:2])
    arch = uname[0]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument(
        '-m',
        '--major',
        type=int,
        default=major,
        help='FreeBSD major version (default {})'.format(major)
    )
    parser.add_argument(
        '-a',
        '--arch',
        type=str,
        default=arch,
        help='FreeBSD architecture (default {})'.format(arch)
    )
    args = parser.parse_args(argv)
    parser.parse_args(argv)
    if major == args.major:
        extra = '(detected)'
    else:
        extra = '(override)'
    print('# FreeBSD major version: {} {}'.format(args.major, extra))
    if arch == args.arch:
        extra = '(detected)'
    else:
        extra = '(override)'
    print('# FreeBSD processor architecture: {} {}'.format(args.arch, extra))
    print('# Retrieving local and remote package lists')
    # I'm using concurrent.futures here because especially get_remote_pkgs
    # can take a long time. This way we can reduce the time as much as possible.
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
    print('# Checking options on local packages')
    with cf.ThreadPoolExecutor() as ex:
        localpkg = ex.map(check_options, localpkg)
    print('# * Finished checking options on local packages.')
    not_remote = []
    for name, version, _, default_options in localpkg:
        if name in remotepkg:
            rv = remotepkg[name]
            if default_options == Comparison.SAME and compare(version, rv):
                print('{}-{}: remote has {}'.format(name, version, rv))
        else:
            not_remote.append(name)
    print('# Not in remote repo:')
    print('# ' + ' '.join(not_remote))


if __name__ == '__main__':
    main(sys.argv[1:])

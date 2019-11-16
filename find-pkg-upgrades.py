#!/usr/bin/env python3
# file: find-pkg-upgrades.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2017-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2017-11-26T14:38:15+01:00
# Last modified: 2019-11-16T10:48:58+0100
"""Find newer packages and ports for FreeBSD.

Using this program requires that the doas 'doas' and ‘pkg’ ports are
installed. The ‘doas’ port should be set up to allow ‘pkg version -R’
to be run as root.
"""

import argparse
import logging
import concurrent.futures as cf
import os
import re
import subprocess as sp
import sys
import requests

__version__ = '3.0'


def main(argv):
    """
    Entry point for find-pkg-upgrades.py.


    Arguments:
        argv: Command line arguments.
    """
    configure(argv)
    # I'm using concurrent.futures here because the functions can take a long time.
    # This way we can reduce the time as much as possible.
    with cf.ProcessPoolExecutor(max_workers=3) as ex:
        logging.info('retrieving remote package updates')
        remote = ex.submit(pkg_version_R)
        logging.info('retrieving local ports tree updates')
        local = ex.submit(pkg_version)
        for fut in cf.as_completed([remote, local]):
            if fut == remote:
                rpkgs, rports, rlen = remote.result()
                logging.info(f'finished scan of {rlen} remote packages')
            else:
                lpkgs, lports, llen = local.result()
                logging.info(f'finished scan of {llen} local packages')
    if rpkgs:
        print('# The following ports can be updated from packages:')
        print(' '.join(rpkgs))
    if lpkgs:
        print('# The following ports will have new packages in the future:')
        print(' '.join(lpkgs))
    if rports:
        print('# The following ports have new packages, but we use non-default options:')
        print(' '.join(rports))
    if lports:
        print('# The following must be updated from ports; non-default options:')
        print(' '.join(lports))


def configure(argv):
    """Configure the application at start-up."""
    # Get FreeBSD major version and architecture.
    cp = sp.run(['uname', '-p', '-U'], stdout=sp.PIPE, stderr=sp.DEVNULL, text=True)
    uname = cp.stdout.split()
    major = int(uname[1][:2])
    arch = uname[0]
    # Set standard output to flush after every line
    sys.stdout.reconfigure(line_buffering=True)
    # Process the command-line arguments.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument(
        '--log',
        default='info',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'info')"
    )
    args = parser.parse_args(argv)
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format='%(levelname)s: %(message)s'
    )
    # Look for required programs.
    try:
        for prog in ('pkg', 'make', 'doas', 'uname'):
            sp.run([prog], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            logging.debug(f'found “{prog}”')
    except FileNotFoundError:
        logging.error('required program “{prog}” not found')
        sys.exit(1)
    # Print info for the user.
    logging.info(f'FreeBSD major version: {major}')
    logging.info(f'FreeBSD processor architecture: {arch}')


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
    comp = sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL, text=True)
    return comp.stdout.splitlines()


def pkg_version():
    """Retrieve ports that have local updates."""
    data = [ln.strip().split() for ln in run(['pkg', 'version'])]
    local = [name.rsplit('-', maxsplit=1)[0]
             for name, state in data if state == '<']
    # These updates might be available in the future.
    pkgs = [name for name in local if uses_default_options(name)]
    # Newer portd, non-default options. These must be updated as ports.
    ports = sorted(list(set(local) - set(pkgs)))
    return pkgs, ports, len(data)


def pkg_version_R():
    """Retrieve packages that have remote updates."""
    data = [ln.strip().split() for ln in run(['doas', 'pkg', 'version', '-R'])]
    data = [item for item in data if len(item) == 2]
    remote = sorted(
        [name.rsplit('-', maxsplit=1)[0] for name, state in data if state == '<']
    )
    # These packages can be updated.
    pkgs = [name for name in remote if uses_default_options(name)]
    # These ports have newer packages, but we don't use default options.
    ports = sorted(list(set(remote) - set(pkgs)))
    return pkgs, ports, len(data)


def uses_default_options(name):
    """
    Check of a given package uses the default options or
    if options have been changed.

    Arguments:
        name (str): Name of the package.

    Returns:
        A Comparison
    """
    optionlines = run(['pkg', 'query', '%Ok %Ov', name])
    options_set = set(opt.split()[0] for opt in optionlines if opt.endswith('on'))
    try:
        origin = run(['pkg', 'query', '%o', name])[0]
        os.chdir(f'/usr/ports/{origin}')
    except (FileNotFoundError, IndexError):
        return False
    default = run(['make', '-V', 'OPTIONS_DEFAULT'])
    if not default[0]:
        return True
    options_default = set(default[0].split())
    if options_default == options_set:
        v = True
    else:
        v = False
    return v


if __name__ == '__main__':
    main(sys.argv[1:])

#!/usr/bin/env python3
# file: find-pkg-upgrades.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2017-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2017-11-26T14:38:15+01:00
# Last modified: 2020-06-19T13:25:52+0200
"""Find newer packages and ports for FreeBSD.

Using this program requires that the doas 'doas' and ‘pkg’ ports are
installed. The ‘doas’ port should be set up to allow ‘pkg version -R’
to be run as root.
"""

import argparse
import logging
import concurrent.futures as cf
import os
import subprocess as sp
import sys

__version__ = '4.0'


def main():
    """
    Entry point for find-pkg-upgrades.py.
    """
    major, arch = setup()
    # I'm using concurrent.futures here because the functions can take a long time.
    # This way we can reduce the time as much as possible.
    with cf.ProcessPoolExecutor() as ex:
        logging.info('starting retrieval of remote packages')
        remote_packages_f = ex.submit(pkg_version_R)
        logging.info('starting gathering package options')
        options_f = ex.submit(pkg_query)
        logging.info('starting gathering default port options')
        default_f = ex.submit(get_default_options)
        logging.info('starting gathering of ports with local updates')
        local_updates_f = ex.submit(pkg_version)
        for fut in cf.as_completed(
            [options_f, local_updates_f, remote_packages_f, default_f]
        ):
            if fut == options_f:
                local_options = fut.result()
                k = len(local_options)
                logging.info(f'finished gathering {k} package options')
            elif fut == local_updates_f:
                local_updates = fut.result()
                k = len(local_updates)
                logging.info(f'finished gathering {k} ports with local updates')
            elif fut == default_f:
                default_options = fut.result()
                k = len(default_options)
                logging.info(f'finished gathering {k} default port options')
            elif fut == remote_packages_f:
                remote_packages = fut.result()
                k = len(remote_packages)
                logging.info(f'finished retrieving {k} remote packages.')
    if remote_packages:
        rpkgs = [
            p for p in remote_packages
            if local_options.get(p, '') == default_options.get(p, '')
        ]
        print('# The following ports can be updated from packages:')
        print(' '.join(rpkgs))
        print('# The following ports have new packages, but we use non-default options:')
        print(' '.join(p for p in remote_packages if p not in rpkgs))
    if local_updates:
        lpkgs = [
            p for p in local_updates
            if local_options.get(p, '') == default_options.get(p, '')
        ]
        print('# The following ports will have new packages in the future:')
        print(' '.join(lpkgs))
        print('# The following must be updated from ports; non-default options:')
        print(' '.join(p for p in local_updates if p not in lpkgs))


def setup():
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
    args = parser.parse_args(sys.argv[1:])
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
    return (major, arch)


def run(args):
    """
    Run a subprocess and return the standard output split into lines.

    Arguments:
        args (list): List of argument strings. Typically a command name
            followed by options.

    Returns:
        Standard output of the program, converted to UTF-8 and split into lines.
    """
    comp = sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL, text=True)
    return comp.stdout.splitlines()


def pkg_query():
    """Retrieve all set package options.

    Returns:
        A dict indexed by package name that contains a sorted string of all
        the locally set package options.
    """
    data = [ln.split() for ln in run(['pkg', 'query', '%n %Ok %Ov'])]
    names = sorted(set(ln[0] for ln in data))
    opts = {n: [] for n in names}
    for name, option, value in data:
        if value == 'on':
            opts[name].append(option)
    res = {k: ' '.join(sorted(v)) for k, v in opts.items() if v}
    return res


def pkg_version():
    """Retrieve package names that have local updates."""
    data = [ln.strip().split() for ln in run(['pkg', 'version'])]
    local = sorted(
        name.rsplit('-', maxsplit=1)[0] for name, state in data if state == '<'
    )
    return local


def pkg_version_R():
    """Retrieve package names that have remote updates."""
    data = [ln.strip().split() for ln in run(['doas', 'pkg', 'version', '-R'])]
    data = [item for item in data if len(item) == 2]
    remote = sorted(
        [name.rsplit('-', maxsplit=1)[0] for name, state in data if state == '<']
    )
    return remote


def get_default_options():
    """
    Retrieve the default options for installed ports/packages.

    Returns:
        A dict indexed by package name that contains a sorted string of all
        the default port options.
    """
    query = run(['pkg', 'query', '%n %o'])
    res = {}
    for data in query:
        name, path = data.split()
        try:
            os.chdir(f'/usr/ports/{path}')
            cp = sp.run(['make', '-V', 'OPTIONS_DEFAULT'], stdout=sp.PIPE, text=True)
            v = cp.stdout.strip()
            if v:
                res[name] = v
        except FileNotFoundError:
            res[name] = ''
    return res


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# file: git-check-all.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2012-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2012-09-02T17:45:51+02:00
# Last modified: 2019-07-27T16:00:59+0200
"""
Run ``git gc`` on all the user's git repositories.

Find all directories in the user's home directory that are managed with
git, and run ``git gc`` on them unless they have uncommitted changes.
"""

import argparse
import os
import subprocess as sp
import sys
import logging


def main(argv):
    """
    Entry point of git-check-all.

    Arguments:
        argv: Command line arguments minus the program name.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--log',
        default='info',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'info')"
    )
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format='%(levelname)s: %(message)s'
    )
    logging.debug(f'Command line arguments = {argv}')
    logging.debug(f'Parsed arguments = {args}')
    checkfor(['git', '--version'])
    for (dirpath, dirnames, filenames) in os.walk(os.environ['HOME']):
        if '.git' in dirnames:
            runchecks(dirpath, args.verbose)


def checkfor(args, rv=0):
    """
    Ensure that a program necessary for using this script is available.

    If the required utility is not found, this function will exit the program.

    Arguments:
        args: String or list of strings of commands. A single string may not
            contain spaces.
        rv: Expected return value from evoking the command.
    """
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('no spaces in single command allowed')
        args = [args]
    else:
        if not isinstance(args, (list, tuple)):
            raise ValueError('args should be a list or tuple')
        if not all(isinstance(x, str) for x in args):
            raise ValueError('args should be a list or tuple of strings')
    try:
        cp = sp.run(args)
    except FileNotFoundError as oops:
        logging.error(f'required program "{args[0]}" not found: {oops.strerror}.')
        sys.exit(1)
    if cp.returncode != rv:
        logging.error(f'returncode {cp.returncode} should be {rv}')
        sys.exit(1)
    logging.info(f'found required program "{args[0]}"')


def runchecks(d, verbose=False):
    """
    Run git checks in the specified directory.

    If the repository is clean, do a ligth-weight garbage collection run on it.

    Arguments:
        d: Directory to run the checks in.
        verbose: Boolean to enable verbose messages.
    """
    os.chdir(d)
    outp = gitcmd('status', True)
    if 'clean' not in outp:
        logging.info(f"'{d}' is not clean, skipping.")
        return
    if verbose:
        logging.info(f"Running check on '{d}'")
    rv = gitcmd(['gc', '--auto', '--quiet'])
    if rv:
        print(f"git gc failed on '{d}'!")


def gitcmd(cmds, output=False):
    """
    Run the specified git subcommand.

    Arguments:
        cmds: command string or list of strings of command and arguments.
        output: flag to specify if the output should be captured and
            returned, or just the return value.

    Returns:
        The return value or the output of the git command.
    """
    if isinstance(cmds, str):
        if ' ' in cmds:
            raise ValueError('No spaces in single command allowed.')
        cmds = [cmds]
    else:
        if not isinstance(cmds, (list, tuple)):
            raise ValueError('args should be a list or tuple')
        if not all(isinstance(x, str) for x in cmds):
            raise ValueError('args should be a list or tuple of strings')
    cmds = ['git'] + cmds
    if output:
        cp = sp.run(cmds, stdout=sp.PIPE, stderr=sp.STDOUT, text=True)
        return cp.stdout
    else:
        cp = sp.run(cmds)
    return cp.returncode


if __name__ == '__main__':
    main(sys.argv[1:])

#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-05-14 22:30:11 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to <script>. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Find all directories in the user's home directory that are managed with
git, and run ``git gc`` on them unless they have uncommitted changes."""

import os
import subprocess
import sys


def main(args):
    """Entry point of git-check-all.

    Arguments:
        args: Command line arguments minus the program name.
    """
    checkfor(['git', '--version'])
    verbose = False
    if '-v' in args:
        verbose = True
    for (dirpath, dirnames, filenames) in os.walk(os.environ['HOME']):
        if '.git' in dirnames:
            runchecks(dirpath, verbose)


def checkfor(args, rv=0):
    """
    Make sure that a program necessary for using this script is available.
    If not, it terminates the program by calling sys.exit.

    Arguments:
        args: String or list of strings of commands. A single string may
            not contain spaces.
        rv: Expected return value from evoking the command.
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
        print(outs.format(args[0], oops.strerror))
        sys.exit(1)


def runchecks(d, verbose=False):
    """
    Run git checks in the specified directory. If the repository is
    clean, do a ligth-weight garbage collection run on it.

    Arguments:
        d: Directory to run the checks in.
        verbose: Boolean to enable verbose messages.
    """
    os.chdir(d)
    outp = gitcmd('status', True)
    if 'clean' not in outp:
        print("'{}' is not clean, skipping.".format(d))
        return
    if verbose:
        print("Running check on '{}'".format(d))
    rv = gitcmd(['gc', '--auto', '--quiet'])
    if rv:
        print("git gc failed on '{}'!".format(d))


def gitcmd(cmds, output=False):
    """Run the specified git command.

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
    cmds = ['git'] + cmds
    if output:
        rv = subprocess.check_output(cmds, stderr=subprocess.STDOUT).decode()
    else:
        with open(os.devnull, 'w') as bb:
            rv = subprocess.call(cmds, stdout=bb, stderr=bb)
    return rv


if __name__ == '__main__':
    main(sys.argv[1:])

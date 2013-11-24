#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to <script>. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Find all directories that are managed with git, and check them
unless they have uncommitted changes."""

import os
import sys
import subprocess


def checkfor(args, rv=0):
    """Make sure that a program necessary for using this script is
    available.

    :param args: String or list of strings of commands. A single string may
    not contain spaces.
    :param rv: Expected return value from evoking the command.
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


def gitcmd(cmds, output=False):
    """Run the specified git command.

    Arguments:
    cmds   -- command string or list of strings of command and arguments
    output -- wether the output should be captured and returned, or
              just the return value
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


def runchecks(d):
    """Run git checks in the specified directory. If the repository is
    clean, do a ligth-weight garbage collection run on it.

    Arguments:
    d -- directory to run the checks in.
    """
    os.chdir(d)
    outp = gitcmd('status', True)
    if not 'clean' in outp:
        print("'{}' is not clean, skipping.".format(d))
        return
    rv = gitcmd(['gc', '--auto', '--quiet'])
    if rv:
        print("git gc failed on '{}'!".format(d))


def main():
    """Main program."""
    #pylint: disable=W0612
    checkfor(['git', '--version'])
    for (dirpath, dirnames, filenames) in os.walk(os.environ['HOME']):
        if '.git' in dirnames:
            runchecks(dirpath)


if __name__ == '__main__':
    main()

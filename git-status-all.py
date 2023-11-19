#!/usr/bin/env python
# file: git-check-all.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2022 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2022-01-22T17:36:02+0100
# Last modified: 2023-11-19T22:00:58+0100
"""
Run ``git status`` on all the user's git repositories under the current
working directory.

Report repositories that have uncommitted changes or that are ahead of their remote.
"""

import argparse
import os
import subprocess as sp
import sys
import logging


def main():
    """
    Entry point of git-status-all.
    """
    args = setup()
    if not args.directories:
        args.directories = [""]
    cwd = os.getcwd() + os.sep
    args.directories = [
        d if d.startswith(os.sep) else cwd + d for d in args.directories
    ]
    for d in args.directories:
        for (dirpath, dirnames, filenames) in os.walk(d):
            if any(w in dirpath for w in args.ignore):
                continue
            if ".git" in dirnames:
                runstatus(dirpath, args.verbose)


def setup():
    """Parse command-line arguments. Check for required programs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'info')",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="also report on repos that are OK"
    )
    parser.add_argument(
        "-i",
        "--ignore",
        action="append",
        default=[],
        help="directories that contain IGNORE are ignored (can be use multiple times)",
    )
    parser.add_argument(
        "directories", nargs="*", help="one or more directories to process"
    )
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.debug(f"Command line arguments = {sys.argv}")
    logging.debug(f"Parsed arguments = {args}")
    # Check for required programs.
    try:
        sp.run(["git"], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        logging.debug("found “git”")
    except FileNotFoundError:
        logging.error("the program “git” cannot be found")
        sys.exit(1)
    return args


def runstatus(d, verbose=False):
    """
    Run git status in the specified directory.

    Report status and if branch is ahead of remotes.

    Arguments:
        d: Directory to run the checks in.
        verbose: Boolean to enable verbose messages.
    """
    os.chdir(d)
    home = os.environ["HOME"]
    idx = d.index(home) + len(home)
    d = '~' + d[idx:]
    outp = gitcmd("status", True)
    notclean = ""
    if b"working tree clean" not in outp:
        notclean = "\033[31mnot clean\033[0m"
    if b"is ahead of" in outp:
        if notclean:
            notclean = "\033[31mnot clean\033[0m, \033[35mahead of remote branch\033[0m"
        else:
            notclean = "\033[35mahead of remote branch\033[0m"
    if notclean:
        print(f"'{d}' is {notclean}.")
    elif verbose:
        print(f"'{d}' is \033[32mOK\033[0m.")


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
        if " " in cmds:
            raise ValueError("No spaces in single command allowed.")
        cmds = [cmds]
    else:
        if not isinstance(cmds, (list, tuple)):
            raise ValueError("args should be a list or tuple")
        if not all(isinstance(x, str) for x in cmds):
            raise ValueError("args should be a list or tuple of strings")
    cmds = ["git"] + cmds
    if output:
        cp = sp.run(cmds, stdout=sp.PIPE, stderr=sp.STDOUT)
        return cp.stdout
    else:
        cp = sp.run(cmds, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    return cp.returncode


if __name__ == "__main__":
    main()

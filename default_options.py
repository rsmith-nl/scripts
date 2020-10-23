#!/usr/bin/env python3
# file: default_options.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2016-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2018-03-26T23:04:50+02:00
# Last modified: 2019-11-15T23:16:50+0100
"""
For each package name given on the command line, determine if the options
are identical compared to the default options. If so, print out the package name.

* The ‘pkg info’ command is used to retrieve the origin
* The ‘pkg query’ command is used to retrieve the options that are set.
* For determining the default options, ‘make -V OPTIONS_DEFAULT’ is called
  from the port directory.

This program requires pkg(8), BSD make(1) and the ports tree.
[Note that GNU make won't work; it lacks the -V option.]
So this program will run on FreeBSD and maybe DragonflyBSD.
"""
# Imports {{{1
from enum import Enum
import concurrent.futures as cf
import os
import subprocess as sp
import sys


class Comparison(Enum):
    SAME = 0
    CHANGED = 1
    UNKNOWN = 2


def main(names):  # {{{1
    """
    Entry point for default_options.py

    Arguments:
        names: package names to check
    """
    # Look for required programs.
    err = sys.stderr
    try:
        for prog in ("pkg", "make"):
            sp.run([prog], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    except FileNotFoundError:
        print("ERROR: required program “{prog}” not found", file=err)
        sys.exit(1)
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        for pkg, result in tp.map(check, names):
            if result == Comparison.SAME:
                print(pkg)
            elif result == Comparison.UNKNOWN:
                print(f"# “{pkg}” is unknown in the ports tree.", file=err)
            else:
                print(f"# “{pkg}” uses non-default options.", file=err)


def run(args):  # {{{1
    """
    Run a subprocess and return the standard output.

    Arguments:
        args (list): List of argument strings. Typically a command name
            followed by options.

    Returns:
        Standard output of the program, converted to a string.
    """
    comp = sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL, text=True)
    return comp.stdout


def check(pkgname):  # {{{1
    """
    Check of a given package uses the default options or
    if options have been changed.

    Arguments:
        pkgname (str): The name of a package.

    Returns:
        A tuple of a string containing the package origin and a Comparison enum.
    """
    optionlines = run(["pkg", "query", "%Ok %Ov", pkgname]).splitlines()
    options_set = set(opt.split()[0] for opt in optionlines if opt.endswith("on"))
    try:
        origin = run(["pkg", "info", "-o", pkgname]).split()[-1]
        os.chdir("/usr/ports/{}".format(origin))
    except FileNotFoundError:
        return (pkgname, Comparison.UNKNOWN)
    default = run(["make", "-V", "OPTIONS_DEFAULT"])
    options_default = set(default.split())
    if options_default == options_set:
        v = Comparison.SAME
    else:
        v = Comparison.CHANGED
    return (origin, v)


if __name__ == "__main__":
    main(sys.argv[1:])

#!/usr/bin/env python3
# file: changed_options.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2018-03-26 20:53:13 +0200
# Last modified: 2018-03-26 23:03:02 +0200
"""
Get a list of installed packages. For each package, determine if the options
have been changed compared to the default options, and print that.

* The ‘pkg query’ command is used to retrieve the options that are set.
* For determining the default options, ‘make -V OPTIONS_DEFAULT’ is called
  from the port directory.

This program requires pkg(8) and the ports tree to be installed.
So this program will run on FreeBSD and maybe DragonflyBSD.
"""
# Imports {{{1
import concurrent.futures as cf
import os
import subprocess as sp
import sys


def run(args):  # {{{1
    """
    Run a subprocess and return the standard output.

    Arguments:
        args (list): List of argument strings. Typically a command name
            followed by options.

    Returns:
        Standard output of the program, converted to UTF-8 string.
    """
    comp = sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL)
    return comp.stdout.decode('utf-8')


def check(line):  # {{{1
    """
    Check of a given package uses the default options or
    if options have been changed.

    Arguments:
        line (str): A line of text containing the package name and origin,
        separated by whitespace.

    Returns:
        A string containing the package name and either [CHANGED] or [default].
    """
    pkg, origin = line.split()
    optionlines = run(['pkg', 'query', '%Ok %Ov', pkg]).splitlines()
    options_set = set(opt.split()[0] for opt in optionlines if opt.endswith('on'))
    try:
        os.chdir('/usr/ports/{}'.format(origin))
    except FileNotFoundError:
        return ('{}: undetermined'.format(pkg))
    default = run(['make', '-V', 'OPTIONS_DEFAULT'])
    options_default = set(default.split())
    if options_default == options_set:
        v = 'default'
    else:
        v = 'CHANGED'
    return '{}: [{}]'.format(pkg, v)


def main(argv):  # {{{1
    """
    Entry point for changed_options.py.

    Arguments:
        argv: command line arguments
    """
    data = run(['pkg', 'info', '-a', '-o'])
    packagelines = data.splitlines()
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        for rv in tp.map(check, packagelines):
            print(rv)


if __name__ == '__main__':
    main(sys.argv[1:])

#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
# file: open.py
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-12-26 11:45:59 +0100
# Last modified: 2017-10-07 22:39:54 +0200
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to open.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/
"""
Open file(s) given on the command line in the appropriate program.

Some of the programs are X11 programs.
"""

from os.path import isdir, isfile, exists
from re import search, IGNORECASE
from subprocess import Popen, run, PIPE
from sys import argv
import argparse
import logging
from magic import from_file

__version__ = '1.5.1'

# You should adjust the programs called to suit your preferences.
filetypes = {
    '\.(pdf|epub)$': ['mupdf'],
    '\.html$': ['firefox'],
    '\.xcf$': ['gimp'],
    '\.e?ps$': ['gv'],
    '\.(jpe?g|png|gif|tiff?|p[abgp]m|bmp|svg)$': ['gpicview'],
    '\.(pax|cpio|zip|jar|ar|xar|rpm|7z)$': ['tar', 'tf'],
    '\.(tar\.|t)(z|gz|bz2?|xz)$': ['tar', 'tf'],
    '\.(mp4|mkv|avi|flv|mpg|movi?|m4v|webm)$': ['mpv']
}
othertypes = {'dir': ['rox'], 'txt': ['gvim', '--nofork']}


def main(argv):  # noqa
    """Entry point for open.

    Arguments:
        argv: command line arguments; list of strings.
    """
    if argv[0].endswith(('open', 'open.py')):
        del argv[0]
    opts = argparse.ArgumentParser(prog='open', description=__doc__)
    opts.add_argument('-v', '--version', action='version', version=__version__)
    opts.add_argument('-a', '--application', help='application to use')
    opts.add_argument(
        '--log',
        default='warning',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'warning')")
    opts.add_argument(
        "files",
        metavar='file',
        nargs='*',
        help="one or more files to process")
    args = opts.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format='%(levelname)s: %(message)s')
    logging.info('command line arguments = {}'.format(argv))
    logging.info('parsed arguments = {}'.format(args))
    fail = "opening '{}' failed: {}"
    # Check for non-local files with `locate`.
    try:
        files = []
        for nm in args.files:
            if exists(nm):
                files.append(nm)
            else:
                cp = run(['locate', nm], stdout=PIPE)
                paths = cp.stdout.decode('utf-8').splitlines()
                if len(paths) == 1:
                    files.append(paths[0])
                elif len(paths) == 0:
                    logging.warning("path '{}' not found".format(nm))
                else:
                    logging.warning("ambiguous path '{}' skipped".format(nm))
                    for p in paths:
                        logging.warning("found '{}'".format(p))
    except FileNotFoundError:  # `locate` not available.
        files = args.files
    # Open the file(s).
    for nm in files:
        logging.info("Trying '{}'".format(nm))
        if not args.application:
            if isdir(nm):
                cmds = othertypes['dir'] + [nm]
            elif isfile(nm):
                cmds = matchfile(filetypes, othertypes, nm)
            else:
                cmds = None
        else:
            cmds = [args.application, nm]
        if not cmds:
            logging.warning("do not know how to open '{}'".format(nm))
            continue
        try:
            Popen(cmds)
        except OSError as e:
            logging.error(fail.format(nm, e))
    else:  # No files named
        if args.application:
            try:
                Popen([args.application])
            except OSError as e:
                logging.error(fail.format(args.application, e))


def matchfile(fdict, odict, fname):
    """
    Return the matching program for a given filename.

    Arguments:
        fdict: Handlers for files. A dictionary of regex:(commands)
            representing the file type and the action that is to be taken for
            opening one.
        odict: Handlers for other types. A dictionary of str:(arguments).
        fname: A string containing the name of the file to be opened.

    Returns: A list of commands for subprocess.Popen.
    """
    for k, v in fdict.items():
        if search(k, fname, IGNORECASE) is not None:
            return v + [fname]
    if b'text' in from_file(fname):
        return odict['txt'] + [fname]
    return None


if __name__ == '__main__':
    main(argv)

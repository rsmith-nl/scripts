#!/usr/bin/env python3
# file: open.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2014-12-26T13:36:19+01:00
# Last modified: 2018-07-07T15:03:21+0200
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

__version__ = '1.6'

# You should adjust the programs called to suit your preferences.
filetypes = {
    '\.(pdf|epub)$': ['mupdf'],
    '\.html$': ['firefox'],
    '\.xcf$': ['gimp'],
    '\.e?ps$': ['gv'],
    '\.(jpe?g|png|gif|tiff?|p[abgp]m|bmp|svg)$': ['gpicview'],
    '\.(pax|cpio|zip|jar|ar|xar|rpm|7z)$': ['tar', 'tf'],
    '\.(tar\.|t)(z|gz|bz2?|xz)$': ['tar', 'tf'],
    '\.(mp4|mkv|avi|flv|mpg|movi?|m4v|webm)$': ['mpv'],
    '\.(s3m|xm|mod|mid)$': ['urxvt', '-title', 'Timidity++', '-e', 'timidity', '-in', '-A30a']
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
        help="logging level (defaults to 'warning')"
    )
    opts.add_argument("files", metavar='file', nargs='*', help="one or more files to process")
    args = opts.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None), format='%(levelname)s: %(message)s'
    )
    logging.info(f'command line arguments = {argv}')
    logging.info(f'parsed arguments = {args}')
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
                    logging.warning(f"path '{nm}' not found")
                else:
                    logging.warning(f"ambiguous path '{nm}' skipped")
                    for p in paths:
                        logging.warning(f"found '{p}'")
    except FileNotFoundError:  # `locate` not available.
        files = args.files
    # Open the file(s).
    for nm in files:
        logging.info(f"Trying '{nm}'")
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
            logging.warning(f"do not know how to open '{nm}'")
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

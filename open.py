#!/usr/bin/env python3
# file: open.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-12-26 11:45:59 +0100
# $Date$
# $Revision$

"""Opens the files given on the command line in the approriate program."""

from re import search, IGNORECASE
from subprocess import Popen, check_output
from sys import argv
from os.path import basename, isdir, isfile

__version__ = '$Revision$'[11:-2]

filetypes = {'\.pdf$': ['mupdf'], '\.html$': ['firefox', '-new-tab'],
             '\.zip$': ['unzip', '-l'], '\.xcf$': ['gimp'],
             '\.(jpg|jpeg|png|gif|tif)$': ['gpicview'],
             '\.(tar\.|t)([zZ]|gz|bz[2]?|xz)$': ['tar', 'tf'],
             '\.(mp4|mkv|avi|flv|mpg|mov)$': ['mpv']}


def findprog(matchdict, fname):
    """For the given filename, returns the matching program.

    :param matchdict: dictionary of regex:[arguments]
    :param fname: file name
    :returns: the commands for subprocess.Open.
    """
    for k, v in matchdict.items():
        if search(k, fname, IGNORECASE) is not None:
            return v + [fname]
    try:
        if b'text' in check_output(['file', fname]):
            return ['gvim', '--nofork', fname]
    except CalledProcessError:
        pass
    return None


def main(args):
    """Entry point for this script.

    :param args: command line arguments
    """
    if len(args) == 1:
        binary = basename(args[0])
        print("{} ver. {}".format(binary, __version__), file=sys.stderr)
        print("Usage: {} [file ...]".format(binary), file=sys.stderr)
        sys.exit(0)
    del args[0]  # delete the name of the script.
    for nm in args:
        if isdir(nm):
            cmds = ['rox', nm]
        elif isfile(nm):
            cmds = findprog(filetypes, nm)
        if cmds is not None:
            Popen(cmds)


if __name__ == '__main__':
    main(argv)

#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
# file: open.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-12-26 11:45:59 +0100
# $Date$
# $Revision$
#
# To the extent possible under law, <rsmith@xs4all.nl> has waived all
# copyright and related or neighboring rights to open.py. This work is
# published from the Netherlands. See
# http://creativecommons.org/publicdomain/zero/1.0/

"""Opens the file(s) given on the command line in the approriate program.
It assumes you are running X11. It uses the following programs;"""

from re import search, IGNORECASE
from subprocess import Popen, check_output
from sys import argv, exit, stderr
from os.path import basename, isdir, isfile

__version__ = '$Revision$'[11:-2]

filetypes = {'\.pdf$': ['mupdf'], '\.html$': ['firefox', '-new-tab'],
             '\.zip$': ['unzip', '-l'], '\.xcf$': ['gimp'],
             '\.(jpg|jpeg|png|gif|tif)$': ['gpicview'],
             '\.(tar\.|t)([zZ]|gz|bz[2]?|xz)$': ['tar', 'tf'],
             '\.(mp4|mkv|avi|flv|mpg|mov)$': ['mpv']}
othertypes = {'dir': ['rox'], 'txt': ['gvim', '--nofork']}


def matchfile(fdict, odict, fname):
    """For the given filename, returns the matching program.

    :param fdict: handlers for files; dictionary of regex:[arguments]
    :param odict: handlers for other types; dictionary of str:[arguments]
    :param fname: file name
    :returns: a list of commands for subprocess.Open.
    """
    for k, v in fdict.items():
        if search(k, fname, IGNORECASE) is not None:
            return v + [fname]
    try:
        if b'text' in check_output(['file', fname]):
            return odict['txt'] + [fname]
    except CalledProcessError:
        pass
    return None


def main(args):
    """Entry point for this script.

    :param args: command line arguments
    """
    if len(args) == 1:
        binary = basename(args[0])
        print("{} ver. {}".format(binary, __version__), file=stderr)
        print("Usage: {} [file ...]\n".format(binary), file=stderr)
        print(__doc__)
        print("* file")
        for v in filetypes.values():
            print("* {}".format(v[0]))
        tfs = "\nAny other files that contain text are opened with {}."
        print(tfs.format(othertypes['txt'][0]))
        print("Directories are opened with {}.".format(othertypes['dir'][0]))
        exit(0)
    del args[0]  # delete the name of the script.
    for nm in args:
        if isdir(nm):
            cmds = othertypes['dir'] + [nm]
        elif isfile(nm):
            cmds = matchfile(filetypes, othertypes, nm)
        if cmds is not None:
            Popen(cmds)

if __name__ == '__main__':
    main(argv)

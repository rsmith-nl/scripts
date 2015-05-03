#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-05-03 22:10:01 +0200
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to mkhistory.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Script to format a Git log for LaTeX"""

import os
import subprocess
import sys

# The following texts determine how the commits are generated. Change them to
# suit your preferences.
header = r"""% -*- latex -*-
% Automatisch gegenereerd door tools/mkhistory.py

\chapter{Wijzigingen}

Dit hoofdstuk wordt automatisch gegenereerd uit het \texttt{git}
revisiecontrolesysteem. De meest recente wijzigingen staan bovenaan.

"""

commithdr = r'wijziging:'
authorhdr = r'door:'
datehdr = r'datum:'

# If you change the commithdr, authorhdr or datehdr, you might have to change
# the widths in the begintable text below.
begintable = r"""\begingroup\hspace{-\tabcolsep}
\begin{tabular}{p{0.1\textwidth}p{0.8\textwidth}}
"""

endtable = r"""\end{tabular}\endgroup

"""


def genrecords(lol):
    """Generate a LaTeX table for each commit in the input lines..

    Keyword arguments:
    lol -- list of lines
    """
    rv = ''
    for ln in lol:
        if ln.startswith('commit'):
            if rv:
                rv += endtable
                yield rv
            rv = begintable
            words = ln.split(' ', 1)
            ln = ln.replace(' ', ' & ', 1)
            rv += '  ' + commithdr + ' & ' + words[1] + '\\\\\n'
        elif ln.startswith('Merge:'):
            words = ln.split(':', 1)
            rv += '  ' + commithdr + ': & ' + words[1].lstrip(None) + '\\\\\n'
        elif ln.startswith('Author:'):
            ln = ln.replace(': ', ': & ')
            ln = ln.replace('Author:', authorhdr)
            rv += '  ' + ln + '\\\\\n'
        elif ln.startswith('Date:'):
            ln = ln.replace(': ', ': & ')
            ln = ln.replace('Date:', datehdr)
            rv += '  ' + ln + '\\\\\n'
        else:
            ln = ln.lstrip(None)
            if len(ln):
                rv += '  & ' + ln + '\\\\\n'
    if rv:
        rv += endtable + '% EOF\n'
        yield rv
    return


def main(argv):
    """Main program.

    Keyword arguments:
    argv -- command line arguments
    """
    if len(argv) == 1:
        binary = os.path.basename(argv[0])
        print("Usage: {} outputfilename".format(binary))
        sys.exit(0)
    fn = argv[1]
    try:
        lines = subprocess.check_output(['git', 'log']).decode().split('\n')
    except subprocess.CalledProcessError:
        print("Git not found! Stop.")
        sys.exit(1)
    if fn == '-':
        of = sys.stdout
    else:
        of = open(fn, 'w+')
    of.write(header)
    for rec in genrecords(lines):
        of.write(rec)
    of.close()


if __name__ == '__main__':
    main(sys.argv)

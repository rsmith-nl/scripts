#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-11-03 14:42:56 +0100
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to mkhistory.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Script to format a Git log for LaTeX"""

import os
import re
import subprocess
import sys

# The following texts determine how the commits are generated. Change them to
# suit your preferences.
header = r"""% vim:fileencoding=utf-8:ft=tex
% Automatisch gegenereerd door tools/mkhistory.py

"""


def fmtlog(txt):
    """Reformat the text of the one-line log"""
    # Replace TeX special characters in the whole text.
    specials = ('_', '#', '%', '\$', '{', '}')
    for s in specials:
        txt = re.sub(r'(?<!\\)' + s, '\\' + s, txt)
    # Remove periods at the end of lines.
    txt = re.sub('\.$', '', txt, flags=re.MULTILINE)
    lines = txt.split('\n')
    # Remove reference to HEAD
    lines[0] = re.sub('\(.*\) ', '', lines[0])
    # Use typewriter font for the commit id.
    lines = [r'\texttt{' + re.sub(' ', r'} ', ln, count=1)
             for ln in lines if ln]
    return '\\\\\n'.join(lines)


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
        args = ['git', 'log', '--oneline']
        txt = subprocess.check_output(args).decode()
    except subprocess.CalledProcessError:
        print("Git not found! Stop.")
        sys.exit(1)
    if fn == '-':
        of = sys.stdout
    else:
        of = open(fn, 'w+')
    of.write(header)
    of.write(fmtlog(txt))
    of.close()


if __name__ == '__main__':
    main(sys.argv)

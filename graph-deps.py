#!/usr/bin/env python3
# file: graph-deps.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2017-04-27 13:50:28 +0200
# Last modified: 2018-03-10 22:50:33 +0100
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to graph-deps.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/
"""
Creates a graph of FreeBSD package dependencies.

Use it like this:

    pkg info -dx py27- | python3 graph-deps.py | dot -o py27-deps.pdf -Tpdf

This will output a graphviz digraph for all Python 2.7 packages on stdout,
which is processed by the “dot” program from the graphics/graphviz port and
turned into a PDF rendering of the graph.
"""

import sys

if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help'):
    print(__doc__)
    exit(0)
output = ['digraph deps {', 'rankdir=LR;', 'fontname="Alegreya";', 'concentratr=true;',
          'node [shape=box, fontname="Alegreya"];']
parent = None
try:
    for ln in sys.stdin:
        pkgname = ln.strip()
        if pkgname.endswith(':'):
            pkgname = pkgname[:-1]
        output.append('"{0}" [label="{0}"];'.format(pkgname))
        if ln[0] not in ' \t':  # parent
            parent = pkgname
        else:
            output.append('"{}" -> "{}";'.format(parent, pkgname))
except KeyboardInterrupt:
    print('\n', __doc__)
else:
    print('\n'.join(output) + '}')

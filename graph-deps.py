# file: graph-deps.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2017-04-27 13:50:28 +0200
# Last modified: 2017-04-27 14:29:56 +0200

"""Create a graph of FreeBSD package dependencies.

Use it like this:

    pkg info -dx py27- | python3 graph-deps.py | dot -o py27-deps.pdf -Tpdf

This will output a graphviz digraph for all Python 2.7 packages on stdout,
which is processed by the “dot” program from the graphics/graphviz port and
turned into a PDF rendering of the graph.
"""

import sys

output = ['digraph deps {', 'rankdir=LR;', 'node [shape=box];']
parent = None
for ln in sys.stdin:
    pkgname = ln.strip()
    if pkgname.endswith(':'):
        pkgname = pkgname[:-1]
    output.append('"{0}" [label="{0}"];'.format(pkgname))
    if ln[0] not in ' \t':  # parent
        parent = pkgname
    else:
        output.append('"{}" -> "{}";'.format(parent, pkgname))
print('\n'.join(output)+'}')

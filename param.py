#!/usr/bin/env python3
# file: param.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>
# Created: 2019-12-07T13:30:37+0100
# Last modified: 2019-12-07T17:11:01+0100
"""Executes or evaluates Python code between <> in a file.
Usage: param.py input output [var=value ...]
"""

import logging
import re
import os
import sys


def main(args):
    logging.basicConfig(level='INFO', format='%(levelname)s: %(message)s')
    if len(args) < 2:
        print(__doc__)
        exit(0)
    # Save file names
    infname, outfname = args[0], args[1]
    # Process arguments
    overrides = getvars(args[2:])
    lines = readfile(infname)
    globvar = {"__builtins__": None}
    writefile(outfname, lines, globvar, overrides)


def getvars(args):
    vdict = {}
    for arg in args:
        if '=' not in arg:
            logging.warning('no “=” in “{arg}”; skipped')
            continue
        exec(arg, None, vdict)
    return vdict


def readfile(path):
    with open(path) as f:
        lines = f.readlines()
    return list(enumerate(lines, start=1))


def writefile(path, lines, globvar, overrides):
    locvar = {}
    if path == '-':
        outf = sys.stdout
    else:
        outf = open(path, 'w')
        outf.reconfigure(newline=os.linesep)
    for num, line in lines:
        outline = line
        expr = re.findall('<.[^>]*>', line)
        for e in expr:
            if '=' in e:
                rep = e[1:-1]
                exec(e[1:-1], globvar, locvar)
                for k in overrides.keys():
                    if k in locvar and locvar[k] != overrides[k]:
                        locvar[k] = overrides[k]
                        logging.info(f'{k} overridden by command line on line {num}')
                        rep = f'{k} = {overrides[k]}'
                outline = outline.replace(e, rep)
            else:
                try:
                    res = str(eval(e[1:-1], globvar, locvar))
                    outline = outline.replace(e, res)
                except NameError as err:
                    logging.error(f'line {num} ' + err)
        outf.write(outline)
    outf.close()


if __name__ == '__main__':
    main(sys.argv[1:])

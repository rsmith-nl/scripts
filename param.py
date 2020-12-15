#!/usr/bin/env python
# file: param.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2019 R.F. Smith <rsmith@xs4all.nl>
# Created: 2019-12-07T13:30:37+0100
# Last modified: 2020-07-18T00:46:55+0200
"""Executes or evaluates Python code between <> on a single line in a file.
Usage: param.py input output [var=value ...]

Values defined on the command line override those given in the input file.

For example, <x=3/4> will be replaced by x=3/4, while <x> will be replaced by
0.75 and <2*x> will be replaced by 1.5.

The math constants e and pi are recognized without having to be imported, as
are some math functions;
* sin, cos, tan (taking degrees as arguments, not radians).
* asin, acos, atan (returning degrees as results).
* log, log2 and log10
* ceil, floor
* pow, sqrt

This script is meant for *relatively simple* parameter substitutions and
calculations.
"""

import logging
import math
import re
import os
import sys


def main(args):
    logging.basicConfig(level="INFO", format="%(levelname)s: %(message)s")
    if len(args) < 2:
        print(__doc__)
        exit(0)
    # Save file names
    infname, outfname = args[0], args[1]
    # Process arguments
    overrides = getvars(args[2:])
    lines = readfile(infname)
    globvar = mkglobals()
    writefile(outfname, lines, globvar, overrides)


def getvars(args):
    vdict = {}
    for arg in args:
        if "=" not in arg:
            logging.warning("no “=” in “{arg}”; skipped")
            continue
        exec(arg, None, vdict)
    return vdict


def readfile(path):
    with open(path) as f:
        lines = f.readlines()
    return list(enumerate(lines, start=1))


def mkglobals():
    rv = {"__builtins__": None}

    def sin(deg):
        return math.sin(math.radians(deg))

    def asin(num):
        return math.degrees(math.asin(num))

    def cos(deg):
        return math.cos(math.radians(deg))

    def acos(num):
        return math.degrees(math.acos(num))

    def tan(deg):
        return math.tan(math.radians(deg))

    def atan(num):
        return math.degrees(math.atan(num))

    for k in ["e", "pi", "log", "log2", "log10", "floor", "ceil", "pow", "sqrt"]:
        rv[k] = eval("math." + k)
    for k in ["sin", "asin", "cos", "acos", "tan", "atan", "round"]:
        rv[k] = eval(k)

    return rv


def writefile(path, lines, globvar, overrides):
    locvar = {k: v for k, v in overrides.items()}
    if path == "-":
        outf = sys.stdout
    else:
        outf = open(path, "w")
        outf.reconfigure(newline=os.linesep)
    for num, line in lines:
        outline = line
        expr = re.findall("<[^@<>]*>", line)
        for e in expr:
            if "=" in e:
                rep = e[1:-1]
                exec(e[1:-1], globvar, locvar)
                for k in overrides.keys():
                    if k in locvar and locvar[k] != overrides[k]:
                        locvar[k] = overrides[k]
                        logging.info(f"{k} overridden by command line on line {num}")
                        rep = f"{k} = {overrides[k]}"
                outline = outline.replace(e, rep)
            else:
                try:
                    res = str(eval(e[1:-1], globvar, locvar))
                    outline = outline.replace(e, res)
                except (NameError, TypeError) as err:
                    logging.error(f"line {num}, evaluating {e} " + str(err))
        outf.write(outline)
    outf.close()


if __name__ == "__main__":
    main(sys.argv[1:])

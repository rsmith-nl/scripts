#!/usr/bin/env python
# file: img4latex.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2014-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2014-12-05T01:26:59+01:00
# Last modified: 2020-04-01T00:15:43+0200
"""Create a suitable LaTeX figure environment for image files."""

import argparse
import configparser
import logging
import os
import subprocess as sp
import sys

__version__ = "2020.04.01"


def main():
    """
    Entry point for img4latex.
    """
    args = setup()
    for filename in args.file:
        if not os.path.exists(filename):
            logging.error(f'file "{filename}" does not exist.')
            continue
        if filename.endswith((".ps", ".PS", ".eps", ".EPS", ".pdf", ".PDF")):
            bbox = getpdfbb(filename)
            bbwidth = float(bbox[2]) - float(bbox[0])
            bbheight = float(bbox[3]) - float(bbox[1])
            hscale = 1.0
            vscale = 1.0
            if bbwidth > args.width:
                hscale = args.width / bbwidth
            if bbheight > args.height:
                vscale = args.height / bbheight
            logging.info(f"hscale: {hscale:.3f}, vscale: {vscale:.3f}")
            scale = min([hscale, vscale])
            if scale < 0.999:
                fs = "[viewport={} {} {} {},clip,scale={s:.3f}]"
                opts = fs.format(*bbox, s=scale)
            else:
                fs = "[viewport={} {} {} {},clip]"
                opts = fs.format(*bbox)
        elif filename.endswith((".png", ".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG")):
            width, height = getpicsize(filename)
            opts = None
            hscale = args.width / width
            vscale = args.height / height
            logging.info(f"hscale: {hscale:.3f}, vscale: {vscale:.3f}")
            scale = min([hscale, vscale])
            if scale < 0.999:
                opts = f"[scale={scale:.3f}]"
        else:
            logging.error(f'file "{filename}" has an unrecognized format. Skipping...')
            continue
        output_figure(filename, opts)
    print()


def setup():
    """Process command-line arguments. Read config file."""
    after = """
The width and height arguments can also be set in a configuration file
called ~/.img4latexrc. It should look like this:

    [size]
    width = 125
    height = 280

Command-line arguments override settings in the configuration file.
Otherwise, the defaults apply.
"""
    raw = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=raw, epilog=after
    )
    parser.add_argument(
        "-w",
        "--width",
        type=float,
        default=160,
        help="width of the text block in mm. (default=160)",
    )
    parser.add_argument(
        "-t",
        "--height",
        type=float,
        default=270,
        help="height of the text block in mm. (default=270)",
    )
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("file", nargs="*")
    cfg = from_config()
    args = parser.parse_args(sys.argv[1:], namespace=cfg)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%% %(levelname)s: %(message)s",
    )
    if cfg is None:
        logging.info("configuration file not found")
    else:
        logging.info(f"from config: {cfg}")
    logging.debug(f"command line arguments = {sys.argv}")
    logging.debug(f"parsed arguments = {args}")
    args.width *= 72 / 25.4  # convert to points
    args.height *= 72 / 25.4  # convert to points
    if not args.file:
        parser.print_help()
        sys.exit(0)
    return args


def from_config():
    """
    Read configuration data.

    Returns:
        An Argparse.Namespace object
    """
    values = argparse.Namespace()
    d = vars(values)
    config = configparser.ConfigParser()
    cfgname = os.environ["HOME"] + os.sep + ".img4latexrc"
    if not config.read(cfgname):
        return None
    for name in ["width", "height"]:
        if name in config["size"]:
            d[name] = float(config["size"][name])
    return values


def getpdfbb(fn):
    """
    Get the BoundingBox of a PostScript or PDF file.

    Arguments:
        fn: Name of the file to get the BoundingBox from.

    Returns:
        A tuple of strings in the form (llx lly urx ury), where ll means
        lower left and ur means upper right.
    """
    gsopts = [
        "gs",
        "-q",
        "-dFirstPage=1",
        "-dLastPage=1",
        "-dNOPAUSE",
        "-dBATCH",
        "-sDEVICE=bbox",
        fn,
    ]
    gsres = sp.run(gsopts, stdout=sp.PIPE, stderr=sp.STDOUT, text=True, check=True)
    bbs = gsres.stdout.splitlines()[0]
    return bbs.split(" ")[1:]


def getpicsize(fn):
    """
    Get the width and height of a bitmapped file.

    Arguments:
        fn: Name of the file to check.

    Returns:
        Width, hight of the image in points.
    """
    args = ["identify", "-verbose", fn]
    rv = sp.run(args, stdout=sp.PIPE, stderr=sp.STDOUT, text=True, check=True)
    data = {}
    for ln in rv.stdout.splitlines():
        k, v = ln.strip().split(":", 1)
        data[k] = v.strip()
    if data["Units"] != "Undefined":
        res = float(data["Resolution"].split("x")[0])
    else:
        res = 72  # default for includegraphics.
    logging.debug("resolution={} {}".format(res, data["Units"]))
    geom = data["Geometry"].split("+")[0].split("x")
    xsize, ysize = int(geom[0]), int(geom[1])
    logging.debug(f"x={xsize} px, y={ysize} px")
    factor = {"PixelsPerInch": 72, "PixelsPerCentimeter": 28.35, "Undefined": 72}
    m = factor[data["Units"]] / res
    x, y = xsize * m, ysize * m
    logging.debug(f"scaled x={x} pt, y={y} pt")
    return (x, y)


def output_figure(fn, options=None):
    r"""
    Print the LaTeX code for the figure.

    Arguments:
        fn: name of the file.
        options: options to add to the \includegraphics command.
    """
    fb = fn.rpartition(".")[0]
    fbnodir = fb[fn.rfind("/") + 1 :]
    print()
    print(r"\begin{figure}[!htbp]")
    if options:
        print(r"  \centerline{\includegraphics" + options + "%")
        print(r"    {{{}}}}}".format(fb))
    else:
        print(r"  \centerline{{\includegraphics{{{}}}}}".format(fb))
    label = fbnodir.replace(" ", "-").replace("_", "-")
    print(r"  \caption{{\label{{fig:{}}}{}}}".format(label, label))
    print(r"\end{figure}")


if __name__ == "__main__":
    main()

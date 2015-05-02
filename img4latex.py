#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
# file: img4latex.py
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-12-04 20:14:34 +0100
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to img4latex.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Program to check a PDF, PNG or JPEG file and return
   a suitable LaTeX figure environment for it."""

__version__ = '$Revision$'[11:-2]

import argparse
import os
import subprocess
import sys


def getpdfbb(fn):
    """Use ghostscript to get the BoundingBox of a PostScript or PDF
    file.

    :param fn: name of the file to get the BoundingBox from
    :returns: a tuple of strings in the form (llx lly urx ury).
    """
    gsopts = ['gs', '-q', '-dFirstPage=1', '-dLastPage=1', '-dNOPAUSE',
              '-dBATCH', '-sDEVICE=bbox', fn]
    gsres = subprocess.check_output(gsopts, stderr=subprocess.STDOUT)
    bbs = gsres.decode().splitlines()[0]
    return bbs.split(' ')[1:]


def getpixwidth(fn):
    """Use ImageMagick to get the width of a bitmapped file

    :param fn: name of the file to check.
    :returns: width in points.
    """
    idargs = ['identify', '-verbose', fn]
    idres = subprocess.check_output(idargs, stderr=subprocess.STDOUT)
    lines = idres.decode().splitlines()
    data = {}
    for ln in lines:
        k, v = ln.strip().split(':', 1)
        data[k] = v.strip()
    if data['Units'] != 'Undefined':
        res = float(data['Resolution'].split('x')[0])
    else:
        res = 300
    size = int(data['Geometry'].split('+')[0].split('x')[0])
    # Convert pixels to points
    factor = {
        'PixelsPerInch': 72,
        'PixelsPerCentimeter': 28.35,
        'Undefined': 72
    }
    return size / res * factor[data['Units']]


def output_figure(fn, options=""):
    """Print the LaTeX code for the figure.

    :param fn: name of the file to get the BoundingBox from
    :param options: options to add to the \includegraphics command
    """
    fb = fn.rpartition('.')[0]
    fbnodir = fb[fn.rfind('/') + 1:]
    print()
    print(r'\begin{figure}[!htbp]')
    print(r'  \centerline{\includegraphics' + options + '%')
    print(r'    {{{}}}}}'.format(fb))
    label = fbnodir.replace(' ', '-').replace('_', '-')
    print(r'  \caption{{\label{{fig:{}}}{}}}'.format(label, label))
    print(r'\end{figure}')


def checkfor(args, rv=0):
    """Make sure that a program necessary for using this script is
    available.

    :param args: String or list of strings of commands. A single string may
    not contain spaces.
    :param rv: Expected return value from evoking the command.
    """
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('no spaces in single command allowed')
        args = [args]
    try:
        with open(os.devnull, 'w') as bb:
            rc = subprocess.call(args, stdout=bb, stderr=bb)
        if rc != rv:
            raise OSError
    except OSError as oops:
        outs = "Required program '{}' not found: {}."
        print(outs.format(args[0], oops.strerror))
        sys.exit(1)


def main(argv):
    """Entry point for this script.

    :param argv: command line arguments
    """
    checkfor(['gs', '-v'])
    checkfor(['identify', '-version'])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-w', '--width',
                        default=160,
                        type=float,
                        help='width of the text block in mm.')
    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__)
    parser.add_argument('file', nargs='*')
    args = parser.parse_args(argv)
    args.width *= 72 / 25.4  # convert to points
    del args.file[0]
    if not args.file:
        parser.print_help()
        sys.exit(0)
    for filename in args.file:
        if not os.path.exists(filename):
            print('File "{}" does not exist.'.format(filename))
            continue
        if filename.endswith(('.ps', '.PS', '.eps', '.EPS', '.pdf', '.PDF')):
            bbox = getpdfbb(filename)
            bbwidth = float(bbox[2]) - float(bbox[0])
            scale = 1.0
            if bbwidth > args.width:
                scale = args.width / bbwidth
            fs = '[viewport={} {} {} {},clip,scale={s:.3f}]'
            opts = fs.format(*bbox, s=scale)
        elif filename.endswith(('.png', '.PNG', '.jpg', '.JPG', '.jpeg',
                                '.JPEG')):
            width = getpixwidth(filename)
            opts = ''
            if width > args.width:
                opts = '[scale={:.3f}]'.format(args.width / width)
        else:
            fskip = 'File "{}" has an unrecognized format. Skipping...'
            print(fskip.format(filename))
            continue
        output_figure(filename, opts)
    print()


if __name__ == '__main__':
    main(sys.argv)

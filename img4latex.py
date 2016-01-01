#!/usr/bin/env python3
# vim:fileencoding=utf-8:ft=python
# file: img4latex.py
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2014-12-04 20:14:34 +0100
# Last modified: 2016-01-06 21:43:52 +0100
#
# To the extent possible under law, R.F. Smith has waived all copyright and
# related or neighboring rights to img4latex.py. This work is published
# from the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Program to check a PDF, PNG or JPEG file and return
   a suitable LaTeX figure environment for it."""

import argparse
import logging
import os
import subprocess
import sys
from wand.image import Image

__version__ = '1.3.0'


def main(argv):
    """Entry point for img4latex.

    Arguments:
        argv: All command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-w', '--width', default=160, type=float,
                        help='width of the text block in mm. (default 160)')
    parser.add_argument('--log', default='warning',
                        choices=['debug', 'info', 'warning', 'error'],
                        help="logging level (defaults to 'warning')")
    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__)
    parser.add_argument('file', nargs='*')
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                        format='%% %(levelname)s: %(message)s')
    logging.debug('command line arguments = {}'.format(argv))
    logging.debug('parsed arguments = {}'.format(args))
    args.width *= 72 / 25.4  # convert to points
    checkfor(['gs', '-v'])
    if not args.file:
        parser.print_help()
        sys.exit(0)
    for filename in args.file:
        if not os.path.exists(filename):
            logging.error('file "{}" does not exist.'.format(filename))
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
            width = getpicwidth(filename)
            opts = ''
            if width > args.width:
                opts = '[scale={:.3f}]'.format(args.width / width)
        else:
            fskip = 'file "{}" has an unrecognized format. Skipping...'
            logging.error(fskip.format(filename))
            continue
        output_figure(filename, opts)
    print()


def checkfor(args, rv=0):
    """
    Make sure that a program necessary for using this script is available.
    If the required utility is not found, this function will exit the program.

    Arguments:
        args: String or list of strings of commands. A single string may not
            contain spaces.
        rv: Expected return value from evoking the command.
    """
    if isinstance(args, str):
        if ' ' in args:
            raise ValueError('no spaces in single command allowed')
        args = [args]
    try:
        rc = subprocess.call(args, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        if rc != rv:
            raise OSError
        logging.info('found required program "{}"'.format(args[0]))
    except OSError as oops:
        outs = 'required program "{}" not found: {}.'
        logging.error(outs.format(args[0], oops.strerror))
        sys.exit(1)


def getpdfbb(fn):
    """Use ghostscript to get the BoundingBox of a PostScript or PDF
    file.

    Arguments:
        fn: Name of the file to get the BoundingBox from.

    Returns:
        A tuple of strings in the form (llx lly urx ury), where ll means
        lower left and ur means upper right.
    """
    gsopts = ['gs', '-q', '-dFirstPage=1', '-dLastPage=1', '-dNOPAUSE',
              '-dBATCH', '-sDEVICE=bbox', fn]
    gsres = subprocess.check_output(gsopts, stderr=subprocess.STDOUT)
    bbs = gsres.decode().splitlines()[0]
    return bbs.split(' ')[1:]


def getpicwidth(fn):
    """Use ImageMagick to get the width of a bitmapped file.

    Arguments:
        fn: Name of the file to check.

    Returns:
        Width of the image in points.
    """
    factor = {
        'pixelsperinch': 72,
        'pixelspercentimeter': 28.35,
        'undefined': 72
    }
    with Image(filename=fn) as img:
        if img.units is not 'undefined':
            res, _ = img.resolution
        else:
            res = 300
        return img.width / res * factor[img.units]
    return None


def output_figure(fn, options=""):
    """Print the LaTeX code for the figure.

    Arguments:
        fn: name of the file.
        options: options to add to the \includegraphics command.
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


if __name__ == '__main__':
    main(sys.argv[1:])

#!/usr/bin/env python3
# file: foto4lb.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2011-2019 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2011-11-07T21:40:58+01:00
# Last modified: 2019-07-27T14:52:19+0200
"""Shrink fotos to a size suitable for use in my logbook."""

from datetime import datetime
import argparse
import concurrent.futures as cf
import logging
import os
import subprocess as sp
import sys
# For performance measurments
# import time

from PIL import Image
from PIL.ExifTags import TAGS

__version__ = '2.1'
outdir = 'foto4lb'
extensions = ('.jpg', '.jpeg', '.raw')


def main(argv):
    """
    Entry point for foto4lb.

    Arguments:
        argv: Command line arguments without the script name.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-w',
        '--width',
        default=886,
        type=int,
        help='width of the images in pixels (default 886)'
    )
    parser.add_argument(
        '--log',
        default='warning',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'warning')"
    )
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('path', nargs='*', help='directory in which to work')
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format='%(levelname)s: %(message)s'
    )
    logging.debug(f'Command line arguments = {argv}')
    logging.debug(f'Parsed arguments = {args}')
    if not args.path:
        parser.print_help()
        sys.exit(0)
    checkfor('convert', rv=1)
    pairs = []
    count = 0
    for path in args.path:
        if os.path.exists(path + os.sep + outdir):
            logging.warning(f'"{outdir}" already exists in "{path}", skipping this path.')
            continue
        files = [
            f.name for f in os.scandir(path)
            if f.is_file() and f.name.lower().endswith(extensions)
        ]
        count += len(files)
        pairs.append((path, files))
        logging.debug(f'Path: "{path}"')
        logging.debug(f'Files: {files}')
    if len(pairs) == 0:
        logging.info('nothing to do.')
        return
    logging.info(f'found {count} files.')
    logging.info('creating output directories.')
    for dirname, _ in pairs:
        os.mkdir(dirname + os.sep + outdir)
    infodict = {
        0: "file '{}' processed.",
        1: "file '{}' is not an image, skipped.",
        2: "error running convert on '{}'."
    }
    # For performance measurements.
    # start = time.monotonic()
    with cf.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
        agen = ((p, fn, args.width) for p, flist in pairs for fn in flist)
        for fn, rv in tp.map(processfile, agen):
            logging.info(infodict[rv].format(fn))
    # For performance measurements.
    # dt = time.monotonic() - start
    # logging.info(f'startup preparations took {dt:.2f} s')


def checkfor(args, rv=0):
    """
    Ensure that a program necessary for using this script is available.

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
    else:
        if not isinstance(args, (list, tuple)):
            raise ValueError('args should be a list or tuple')
        if not all(isinstance(x, str) for x in args):
            raise ValueError('args should be a list or tuple of strings')
    try:
        cp = sp.run(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    except FileNotFoundError as oops:
        logging.error(f'required program "{args[0]}" not found: {oops.strerror}.')
        sys.exit(1)
    if cp.returncode != rv:
        logging.error(f'returncode {cp.returncode} should be {rv}')
        sys.exit(1)
    logging.info(f'found required program "{args[0]}"')


def processfile(packed):
    """
    Read an image file and write a smaller version.

    Arguments:
        packed: A 3-tuple of (path, filename, output width)

    Returns:
        A 2-tuple (input file name, status).
        Status 0 indicates a succesful conversion,
        status 1 means that the input file was not a recognized image format,
        status 2 means a subprocess error.
    """
    # For performance measurements.
    # start = time.monotonic()
    path, name, newwidth = packed
    fname = os.sep.join([path, name])
    oname = os.sep.join([path, outdir, name.lower()])
    try:
        img = Image.open(fname)
        ld = {}
        for tag, value in img._getexif().items():
            decoded = TAGS.get(tag, tag)
            ld[decoded] = value
        want = set(['DateTime', 'DateTimeOriginal', 'CreateDate', 'DateTimeDigitized'])
        available = sorted(list(want.intersection(set(ld.keys()))))
        fields = ld[available[0]].replace(' ', ':').split(':')
        dt = datetime(*map(int, fields))
    except Exception:
        logging.warning('exception raised when reading the file time.')
        dt = datetime.today()
    args = [
        'convert', fname, '-strip', '-resize',
        str(newwidth), '-units', 'PixelsPerInch', '-density', '300', '-unsharp',
        '2x0.5+0.7+0', '-quality', '80', oname
    ]
    rp = sp.call(args)
    if rp != 0:
        return (name, 2)
    modtime = dt.timestamp()
    os.utime(oname, (modtime, modtime))
    # For performance measurements.
    # dt = time.monotonic() - start
    # logging.info(f'processfile took {dt:.2f} s')
    return (fname, 0)


if __name__ == '__main__':
    main(sys.argv[1:])

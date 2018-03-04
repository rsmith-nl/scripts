#!/usr/bin/env python3
# file: fix-pdftitle.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2017-04-11 15:39:37 +0200
# Last modified: 2018-03-04 11:47:26 +0100
"""
Fix PDF file titles.

Decrypt PDF safety data sheets and fix the title to match the filename.
This is done to make sure that the reader app on a tablet displays a sensible title.
"""

from collections import defaultdict
import argparse
import logging
import os
import shutil
import subprocess as sp
import sys
import tempfile

__version__ = '1.1'


def pdfinfo(path):
    """
    Retrieves the contents of the ‘info’ dictionary from a PDF file using
    the ``pdfinfo`` program.

    Arguments:
        path (str): The path to the PDF file to use.

    Returns:
        A collections.defaultdict containing the info dictionary. Using a
        non-existing key will return an empty string.
    """
    args = ['pdfinfo', path]
    rv = sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL)
    if rv.returncode != 0:
        return defaultdict(lambda: '')
    pairs = [(k, v.strip()) for k, v in
             [ln.split(':', 1) for ln in rv.stdout.decode('utf-8').splitlines()]]
    return defaultdict(lambda: '', pairs)


def decrypt(path, fn, tempdir):
    """
    Decrypt a PDF file using ``qpdf``.

    Arguments:
        path (str): Path to the file to decrypt.
        fn (str): Only the name of the file to decrypt.
        tempdir (str): Location of temporary directory to use.

    Returns:
        The return value of the ``qpdf`` call; 0 when succesfull.
    """
    tmppath = tempdir + os.sep + fn
    args = ['qpdf', '--decrypt', path, tmppath]
    rv = sp.run(args)
    if rv.returncode == 0:
        os.remove(path)
        shutil.copyfile(tmppath, path)
    os.remove(tmppath)
    return rv.returncode


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--log',
        default='info',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'info')")
    parser.add_argument(
        '-v', '--version', action='version', version=__version__)
    parser.add_argument(
        "files",
        metavar='file',
        nargs='+',
        help="one or more files to process")
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format='%(levelname)s: %(message)s')
    if args.log == 'debug':
        logging.debug('using verbose logging')
    tdir = tempfile.mkdtemp()
    for path in args.files:
        logging.debug('processing {}'.format(path))
        info = pdfinfo(path)
        if len(info) == 0:
            es = 'skipping {}; could not retrieve info dict'
            logging.error(es.format(path))
            continue
        fn = os.path.basename(path)
        if info['Encrypted'].startswith('yes'):
            logging.info('{} is encrypted'.format(path))
            rv = decrypt(path, fn, tdir)
            if rv != 0:
                es = 'could not decrypt {}; qpdf returned {}'
                logging.error(es.format(path, rv))
                continue
            logging.debug('{} decrypted'.format(path))
        else:
            logging.debug('{} is not encrypted'.format(path))
        newtitle = fn.replace('_', ' ')[:-4]
        if info['Title'] != newtitle:
            # Use ghostscript to change the title
            with open('pdfmarks', 'w') as marksfile:
                marksfile.write('[ /Title ({})\n  /DOCINFO pdfmark'.format(newtitle))
            args2 = ['gs', '-q', '-dBATCH', '-dNOPAUSE', '-sDEVICE=pdfwrite',
                     '-sOutputFile=withmarks.pdf', path, 'pdfmarks']
            rv = sp.run(args2, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            if rv.returncode != 0:
                os.remove('withmarks.pdf')
                es = 'could not change title of {}; exiftool returned {}'
                logging.error(es.format(path, rv.returncode))
            else:
                try:
                    os.remove(path)
                    os.rename('withmarks.pdf', path)
                    logging.info('title of {} changed'.format(path))
                except OSError as e:
                    es = 'could not rename withmarks.pdf to {}: {}'
                    logging.error(es.format(path, e))
            os.remove('pdfmarks')
        else:
            logging.debug('the title of {} does not need to be changed'.format(path))
    shutil.rmtree(tdir)


if __name__ == '__main__':
    main(sys.argv[1:])

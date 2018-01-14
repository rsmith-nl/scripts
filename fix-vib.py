#!/usr/bin/env python3
# file: fix-vib.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2017-04-11 15:39:37 +0200
# Last modified: 2018-01-14 14:00:23 +0100
"""
Fix PDF file titles.

Decrypt safety data sheets and fix the title to match the filename.
This is done to make sure that the reader app on a tablet displays a sensible title.
"""

from collections import defaultdict
import logging
import os
import shutil
import subprocess as sp
import sys
import tempfile


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


def main(args):
    lvl = 'INFO'
    if args[0].startswith('-'):
        if args[0] in ('-v', '--verbose'):
            lvl = 'DEBUG'
        if args[0] in ('-h', '--help'):
            print('Usage: fix-vib.py [-v|--verbose|-h|--help] <pdf-files>')
            return
        del args[0]
    logging.basicConfig(level=lvl, format='%(levelname)s: %(message)s')
    if lvl == 'DEBUG':
        logging.info('using verbose logging')
    tdir = tempfile.mkdtemp()
    for path in args:
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
        newtitle = fn.replace('_', ' ')[:-4]
        if info['Title'] != newtitle:
            logging.info('{} needs its title changed'.format(path))
            args2 = ['exiftool', '-m', '-Title={}'.format(newtitle),
                     '-overwrite_original', path]
            rv = sp.run(args2, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            if rv.returncode != 0:
                es = 'could not change title of {}; exiftool returned {}'
                logging.error(es.format(path, rv.returncode))
            else:
                logging.debug('title of {} changed'.format(path))
    shutil.rmtree(tdir)


if __name__ == '__main__':
    main(sys.argv[1:])

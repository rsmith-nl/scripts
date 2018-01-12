# file: fix-vib.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2017-04-11 15:39:37 +0200
# Last modified: 2018-01-12 23:57:46 +0100
"""
Fix PDF file titles.

Decrypt safety data sheets and fix the title to match the filename.
This is done to make sure that the reader app on a tablet displays a sensible title.
"""

from collections import defaultdict
import os
import subprocess as sp
import sys
import tempfile
import shutil


def pdfinfo(path):
    args = ['pdfinfo', path]
    rv = sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL)
    dd = defaultdict(lambda: '')
    if rv.returncode != 0:
        return dd
    pairs = [ln.split(':', 1) for ln in rv.stdout.decode('utf-8').splitlines()]
    for k, v in pairs:
        dd[k] = v.strip()
    return dd


tdir = tempfile.mkdtemp()
for path in sys.argv[1:]:
    info = pdfinfo(path)
    fn = os.path.basename(path)
    if info['Encrypted'].startswith('yes'):
        print(path, 'is encrypted.')
        tmppath = tdir + os.sep + fn
        args = ['qpdf', '--decrypt', path, tmppath]
        rv = sp.run(args)
        if rv.returncode == 0:
            os.remove(path)
            shutil.copyfile(tmppath, path)
            os.remove(tmppath)
        else:
            print('Could not decrypt', path)
            continue
    newtitle = fn.replace('_', ' ')[:-4]
    if info['Title'] != newtitle:
        print(path, 'needs its title changed.')
        args2 = [
            'exiftool', '-m', '-Title={}'.format(newtitle), '-overwrite_original', path
        ]
        rv = sp.run(args2, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        if rv.returncode != 0:
            print('Could not change title of', path)
shutil.rmtree(tdir)

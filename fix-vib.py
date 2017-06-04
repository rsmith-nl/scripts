# file: fix-vib.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2017-04-11 15:39:37 +0200
# Last modified: 2017-06-04 13:24:34 +0200
"""
Fix PDF file titles.

Decrypt safety data sheets and fix the title to match the filename.
This is done to make sure that an e-reader displays a sensible title.
"""

import os
import subprocess
import sys
import tempfile
import shutil

tdir = tempfile.mkdtemp()
for path in sys.argv[1:]:
    fn = os.path.basename(path)
    tmppath = tdir + os.sep + fn
    args = ['qpdf', '--decrypt', path, tmppath]
    rv = subprocess.run(args)
    if rv.returncode != 0:
        print('Could not dercypt', path)
        continue
    os.remove(path)
    shutil.copyfile(tmppath, path)
    os.remove(tmppath)
    newtitle = fn.replace('_', ' ')[:-4]
    args2 = [
        'exiftool', '-Title={}'.format(newtitle), '-overwrite_original', path
    ]
    rv = subprocess.run(args2, stdout=subprocess.DEVNULL)
    if rv.returncode != 0:
        print('Could not change title of', path)
shutil.rmtree(tdir)

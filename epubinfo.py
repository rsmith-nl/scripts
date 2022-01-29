#!/usr/bin/env python
# file: epubinfo.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2021 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2021-03-07T12:02:26+0100
# Last modified: 2021-03-07T14:19:48+0100
"""Extract and print the metadata from an epub file."""

import os
import re
import sys
import zipfile

dcre = r"<dc:([^>\s]+)(?:\s*[^>]*>)(.*)</dc:\1>"

if len(sys.argv) < 2:
    print(__doc__)
    print(f"Usage: {os.path.basename(sys.argv[0])} file ...")
    sys.exit(0)
for fn in sys.argv[1:]:
    if not fn.lower().endswith("epub"):
        print(f"File {fn} is not an epub file; skipping.")
        continue
    print(f"File: {fn}")
    with zipfile.ZipFile(fn) as zf:
        opfnames = [nm for nm in zf.namelist() if "content.opf" in nm]
        if not opfnames:
            print(f"File {fn} has no metadata; skipping.")
            continue
        elif len(opfnames) > 1:
            print(f"More than one metadata file in {fn}!")
        for opf in opfnames:
            print(f"  metadata file: {opf}")
            opfdata = zf.read(opf).decode()
            for key, value in re.findall(dcre, opfdata):
                print(f"  {key}: {value}")

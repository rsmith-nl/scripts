#!/usr/bin/env python3
# file: req.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-08-17T23:42:00+0200
# Last modified: 2020-08-17T23:51:03+0200
"""Extract the requirements from wheel files."""

import sys
import zipfile as zf


def get_req(wheel):
    z = zf.ZipFile(wheel)
    name = [nm for nm in z.namelist() if nm.endswith("METADATA")][0]
    with z.open(name) as f:
        data = f.read().decode().splitlines()
    requirements = [ln.split(maxsplit=1)[1] for ln in data if ln.startswith('Requires-Dist:')]
    return requirements


for path in sys.argv[1:]:
    print(path)
    for dep in get_req(path):
        print("    ", dep)

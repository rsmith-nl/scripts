#!/usr/bin/env python3
# file: wheel-req.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2020-08-17T23:42:00+0200
# Last modified: 2022-02-05T20:19:53+0100
"""Extract the requirements from wheel files."""

import os
import sys
import zipfile as zf


def get_req(wheel):
    z = zf.ZipFile(wheel)
    name = [nm for nm in z.namelist() if nm.endswith("METADATA")][0]
    with z.open(name) as f:
        data = f.read().decode().splitlines()
    requirements = [
        ln.split(maxsplit=1)[1]
        for ln in data
        if ln.startswith("Requires-Dist:") and "extra ==" not in ln
    ]
    return requirements


if __name__ == "__main__":
    for path in sys.argv[1:]:
        print(path.rsplit(os.sep, maxsplit=1)[1])
        for dep in get_req(path):
            print("    ", dep)

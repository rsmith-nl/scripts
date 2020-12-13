#!/usr/bin/env python
# file: all-git.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2020-12-13T22:19:38+0100
# Last modified: 2020-12-13T22:46:40+0100
"""Report on all subdirectories that are managed by git."""

import os
import subprocess as sp

for root, dirs, files in os.walk("."):
    if ".git" in dirs:
        rp = os.getcwd()
        os.chdir(root)
        data = sp.run(
            ["git", "-P", "log", "-n", "1", "--pretty=%H %aI"],
            stdout=sp.PIPE,
            text=True
        ).stdout[:-1]
        os.chdir(rp)
        print(data, root[2:])

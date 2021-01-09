#!/usr/bin/env python
# file: all-git.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2020-12-13T22:19:38+0100
# Last modified: 2021-01-09T14:16:44+0100
"""Report on all subdirectories that are managed by git."""

import os
import subprocess as sp
import time

results = []
for root, dirs, files in os.walk("."):
    if ".git" in dirs:
        rp = os.getcwd()
        os.chdir(root)
        data = sp.run(
            ["git", "-P", "log", "-n", "1", "--pretty=%H %at"],
            stdout=sp.PIPE,
            text=True
        ).stdout[:-1]
        commit_id, seconds = data.split()
        seconds = int(seconds)
        results.append((commit_id, seconds, root[2:]))
        os.chdir(rp)
# Move the most recently changed to the end of the list.
results.sort(key=lambda x: x[1])
for commit_id, seconds, path in results:
    print(commit_id, time.strftime("%Y-%m-%dT%H:%M%:%S%z", time.localtime(seconds)), path)

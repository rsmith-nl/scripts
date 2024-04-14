#!/usr/bin/env python
# file: all-git.py
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2020-12-13T22:19:38+0100
# Last modified: 2022-02-12T12:58:05+0100
"""Report on all subdirectories that are managed by git."""

import os
import sys
import subprocess as sp

if __name__ == "__main__":
    results = []
    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            rp = os.getcwd()
            os.chdir(root)
            data = sp.run(
                ["git", "-P", "log", "-n", "1", "--pretty=%h|%aI"],
                stdout=sp.PIPE,
                stderr=sp.DEVNULL,
                text=True,
            ).stdout[:-1]
            try:
                commit_id, date = data.split("|")
                results.append((commit_id, date, root))
            except ValueError:
                print(f"ERROR in ‘{root}’, skipping.", file=sys.stderr)
            os.chdir(rp)
    # Move the most recently changed to the end of the list.
    results.sort(key=lambda x: x[1])
    sep = " | "
    for commit_id, date, path in results:
        print(f"{commit_id}{sep}{date}{sep}{path}")
